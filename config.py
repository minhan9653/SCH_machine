"""TFmini Machine Flow 전용 설정 파일.

실제 하드웨어 배선, 속도, 거리 기준, 보정 시간은 이 파일에서 수정합니다.
기존 루트 프로젝트의 config.py 값은 참고만 했고, 이 새 프로젝트는 이 파일을 사용합니다.
"""

# TFMINI_PORT:
# TFmini 거리센서가 연결된 UART 장치 경로입니다.
# Raspberry Pi의 GPIO 14/15 기본 UART를 쓰는 경우 보통 "/dev/serial0"입니다.
# 센서가 USB-UART 어댑터에 연결되어 있다면 "/dev/ttyUSB0"처럼 달라질 수 있습니다.
TFMINI_PORT = "/dev/serial0"

# TFMINI_BAUDRATE:
# TFmini와 통신하는 속도입니다.
# TFmini 기본 baudrate가 115200인 경우가 많으므로 기존 설정값을 그대로 사용합니다.
# 센서 설정과 이 값이 다르면 거리값이 정상적으로 읽히지 않습니다.
TFMINI_BAUDRATE = 115200

# SERIAL_TIMEOUT:
# 시리얼 read가 데이터를 기다리는 최대 시간입니다.
# 작게 하면 루프 반응은 빨라지지만 데이터가 늦게 들어올 때 None이 자주 나올 수 있습니다.
# 크게 하면 읽기가 조금 더 기다리므로 반응이 둔해질 수 있습니다.
SERIAL_TIMEOUT = 0.1

# 기존 이름을 기대하는 코드와 맞추기 위한 별칭입니다.
SERIAL_PORT = TFMINI_PORT
BAUDRATE = TFMINI_BAUDRATE

# TRIGGER_DIST:
# 물체 감지로 판단할 거리 기준입니다. 단위는 cm입니다.
# 현재는 거리값이 60cm 이하이면 감지 후보가 됩니다.
# 값을 크게 하면 더 먼 거리에서도 감지되고, 작게 하면 더 가까이 와야 감지됩니다.
TRIGGER_DIST = 60

# RESET_DIST:
# Flow 실행 후 다시 감지 가능 상태로 돌아가기 위한 거리 기준입니다. 단위는 cm입니다.
# 현재 요구사항은 60cm 이상 멀어지면 다시 감지 가능 상태로 돌아가는 것입니다.
# main.py에서는 정확히 60cm 경계에 머무를 때 반복 실행되지 않도록 TRIGGER_DIST보다 멀어진 값에서 재감지합니다.
# 센서값이 60cm 근처에서 흔들려 반복 실행된다면 이 값을 62처럼 조금 크게 올리세요.
RESET_DIST = 60

# DETECT_COUNT:
# TRIGGER_DIST 이하 거리값이 몇 번 연속 들어와야 진짜 감지로 볼지 정합니다.
# 값을 크게 하면 오감지가 줄어들지만 반응이 느려집니다.
# 값을 작게 하면 빠르게 반응하지만 순간 노이즈에도 동작할 수 있습니다.
DETECT_COUNT = 3

# COOLDOWN_SECONDS:
# 트리거가 너무 빠르게 반복되지 않도록 둔 최소 대기 시간입니다.
# 현재 재감지는 RESET_DIST 조건이 핵심이고, 이 값은 추가 안전장치 역할입니다.
COOLDOWN_SECONDS = 1.0

# ACTUATOR_SPEED:
# 리니어 액추에이터 전진 PWM duty 값입니다. 0.0은 정지, 1.0은 최대 출력입니다.
# 값을 크게 하면 더 강하고 빠르게 움직일 수 있지만 전류와 충격이 커질 수 있습니다.
# 값을 작게 하면 천천히 움직이지만 힘이 부족할 수 있습니다.
ACTUATOR_SPEED = 0.6

