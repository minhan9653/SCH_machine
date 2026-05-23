# TFmini Machine Flow

## 1. 프로젝트 목적

`tfmini_machine_flow/`는 TFmini 거리센서 감지를 기준으로 장비 동작 Flow를 실행하는 별도 프로젝트입니다.

기존 루트 프로젝트 파일은 설정값과 하드웨어 제어 방식을 참고만 했습니다. 이 폴더는 자체 `main.py`, `config.py`, `hardware/`, `flows/`, `tests_manual/`을 가지고 독립적으로 동작합니다.

## 2. 폴더 구조

```text
tfmini_machine_flow/
├─ main.py
├─ config.py
├─ hardware/
│  ├─ __init__.py
│  ├─ distance_sensor.py
│  ├─ actuator.py
│  ├─ worm_motor.py
│  ├─ stepper_motor.py
│  └─ servo_motor.py
├─ flows/
│  ├─ __init__.py
│  ├─ machine_flow.py
│  └─ flow_state.py
├─ tests_manual/
│  ├─ test_distance_sensor.py
│  ├─ test_actuator.py
│  ├─ test_worm_motor.py
│  ├─ test_stepper.py
│  └─ test_servo.py
└─ README.md
```

## 3. 실행 방법

작업 폴더 루트(`/home/pi/Desktop`)에서 아래 명령어를 실행합니다.

```bash
python3 tfmini_machine_flow/main.py
```

종료할 때는 `Ctrl+C`를 누릅니다. 종료 시 모터 정지, PWM 정지, 센서 close 처리를 수행합니다.

## 4. 전체 동작 Flow

1. 프로그램이 시작됩니다.
2. TFmini 거리센서를 UART로 연결합니다.
3. 리니어 액추에이터를 설정된 시간만큼 전진시킵니다.
4. 웜기어 모터를 계속 동작시킵니다.
5. 거리값이 60cm 이하로 감지됩니다.
6. 웜기어 모터를 정지합니다.
7. 스텝모터를 +90도 회전합니다.
8. 서보모터를 +방향으로 2초 동안 천천히 이동합니다.
9. 웜기어 모터를 5초 동안 동작시킨 뒤 정지합니다.
10. 서보모터를 -방향으로 2초 동안 천천히 복귀시킵니다.
11. 웜기어 모터를 다시 동작시킵니다.
12. 거리값이 `RESET_DIST` 이상 멀어지면 다시 감지 가능한 상태가 됩니다.

## 5. 재감지 조건

거리값이 `TRIGGER_DIST` 이하로 `DETECT_COUNT`번 연속 들어오면 Flow가 1회 실행됩니다.

같은 물체가 가까운 거리에 계속 있는 동안에는 Flow가 반복 실행되지 않습니다. Flow 실행 중에도 중복 실행되지 않고, Flow가 끝난 뒤에도 거리값이 `RESET_DIST`보다 가까우면 다시 실행되지 않습니다.

거리값이 `RESET_DIST` 이상 멀어진 뒤에만 다음 감지가 가능합니다.

## 6. config.py에서 수정할 수 있는 값

주요 설정값은 [config.py](/home/pi/Desktop/tfmini_machine_flow/config.py)에 있습니다.

- `TFMINI_PORT`, `TFMINI_BAUDRATE`, `SERIAL_TIMEOUT`
- `TRIGGER_DIST`, `RESET_DIST`, `DETECT_COUNT`, `COOLDOWN_SECONDS`
- `ACTUATOR_PINS`, `ACTUATOR_SPEED`, `ACTUATOR_TIME`
- `WORM_MOTOR_PINS`, `WORM_SPEED`, `WORM_RUN_SECONDS`
- `STEPPER_PINS`, `STEPS_90`, `STEP_DELAY`, `DIR_DELAY`
- `SERVO_GPIO`, `SERVO_SPEED`, `SERVO_DEG_PER_SEC`, `SERVO_MOVE_SECONDS`
- `SERVO_HOME_ANGLE`, `SERVO_MIN_ANGLE`, `SERVO_MAX_ANGLE`
- `SERVO_MIN_PULSE_WIDTH`, `SERVO_MAX_PULSE_WIDTH`

자세한 실행 방법과 값 변경 설명은 [실행_설정_가이드.md](/home/pi/Desktop/tfmini_machine_flow/실행_설정_가이드.md)를 확인하세요.

## 7. 부품별 수동 테스트

각 부품을 따로 확인할 때는 작업 폴더 루트에서 아래 명령어를 실행합니다.

```bash
python3 tfmini_machine_flow/tests_manual/test_distance_sensor.py
python3 tfmini_machine_flow/tests_manual/test_actuator.py
python3 tfmini_machine_flow/tests_manual/test_worm_motor.py
python3 tfmini_machine_flow/tests_manual/test_stepper.py
python3 tfmini_machine_flow/tests_manual/test_servo.py
```

## 8. 하드웨어 보정 TODO

- `ACTUATOR_TIME`: 실제로 리니어 액추에이터가 약 3cm 전진하는 시간을 측정해서 보정해야 합니다.
- `SERVO_MIN_PULSE_WIDTH`, `SERVO_MAX_PULSE_WIDTH`: 사용하는 서보 사양에 맞게 PWM 펄스폭을 확인해야 합니다.
- `SERVO_MIN_ANGLE`, `SERVO_MAX_ANGLE`: 실제 기구물의 안전 각도 범위에 맞게 확인해야 합니다.
- `STEPS_90`: 스텝모터 드라이버의 마이크로스텝 설정에 따라 90도 펄스 수를 확인해야 합니다.
- `WORM_SPEED`: 실제 부하 상태에서 웜기어 모터 속도가 적절한지 확인해야 합니다.

## 9. 기존 소스 처리 기준

기존 루트의 `main.py`, `config.py`, `hardware/`, `sequences/`, `flows/`, `tests_manual/`, `archive/`는 수정하지 않습니다.

이 프로젝트는 기존 설정값과 하드웨어 제어 방식을 참고만 하고, 새 구현은 모두 `tfmini_machine_flow/` 아래에서 관리합니다.
