#!/usr/bin/env python3
from gpiozero import PWMOutputDevice, DigitalOutputDevice, AngularServo
import serial
import threading
import time
import sys

# ================================================================
# 설정값
# ================================================================
SERIAL_PORT       = '/dev/serial0'
BAUDRATE          = 115200

TRIGGER_DIST      = 60       # 트리거 거리 (cm)
RESET_DIST        = 62       # 재감지 거리 (히스테리시스)
DETECT_COUNT      = 3        # 연속 감지 횟수
COOLDOWN          = 1.0      # 재트리거 최소 간격 (초)

ACTUATOR_TIME     = 0.5      # 액추에이터 3cm 전진 시간 ★실측 보정★
WORM_SPEED        = 0.30     # 웜기어 PWM duty (1cm/s ★실측 보정★)

STEPS_90          = 1600     # 스텝모터 90도 스텝 수 ★드라이버 설정 확인★
STEP_DELAY        = 0.001    # 스텝 펄스 간격 (초)
DIR_DELAY         = 0.02     # DIR 신호 안정화 대기

SERVO_GPIO        = 22
SERVO_SPEED       = 2.0      # 서보 속도 (deg/s)
SERVO_RUN_TIME    = 2.0      # 서보 구동 시간 (초) — +/- 공통
SERVO_TICK        = 0.05     # 서보 업데이트 주기 (초)

WORM_RUN_TIME     = 5.0      # 6번 스텝에서 웜기어 구동 시간 (초)

# ================================================================
# TFmini UART  (GPIO 14/15 — /dev/serial0)
# ================================================================
ser  = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
_buf = bytearray()

def read_distance():
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
# 리니어 액추에이터  BTS#1 — GPIO 18/19/23/24
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
# 웜기어 #1, #2  BTS#2 — GPIO 12/13/5/6 | BTS#3 — GPIO 20/21/16/26
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
# 스텝모터  GPIO 17(PUL) / 27(DIR)
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
# 서보모터  GPIO 22  (시간 기반 속도 제어)
# ================================================================
_servo       = AngularServo(
    SERVO_GPIO,
    min_angle=-90, max_angle=90,
    min_pulse_width=0.5 / 1000,
    max_pulse_width=2.5 / 1000,
)
_servo_angle = 0.0

def servo_run(duration, direction=1):
    """
    direction=+1 : + 방향
    direction=-1 : - 방향
    duration(초) 동안 SERVO_SPEED(deg/s)로 회전 후 정지
    """
    global _servo_angle
    step_per_tick = SERVO_SPEED * SERVO_TICK * direction
    elapsed = 0.0
    while elapsed < duration:
        next_angle = _servo_angle + step_per_tick
        next_angle = max(-90.0, min(90.0, next_angle))  # 범위 제한
        _servo_angle = next_angle
        _servo.angle = _servo_angle
        time.sleep(SERVO_TICK)
        elapsed += SERVO_TICK
    print(f"     서보 정지 각도: {_servo_angle:.1f}°")

# ================================================================
# 트리거 시퀀스 (별도 스레드 — 순차 실행)
# ================================================================
_seq_running = threading.Event()

def _trigger_sequence():
    print("[트리거 발생]")

    # [3] 웜기어 정지 (트리거 감지 시)
    worm_stop()
    print("  [3] 웜기어 정지")

    # [4] 스텝모터 +90° — 완료까지 블로킹
    print("  [4] 스텝모터 +90° 회전 중...")
    rotate_plus_90()
    print("  [4] 스텝모터 완료")

    # [5] 서보 + 방향 2초 구동 후 정지
    print(f"  [5] 서보 +방향 {SERVO_RUN_TIME}초 구동...")
    servo_run(SERVO_RUN_TIME, direction=+1)
    print("  [5] 서보 정지")

    # [6] 웜기어 5초 구동 후 정지
    print(f"  [6] 웜기어 {WORM_RUN_TIME}초 구동...")
    worm_forward()
    time.sleep(WORM_RUN_TIME)
    worm_stop()
    print("  [6] 웜기어 정지")

    # [7] 서보 - 방향 2초 구동
    print(f"  [7] 서보 -방향 {SERVO_RUN_TIME}초 구동...")
    servo_run(SERVO_RUN_TIME, direction=-1)
    print("  [7] 서보 정지")

    # [8] 웜기어 재시작 (계속 구동)
    worm_forward()
    print("  [8] 웜기어 재시작 (계속 구동)")

    print("[시퀀스 완료]")
    _seq_running.clear()

# ================================================================
# 메인
# ================================================================
def main():
    L_EN.on();  R_EN.on()
    L_EN2.on(); R_EN2.on()
    L_EN3.on(); R_EN3.on()

    # [0] TFmini UART 연결
    print("TFmini UART 연결 완료 (/dev/serial0)")

    # [1] 리니어 액추에이터 3cm 전진
    print("리니어 액추에이터 3cm 전진...")
    actuator_extend()
    time.sleep(ACTUATOR_TIME)
    actuator_stop()
    print("리니어 완료")

    # [2] 웜기어 시작 (트리거 전까지 계속)
    worm_forward()
    print("웜기어 구동 시작 (1cm/s)")
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
                f"거리: {dist:4d} cm  "
                f"서보: {_servo_angle:+6.1f}°  "
            )
            sys.stdout.flush()

            now = time.time()

            if not triggered:
                # [3] 60cm 이하 3회 연속 → 트리거
                detect_hits = (detect_hits + 1) if dist <= TRIGGER_DIST else 0

                if detect_hits >= DETECT_COUNT and (now - last_trig) >= COOLDOWN:
                    triggered   = True
                    last_trig   = now
                    detect_hits = 0
                    _seq_running.set()
                    threading.Thread(target=_trigger_sequence, daemon=True).start()
            else:
                # [9] 시퀀스 완료 + 거리 ≥ 62cm → 재감지 허용
                if not _seq_running.is_set() and dist >= RESET_DIST:
                    triggered   = False
                    detect_hits = 0
                    print("[재감지 가능]")

        time.sleep(0.01)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("종료 중...")
    finally:
        actuator_stop()
        worm_stop()
        _servo.angle = 0

        L_EN.off();  R_EN.off()
        L_EN2.off(); R_EN2.off()
        L_EN3.off(); R_EN3.off()
        PUL.on()

        if ser.is_open:
            ser.close()
        print("시스템 종료 완료")