# ACTUATOR_TIME:
# 프로그램 시작 시 액추에이터를 전진시키는 시간입니다. 단위는 초입니다.
# 요구사항의 "약 3cm 전진"은 이 시간과 ACTUATOR_SPEED 조합으로 맞춥니다.
# 값을 크게 하면 더 많이 전진하고, 작게 하면 덜 전진합니다.
# TODO: 실제 장비에서 약 3cm 전진하는 시간을 측정해서 이 값을 보정하세요.
ACTUATOR_TIME = 1.0

# ACTUATOR_PINS:
# 리니어 액추에이터용 BTS 드라이버 GPIO 핀입니다.
# rpwm/lpwm은 방향별 PWM 출력, l_en/r_en은 드라이버 enable 핀입니다.
# 배선이 바뀐 경우에만 수정하세요. 잘못 바꾸면 모터가 안 돌거나 반대 방향으로 돌 수 있습니다.
ACTUATOR_PINS = {
    "rpwm": 18,
    "lpwm": 19,
    "l_en": 23,
    "r_en": 24,
}

# WORM_SPEED:
# 웜기어 모터 PWM duty 값입니다. 0.0은 정지, 1.0은 최대 출력입니다.
# 기존 config.py의 0.30 값을 그대로 반영했습니다.
# 값을 크게 하면 웜기어가 더 빠르게 돌고, 작게 하면 느리게 돕니다.
# 실제 부하에서 갑자기 크게 올리면 기구 충격이나 전류 증가가 생길 수 있습니다.
WORM_SPEED = 0.30

# WORM_RUN_SECONDS:
# Flow 중간 단계에서 웜기어 모터를 다시 동작시키는 시간입니다. 단위는 초입니다.
# 요구사항 기준으로 5초 동안 동작 후 정지합니다.
# 값을 크게 하면 중간 구동 시간이 길어지고, 작게 하면 짧아집니다.
WORM_RUN_SECONDS = 5.0

# WORM_MOTOR_PINS:
# 웜기어 모터용 BTS 드라이버 GPIO 핀 목록입니다.
# dict 하나가 모터 1개입니다. 현재는 2개 모터를 동시에 같은 속도로 제어합니다.
# rpwm/lpwm은 방향별 PWM 출력, l_en/r_en은 드라이버 enable 핀입니다.
WORM_MOTOR_PINS = [
    {"rpwm": 12, "lpwm": 13, "l_en": 5, "r_en": 6},
    {"rpwm": 20, "lpwm": 21, "l_en": 16, "r_en": 26},
]

# STEPS_90:
# 스텝모터가 +90도 회전하는 데 필요한 펄스 수입니다.
# 드라이버 마이크로스텝 설정, 모터 스텝각, 기어비에 따라 달라집니다.
# 값을 크게 하면 90도보다 더 많이 돌고, 작게 하면 덜 돕니다.
# TODO: 실제 +90도 회전량을 보고 이 값을 보정하세요.
STEPS_90 = 1600

# STEP_DELAY:
# 스텝모터 PUL 신호를 LOW/HIGH로 토글할 때 각 상태를 유지하는 시간입니다. 단위는 초입니다.
# 이 값이 작을수록 펄스가 빨라져 모터가 빠르게 돕니다.
# 너무 작게 하면 모터가 탈조하거나 떨림, 소음, 회전 실패가 생길 수 있습니다.
# 이 값이 클수록 천천히 안정적으로 돌지만 전체 회전 시간이 길어집니다.
STEP_DELAY = 0.001

# DIR_DELAY:
# DIR 방향 핀을 바꾼 뒤 실제 펄스를 보내기 전에 기다리는 시간입니다. 단위는 초입니다.
# 드라이버가 방향 신호를 안정적으로 인식할 시간을 주는 값입니다.
# 너무 작으면 방향 전환 직후 첫 펄스가 잘못 들어갈 수 있습니다.
# 보통 크게 자주 만질 값은 아니고, 방향 전환 문제가 있을 때만 조정합니다.
DIR_DELAY = 0.02

# STEPPER_PINS:
# 스텝모터 드라이버 GPIO 핀입니다.
# pul은 펄스 입력, dir은 방향 입력입니다.
# 배선이 바뀐 경우에만 수정하세요.
STEPPER_PINS = {
    "pul": 17,
    "dir": 27,
}

