#!/usr/bin/env python3
"""
파이프라인 검사 로봇 — 메인 제어 프로그램
대상: Raspberry Pi 5 / gpiozero / TFmini UART
"""

from gpiozero import PWMOutputDevice, DigitalOutputDevice, AngularServo
import serial
import threading
import time
import sys

# ================================================================
# 0. 설정값
# ================================================================
SERIAL_PORT          = '/dev/serial0'
BAUDRATE             = 115200

TRIGGER_DIST         = 60        # 트리거 거리 (cm) — TOF <= 60cm
RESET_DIST           = 62        # 재감지 허용 거리 (히스테리시스 +2cm)
DETECT_COUNT         = 3         # 연속 감지 횟수
COOLDOWN             = 1.0       # 재트리거 최소 간격 (초)

ACTUATOR_TIME        = 0.5       # 리니어 액추에이터 3cm 전진 시간 ★실측 보정★
WORM_SPEED           = 0.30      # 웜기어 PWM duty  (1cm/s 되도록 ★실측 보정★)

STEPS_90             = 1600      # 스텝모터 90도 스텝 수
STEP_DELAY           = 0.001     # 스텝 펄스 간격 (초)
DIR_DELAY            = 0.02      # DIR 신호 설정 후 안정화 대기

SERVO_GPIO           = 22        # 서보 PWM 핀 (표준 PWM 서보 기준)
SERVO_SPEED          = 2.0       # 서보 속도 (deg/sec)
SERVO_TARGET_PLUS    =  45.0     # 트리거 시 목표 각도 (+45°)
SERVO_TARGET_HOME    =   0.0     # 복귀 목표 각도 (절대 0°)
SERVO_REVERSE_DELAY  = 8         # 서보 복귀까지 대기 (초)

# ================================================================
# 1. TFmini UART 초기화  (GPIO 14/15 — /dev/serial0)
# ================================================================
ser  = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
_buf = bytearray()

def read_distance():
    """TFmini 프레임 파싱 → 거리(cm) 반환, 없으면 None"""
    global _buf
    if ser.in_waiting:
        _buf.extend(ser.read(ser.in_waiting))
    while len(_buf) >= 9:
        if _buf[0] == 0x59 and _buf[1] == 0x59:
            frame = _buf[:9]
            if (sum(frame[:8]) & 0xFF) == frame[8]:
                dist = frame[2] + (frame[3] << 8)
                del _buf[:9]
                return dist
        del _buf[:1]
    return None

# ================================================================
# 2. 리니어 액추에이터  BTS#1 — GPIO 18/19/23/24
# ================================================================
RPWM = PWMOutputDevice(18)
LPWM = PWMOutputDevice(19)
L_EN = DigitalOutputDevice(23)
R_EN = DigitalOutputDevice(24)

def actuator_extend():
    LPWM.value = 0.0
    RPWM.value = 0.6

def actuator_stop():
    RPWM.value = 0.0
    LPWM.value = 0.0

# ================================================================
# 3. 웜기어 #1, #2  BTS#2 — GPIO 12/13/5/6  |  BTS#3 — GPIO 20/21/16/26
# ================================================================
RPWM2 = PWMOutputDevice(12);  LPWM2 = PWMOutputDevice(13)
L_EN2 = DigitalOutputDevice(5);   R_EN2 = DigitalOutputDevice(6)

RPWM3 = PWMOutputDevice(20);  LPWM3 = PWMOutputDevice(21)
L_EN3 = DigitalOutputDevice(16);  R_EN3 = DigitalOutputDevice(26)

def worm_forward(speed=WORM_SPEED):
    LPWM2.value = 0.0;  RPWM2.value = speed
    LPWM3.value = 0.0;  RPWM3.value = speed

def worm_stop():
    RPWM2.value = LPWM2.value = 0.0
    RPWM3.value = LPWM3.value = 0.0

# ================================================================
# 4. 스텝모터  GPIO 17(PUL) / 27(DIR)
# ================================================================
PUL = DigitalOutputDevice(17, initial_value=True)
DIR = DigitalOutputDevice(27, initial_value=True)

def _step(steps):
    for _ in range(steps):
        PUL.off(); time.sleep(STEP_DELAY)
        PUL.on();  time.sleep(STEP_DELAY)

def rotate_plus_90():
    DIR.on()
    time.sleep(DIR_DELAY)
    _step(STEPS_90)

