from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep
import serial
import time
import sys

# ==============================
# 0. TFmini 거리센서
# ==============================
ser = serial.Serial('/dev/serial0', 115200, timeout=1)

def read_distance():
    data = ser.read(9)

    if len(data) == 9:
        if data[0] == 0x59 and data[1] == 0x59:
            distance = data[2] + data[3] * 256
            strength = data[4] + data[5] * 256
            return distance, strength
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

def actuator_stop():
    RPWM.value = 0
    LPWM.value = 0

def extend(speed=0.6):
    LPWM.value = 0
    RPWM.value = speed

def retract(speed=0.6):
    RPWM.value = 0
    LPWM.value = speed


# ==============================
# 2. 웜기어 #1
# ==============================
RPWM2 = PWMOutputDevice(12, frequency=1000)
LPWM2 = PWMOutputDevice(13, frequency=1000)

L_EN2 = DigitalOutputDevice(5)
R_EN2 = DigitalOutputDevice(6)

def enable_driver2():
    L_EN2.on()
    R_EN2.on()

def worm_stop():
    RPWM2.value = 0
    LPWM2.value = 0

def worm_forward(speed=0.6):
    LPWM2.value = 0
    RPWM2.value = speed

def worm_reverse(speed=0.6):
    RPWM2.value = 0
    LPWM2.value = speed


# ==============================
# 3. 웜기어 #2
# ==============================
RPWM3 = PWMOutputDevice(20, frequency=1000)
LPWM3 = PWMOutputDevice(21, frequency=1000)

L_EN3 = DigitalOutputDevice(16)
R_EN3 = DigitalOutputDevice(26)

def enable_driver3():
    L_EN3.on()
    R_EN3.on()

def worm2_stop():
    RPWM3.value = 0
    LPWM3.value = 0

def worm2_forward(speed=0.6):
    LPWM3.value = 0
    RPWM3.value = speed

def worm2_reverse(speed=0.6):
    RPWM3.value = 0
    LPWM3.value = speed


# ==============================
# 4. 메인 (실시간 거리 출력)
# ==============================
try:
    enable_driver()
    enable_driver2()
    enable_driver3()

    extend(0.6)
    worm_forward(0.6)
    worm2_forward(0.6)

    while True:
        distance, strength = read_distance()

        if distance is not None:
            # ⭐ 실시간 표시
            sys.stdout.write(f"\r거리: {distance:4d} cm | 신호: {strength:5d}")
            sys.stdout.flush()

        time.sleep(0.02)

finally:
    actuator_stop()
    worm_stop()
    worm2_stop()

    L_EN.off()
    R_EN.off()
    L_EN2.off()
    R_EN2.off()
    L_EN3.off()
    R_EN3.off()