# SERVO_GPIO:
# 서보모터 PWM 제어 GPIO 핀입니다.
# 기존 프로젝트의 SERVO_GPIO=22 값을 그대로 반영했습니다.
SERVO_GPIO = 22

# SERVO_SPEED:
# 서보 내부 제어 루프에서 사용하는 기본 이동 속도입니다. 단위는 도/초(deg/s)입니다.
# move_to()처럼 목표 각도만 줄 때 이 속도로 천천히 이동합니다.
# 이번 Flow의 2초 이동은 move_relative_slow()에서 별도 계산하지만 기본값으로도 사용됩니다.
SERVO_SPEED = 2.0

# SERVO_DEG_PER_SEC:
# Flow에서 서보를 상대 이동시킬 목표 속도입니다. 단위는 도/초입니다.
# 현재 2.0이면 1초에 약 2도 움직입니다.
# 값을 크게 하면 서보 왕복 각도도 커질 수 있으므로 기구 간섭을 확인해야 합니다.
SERVO_DEG_PER_SEC = 2.0

# SERVO_MOVE_SECONDS:
# Flow에서 서보가 한 방향으로 움직이는 시간입니다. 단위는 초입니다.
# 현재는 +방향 2초, -방향 2초로 왕복합니다.
SERVO_MOVE_SECONDS = 2.0

# SERVO_MOVE_DEG:
# 한 번에 이동할 서보 각도입니다.
# SERVO_DEG_PER_SEC * SERVO_MOVE_SECONDS로 계산합니다.
# 현재는 2도/초 * 2초 = 4도입니다.
SERVO_MOVE_DEG = SERVO_DEG_PER_SEC * SERVO_MOVE_SECONDS

# SERVO_HOME_ANGLE:
# 프로그램 시작 시 코드가 기준으로 잡는 서보 초기 각도입니다.
# 실제 장비의 초기 서보 위치와 맞아야 왕복 이동이 의도대로 됩니다.
SERVO_HOME_ANGLE = 0.0

# SERVO_MIN_ANGLE / SERVO_MAX_ANGLE:
# 서보가 움직일 수 있는 최소/최대 각도 제한입니다.
# move_to(), move_relative_slow()에서 이 범위를 넘지 않도록 clamp합니다.
# 실제 기구물이 부딪히는 범위가 있다면 -90~90보다 좁게 잡아야 합니다.
SERVO_MIN_ANGLE = -90.0
SERVO_MAX_ANGLE = 90.0

# SERVO_MIN_PULSE_WIDTH / SERVO_MAX_PULSE_WIDTH:
# AngularServo에 전달하는 PWM 펄스폭입니다. 단위는 초입니다.
# 현재 0.5ms~2.5ms 범위를 사용합니다.
# 서보가 끝까지 가며 떨거나 걸리면 이 값을 더 좁게 조정해야 할 수 있습니다.
# TODO: 사용하는 서보 사양에 맞게 펄스폭과 안전 각도 범위를 보정하세요.
SERVO_MIN_PULSE_WIDTH = 0.5 / 1000
SERVO_MAX_PULSE_WIDTH = 2.5 / 1000

# LOOP_SLEEP_SECONDS:
# main.py의 센서 감지 루프가 한 번 돌고 쉬는 시간입니다. 단위는 초입니다.
# 값을 작게 하면 반응이 빠르지만 CPU 사용량이 늘 수 있습니다.
# 값을 크게 하면 CPU 사용량은 줄지만 감지 반응이 늦어질 수 있습니다.
LOOP_SLEEP_SECONDS = 0.01

# DISTANCE_LOG_INTERVAL_SECONDS:
# 거리값을 터미널에 출력하는 주기입니다. 단위는 초입니다.
# 값을 작게 하면 로그가 자주 찍히고, 크게 하면 로그가 덜 찍힙니다.
# 감지 로직 자체 주기가 아니라 화면 출력 주기만 조절합니다.
DISTANCE_LOG_INTERVAL_SECONDS = 0.2
