"""SCH machine runtime settings.

이 파일은 핀 번호와 동작 기준값을 모아두는 설정 파일입니다.
하드웨어 배선이나 속도/거리 기준을 바꾸고 싶을 때는 먼저 여기부터 수정하세요.
"""

# TFmini 거리센서 UART 설정입니다.
# Raspberry Pi의 GPIO 14/15 UART를 쓰는 경우 보통 /dev/serial0을 사용합니다.
SERIAL_PORT = "/dev/serial0"
BAUDRATE = 115200

# 거리 감지 조건입니다.
# 거리값이 TRIGGER_DIST 이하로 DETECT_COUNT번 연속 들어오면 트리거가 발생합니다.
TRIGGER_DIST = 60

# 트리거 후에는 거리가 RESET_DIST 이상으로 멀어져야 다시 감지할 수 있습니다.
# TRIGGER_DIST보다 조금 크게 두면 거리값이 흔들릴 때 반복 트리거되는 것을 줄일 수 있습니다.
RESET_DIST = 62
DETECT_COUNT = 3

# 트리거가 너무 빠르게 반복되지 않도록 막는 최소 대기 시간입니다.
COOLDOWN = 1.0

# 시작 시 리니어 액추에이터를 전진시키는 시간과 속도입니다.
ACTUATOR_TIME = 0.5
ACTUATOR_SPEED = 0.6

# 웜기어 모터 PWM duty 값입니다. 0.0은 정지, 1.0은 최대 출력입니다.
WORM_SPEED = 0.30

# 스텝모터 설정입니다.
# STEPS_90은 현재 드라이버 세팅에서 90도에 해당하는 펄스 수입니다.
STEPS_90 = 1600
STEP_DELAY = 0.001
DIR_DELAY = 0.02

# 서보 설정입니다.
# SERVO_SPEED는 초당 이동 각도입니다. 2.0이면 45도까지 약 22.5초가 걸립니다.
SERVO_GPIO = 22
SERVO_SPEED = 2.0
SERVO_TARGET_PLUS = 45.0
SERVO_TARGET_HOME = 0.0
SERVO_REVERSE_DELAY = 8.0

# 리니어 액추에이터용 BTS 드라이버 핀입니다.
ACTUATOR_PINS = {
    "rpwm": 18,
    "lpwm": 19,
    "l_en": 23,
    "r_en": 24,
}

# 웜기어용 BTS 드라이버 핀 목록입니다.
# 모터를 3개로 늘리려면 아래 목록에 같은 형식의 dict를 하나 더 추가하면 됩니다.
WORM_MOTOR_PINS = [
    {"rpwm": 12, "lpwm": 13, "l_en": 5, "r_en": 6},
    {"rpwm": 20, "lpwm": 21, "l_en": 16, "r_en": 26},
]

# 스텝모터 드라이버 핀입니다.
# PUL은 펄스, DIR은 회전 방향 신호입니다.
STEPPER_PINS = {
    "pul": 17,
    "dir": 27,
}
