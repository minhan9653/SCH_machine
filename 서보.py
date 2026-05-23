from gpiozero import AngularServo
from time import sleep, time

servo = AngularServo(
    22,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)

try:
    start_time = time()

    # 2초 동안만 천천히 회전
    while time() - start_time < 2:
        servo.angle += 1
        sleep(0.08)   # 클수록 느리게 움직임

except KeyboardInterrupt:
    print("종료")