from gpiozero import DigitalOutputDevice
from time import sleep

# 새 연결 기준
# PUL+ = 3.3V
# PUL- = GPIO17, 물리핀 11
# DIR+ = 3.3V
# DIR- = GPIO27, 물리핀 13

PUL = DigitalOutputDevice(17, initial_value=True)
DIR = DigitalOutputDevice(27, initial_value=True)

def step_motor(steps, delay=0.00003):
    for _ in range(steps):
        PUL.off()
        sleep(delay)
        PUL.on()
        sleep(delay)

try:
    print("정방향 회전")
    DIR.on()
    sleep(0.5)
    step_motor(1000)

    sleep(1)

    print("역방향 회전")
    DIR.off()
    sleep(0.5)
    step_motor(1000)

    print("완료")

except KeyboardInterrupt:
    print("중지")

finally:
    PUL.on()