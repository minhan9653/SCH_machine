from gpiozero import PWMOutputDevice, DigitalOutputDevice
import serial
import time
import sys

# ==============================
# 0. TFmini (안정 버전)
# ==============================
ser = serial.Serial('/dev/serial0', 115200, timeout=0.1)

buffer = bytearray()

def read_tfmini():
    global buffer

    while ser.in_waiting:
        buffer.append(ser.read(1)[0])

        # 최소 9바이트 확보
        if len(buffer) >= 9:
            # 헤더 확인
            if buffer[0] == 0x59 and buffer[1] == 0x59:
                data = buffer[:9]
                buffer = buffer[9:]  # 사용한 데이터 제거

                distance = data[2] + data[3] * 256
                strength = data[4] + data[5] * 256

                return distance, strength
            else:
                # 헤더 아니면 한 칸 밀기
                buffer.pop(0)

    return None, None


# ==============================
# 1. 액추에이터
# ==============================
RPWM = PWMOutputDevice(18, frequency=1000)
LPWM = PWMOutputDevice(19, frequency=1000)
L_EN = DigitalOutputDevice(23)
R_EN = DigitalOutputDevice(24)

def enable_driver():
    L_EN.on()
    R_EN.on()

def extend(speed=0.6):
    LPWM.value = 0
    RPWM.value = speed

def actuator_stop():
    RPWM.value = 0
    LPWM.value = 0


# ==============================
# 2. 웜기어
# ==============================
RPWM2 = PWMOutputDevice(12, frequency=1000)
LPWM2 = PWMOutputDevice(13, frequency=1000)
L_EN2 = DigitalOutputDevice(5)
R_EN2 = DigitalOutputDevice(6)

def enable_driver2():
    L_EN2.on()
    R_EN2.on()

def worm_forward(speed=0.6):
    LPWM2.value = 0
    RPWM2.value = speed

def worm_stop():
    RPWM2.value = 0
    LPWM2.value = 0


# ==============================
# 3. 메인
# ==============================
try:
    enable_driver()
    enable_driver2()

    extend(0.6)
    worm_forward(0.6)

    print("모터 + 거리센서 시작")

    while True:
        dist, strength = read_tfmini()

        if dist is not None:
            sys.stdout.write(f"\r거리: {dist:4d} cm | 신호: {strength:5d}   ")
        else:
            sys.stdout.write("\r센서 데이터 없음...   ")

        sys.stdout.flush()
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n종료")

finally:
    actuator_stop()
    worm_stop()

    L_EN.off()
    R_EN.off()
    L_EN2.off()
    R_EN2.off()