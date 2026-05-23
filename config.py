"""TFmini Machine Flow 전용 설정 파일.

실제 하드웨어 배선, 속도, 거리 기준, 보정 시간은 이 파일에서 수정합니다.
기존 루트 프로젝트의 config.py 값은 참고만 했고, 이 새 프로젝트는 이 파일을 사용합니다.
"""

# TFmini UART 설정입니다. Raspberry Pi 기본 UART는 보통 /dev/serial0을 사용합니다.
TFMINI_PORT = "/dev/serial0"
TFMINI_BAUDRATE = 115200
SERIAL_TIMEOUT = 0.1

# 기존 이름을 기대하는 코드와 맞추기 위한 별칭입니다.
SERIAL_PORT = TFMINI_PORT
BAUDRATE = TFMINI_BAUDRATE

# 거리 감지 기준입니다.
# TRIGGER_DIST 이하가 DETECT_COUNT번 연속 들어오면 Flow가 1회 실행됩니다.
TRIGGER_DIST = 60

# Flow 실행 후에는 RESET_DIST 이상 멀어져야 다시 감지할 수 있습니다.
RESET_DIST = 62
DETECT_COUNT = 3
COOLDOWN_SECONDS = 1.0

# 리니어 액추에이터 설정입니다.
ACTUATOR_SPEED = 0.6
# TODO: 실제 장비에서 약 3cm 전진하는 시간을 측정해서 이 값을 보정하세요.
ACTUATOR_TIME = 1.0
ACTUATOR_PINS = {
    "rpwm": 18,
    "lpwm": 19,
    "l_en": 23,
    "r_en": 24,
}

# 웜기어 모터 설정입니다. WORM_SPEED는 기존 config.py 값을 그대로 반영했습니다.
WORM_SPEED = 0.30
WORM_RUN_SECONDS = 5.0
WORM_MOTOR_PINS = [
    {"rpwm": 12, "lpwm": 13, "l_en": 5, "r_en": 6},
    {"rpwm": 20, "lpwm": 21, "l_en": 16, "r_en": 26},
]

# 스텝모터 설정입니다. PUL/DIR 방식 드라이버 기준입니다.
STEPS_90 = 1600
STEP_DELAY = 0.001
DIR_DELAY = 0.02
STEPPER_PINS = {
    "pul": 17,
    "dir": 27,
}

# 서보모터 설정입니다.
# 요구사항 기준: 초당 2도, 2초 동안 이동하므로 총 4도 이동합니다.
SERVO_GPIO = 22
SERVO_SPEED = 2.0
SERVO_DEG_PER_SEC = 2.0
SERVO_MOVE_SECONDS = 2.0
SERVO_MOVE_DEG = SERVO_DEG_PER_SEC * SERVO_MOVE_SECONDS
SERVO_HOME_ANGLE = 0.0
SERVO_MIN_ANGLE = -90.0
SERVO_MAX_ANGLE = 90.0
# TODO: 사용하는 서보 사양에 맞게 펄스폭과 안전 각도 범위를 보정하세요.
SERVO_MIN_PULSE_WIDTH = 0.5 / 1000
SERVO_MAX_PULSE_WIDTH = 2.5 / 1000

# 메인 루프와 거리 로그 출력 주기입니다.
LOOP_SLEEP_SECONDS = 0.01
DISTANCE_LOG_INTERVAL_SECONDS = 0.2
