from gpiozero import PWMOutputDevice, DigitalOutputDevice
import time

WORM_SPEED = 1

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

def worm_forward(speed=WORM_SPEED):
    LPWM2.value = 0
    RPWM2.value = speed

    LPWM3.value = 0
    RPWM3.value = speed

def worm_stop():
    RPWM2.value = 0
    LPWM2.value = 0

    RPWM3.value = 0
    LPWM3.value = 0

try:
    L_EN2.on()
    R_EN2.on()

    L_EN3.on()
    R_EN3.on()

    worm_forward()
    print("1번, 2번 웜기어 회전 시작")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("정지")

finally:
    worm_stop()

    L_EN2.off()
    R_EN2.off()

    L_EN3.off()
    R_EN3.off()
