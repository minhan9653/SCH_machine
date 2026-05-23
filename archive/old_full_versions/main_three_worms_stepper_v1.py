from gpiozero import PWMOutputDevice, DigitalOutputDevice
import serial
import time
import sys

# ==============================
# 0. 설정값
# ==============================
SERIAL_PORT = '/dev/serial0'
BAUDRATE = 115200

TRIGGER_DIST = 15
RESET_DIST = 20
DETECT_COUNT = 3
COOLDOWN = 1.0

ACTUATOR_SET_TIME = 0.5
WORM_SPEED = 0.3

# 스텝모터
STEPS_90 = 1600
STEP_DELAY = 0.001
DIR_SETUP_DELAY = 0.02

# ==============================
# 1. TFmini
# ==============================
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
buffer = bytearray()

def read_distance():
    global buffer
    while ser.in_waiting:
        buffer.extend(ser.read(ser.in_waiting))

        while len(buffer) >= 9:
            if buffer[0] == 0x59 and buffer[1] == 0x59:
                frame = buffer[:9]
                checksum = sum(frame[:8]) & 0xFF

                if checksum == frame[8]:
                    dist = frame[2] + (frame[3] << 8)
                    buffer = buffer[9:]
                    return dist
                else:
                    buffer.pop(0)
            else:
                buffer.pop(0)
    return None


# ==============================
# 2. 리니어 액추에이터
# ==============================
RPWM = PWMOutputDevice(18)
LPWM = PWMOutputDevice(19)
L_EN = DigitalOutputDevice(23)
R_EN = DigitalOutputDevice(24)

def actuator_extend():
    LPWM.value = 0
    RPWM.value = 0.6

def actuator_stop():
    RPWM.value = 0
    LPWM.value = 0


# ==============================
# 3. 웜기어 3개 (BTS 3개)
# ==============================

# #1
RPWM2 = PWMOutputDevice(12)
LPWM2 = PWMOutputDevice(13)
L_EN2 = DigitalOutputDevice(5)
R_EN2 = DigitalOutputDevice(6)

# #2
RPWM3 = PWMOutputDevice(20)
LPWM3 = PWMOutputDevice(21)
L_EN3 = DigitalOutputDevice(16)
R_EN3 = DigitalOutputDevice(26)

# #3
RPWM4 = PWMOutputDevice(25)
LPWM4 = PWMOutputDevice(8)
L_EN4 = DigitalOutputDevice(7)
R_EN4 = DigitalOutputDevice(1)

def worm_forward(speed=WORM_SPEED):
    # 3개 동시
    LPWM2.value = 0; RPWM2.value = speed
    LPWM3.value = 0; RPWM3.value = speed
    LPWM4.value = 0; RPWM4.value = speed

def worm_stop():
    RPWM2.value = LPWM2.value = 0
    RPWM3.value = LPWM3.value = 0
    RPWM4.value = LPWM4.value = 0


# ==============================
# 4. 스텝모터
# ==============================
PUL = DigitalOutputDevice(17, initial_value=True)
DIR = DigitalOutputDevice(27, initial_value=True)

def step_motor(steps):
    for _ in range(steps):
        PUL.off()
        time.sleep(STEP_DELAY)
        PUL.on()
        time.sleep(STEP_DELAY)

def rotate_plus_90():
    DIR.on()
    time.sleep(DIR_SETUP_DELAY)
    step_motor(STEPS_90)

def rotate_minus_90():
    DIR.off()
    time.sleep(DIR_SETUP_DELAY)
    step_motor(STEPS_90)


# ==============================
# 5. 메인
# ==============================
try:
    # 드라이버 ON
    L_EN.on(); R_EN.on()
    L_EN2.on(); R_EN2.on()
    L_EN3.on(); R_EN3.on()
    L_EN4.on(); R_EN4.on()

    # 3cm 세팅
    actuator_extend()
    time.sleep(ACTUATOR_SET_TIME)
    actuator_stop()

    # 웜기어 시작
    worm_forward()

    print("시스템 시작")

    triggered = False
    detect_hits = 0
    last_trigger_time = 0

    while True:
        dist = read_distance()

        if dist is not None:
            sys.stdout.write(f"\r거리: {dist:4d} cm ")
            sys.stdout.flush()

            now = time.time()

            if not triggered:
                if dist <= TRIGGER_DIST:
                    detect_hits += 1
                else:
                    detect_hits = 0

                if detect_hits >= DETECT_COUNT and (now - last_trigger_time) >= COOLDOWN:
                    triggered = True
                    last_trigger_time = now
                    detect_hits = 0

                    print("\n[트리거 발생]")

                    # 1. 웜기어 정지
                    worm_stop()

                    # 2. +90도
                    print("스텝 +90")
                    rotate_plus_90()

                    # 3. 웜기어 재시작
                    worm_forward()

                    # 4. 3초 후 -90도
                    time.sleep(3)
                    print("스텝 -90")
                    rotate_minus_90()

                    print("완료\n")

            else:
                if dist >= RESET_DIST:
                    triggered = False
                    detect_hits = 0
                    print("\n[재감지 가능]")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n종료")

finally:
    actuator_stop()
    worm_stop()

    L_EN.off(); R_EN.off()
    L_EN2.off(); R_EN2.off()
    L_EN3.off(); R_EN3.off()
    L_EN4.off(); R_EN4.off()

    PUL.on()

    if ser.is_open:
        ser.close()