# ================================================================
# 5. 서보모터  GPIO 22  (표준 PWM 서보 — 2deg/sec 속도 제어)
#    ※ LX-224HV 버스 서보 사용 시 → 시리얼 패킷 방식으로 교체 필요
# ================================================================
class ServoController:
    TICK = 0.05  # 50ms 업데이트 주기

    def __init__(self, gpio, speed=2.0):
        self._servo = AngularServo(
            gpio,
            min_angle=-90, max_angle=90,
            min_pulse_width=0.5 / 1000,
            max_pulse_width=2.5 / 1000,
        )
        self.speed   = speed
        self._angle  = 0.0
        self._target = 0.0
        self._lock   = threading.Lock()
        self._stop   = threading.Event()
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        step_max = self.speed * self.TICK   # deg / tick
        while not self._stop.is_set():
            with self._lock:
                cur = self._angle
                tgt = self._target
            diff = tgt - cur
            if abs(diff) >= 0.05:
                step = min(abs(diff), step_max) * (1 if diff > 0 else -1)
                new  = cur + step
                with self._lock:
                    self._servo.angle = new
                    self._angle = new
            time.sleep(self.TICK)

    def move_to(self, target):
        with self._lock:
            self._target = float(target)

    @property
    def angle(self):
        with self._lock:
            return self._angle

    def close(self):
        self._stop.set()
        time.sleep(0.1)
        self._servo.angle = 0

servo_ctrl = ServoController(SERVO_GPIO, SERVO_SPEED)

# ================================================================
# 6. 트리거 시퀀스 (별도 스레드로 실행)
# ================================================================
trigger_event = threading.Event()   # 시퀀스 진행 중 플래그

def _trigger_sequence():
    print("\n[트리거 발생]")

    # ① 웜기어 정지
    worm_stop()
    print("  ① 웜기어 정지")

    # ② 스텝모터 +90도 (동기, 완료까지 대기)
    print("  ② 스텝모터 +90° 회전 중...")
    rotate_plus_90()
    print("  ② 스텝모터 완료")

    # ③ 서보 +45도 이동 시작 (2deg/s 비동기)
    servo_ctrl.move_to(SERVO_TARGET_PLUS)
    print(f"  ③ 서보 → +{SERVO_TARGET_PLUS}° 이동 시작 ({SERVO_SPEED}°/s)")

    # ④ 웜기어 재시작
    worm_forward()
    print("  ④ 웜기어 재시작")

    # ⑤ 8초 후 서보 복귀
    print(f"  ⑤ {SERVO_REVERSE_DELAY}초 대기 후 서보 복귀...")
    time.sleep(SERVO_REVERSE_DELAY)
    servo_ctrl.move_to(SERVO_TARGET_HOME)
    print(f"  ⑤ 서보 → {SERVO_TARGET_HOME}° 복귀 시작")

    print("[시퀀스 완료]\n")
    trigger_event.clear()

# ================================================================
# 7. 메인 루프
# ================================================================
def main():
    # --- EN 핀 활성화 ---
    L_EN.on();  R_EN.on()
    L_EN2.on(); R_EN2.on()
    L_EN3.on(); R_EN3.on()

    # ── [조건 0] TFmini UART 연결 확인 ──
    print("TFmini UART 연결 완료  (/dev/serial0)")

    # ── [조건 2] 리니어 액추에이터 3cm 전진 ──
    print("리니어 액추에이터 3cm 전진...")
    actuator_extend()
    time.sleep(ACTUATOR_TIME)
    actuator_stop()
    print("리니어 완료")

    # ── [조건 1 / 2-1] 웜기어 시작 (트리거 전까지 계속) ──
    worm_forward()
    print("웜기어 구동 시작  (1cm/s)")
    print("=" * 45)
    print("거리 감지 중...  Ctrl+C = 종료")
    print("=" * 45)

    triggered   = False
    detect_hits = 0
    last_trig   = 0.0

    while True:
        dist = read_distance()

        if dist is not None:
            sys.stdout.write(
                f"\r거리: {dist:4d} cm  "
                f"서보: {servo_ctrl.angle:+6.1f}°  "
            )
            sys.stdout.flush()

            now = time.time()

            if not triggered:
                # 연속 감지 누적 (3. 트리거 조건)
                detect_hits = (detect_hits + 1) if dist <= TRIGGER_DIST else 0

                if detect_hits >= DETECT_COUNT and (now - last_trig) >= COOLDOWN:
                    triggered   = True
                    last_trig   = now
                    detect_hits = 0
                    trigger_event.set()
                    threading.Thread(target=_trigger_sequence, daemon=True).start()
            else:
                # 5. 시퀀스 완료 + 거리 >= 60cm → 재감지 허용
                if not trigger_event.is_set() and dist >= RESET_DIST:
                    triggered   = False
                    detect_hits = 0
                    print("\n[재감지 가능]")

        time.sleep(0.01)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n종료 중...")
    finally:
        actuator_stop()
        worm_stop()
        servo_ctrl.close()

        L_EN.off();  R_EN.off()
        L_EN2.off(); R_EN2.off()
        L_EN3.off(); R_EN3.off()
        PUL.on()

        if ser.is_open:
            ser.close()
        print("시스템 종료 완료")
