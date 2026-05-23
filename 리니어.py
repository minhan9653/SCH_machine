from gpiozero import PWMOutputDevice, DigitalOutputDevice
import time

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

try:
    L_EN.on()
    R_EN.on()

    actuator_extend()

    print("리니어 액추에이터 계속 전진 중")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("정지")

finally:
    actuator_stop()
    L_EN.off()
    R_EN.off()
