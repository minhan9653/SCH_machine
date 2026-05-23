import lgpio
import time

SERVO_PIN = 22
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, SERVO_PIN)

print("중립 (1500us)")
lgpio.tx_servo(h, SERVO_PIN, 1500)
time.sleep(1)

print("정방향 최대 (2500us)")
lgpio.tx_servo(h, SERVO_PIN, 2500)
time.sleep(1)

print("역방향 최대 (500us)")
lgpio.tx_servo(h, SERVO_PIN, 500)
time.sleep(1)

print("중립 복귀")
lgpio.tx_servo(h, SERVO_PIN, 1500)
time.sleep(1)

lgpio.tx_servo(h, SERVO_PIN, 0)
lgpio.gpiochip_close(h)
print("완료")
