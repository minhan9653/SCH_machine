# SCH Machine

Raspberry Pi GPIO 기반 기계 제어 프로젝트입니다.
TFmini 거리센서로 물체를 감지하고, 리니어 액추에이터, 웜기어, 스텝모터, 서보모터를 순서대로 제어합니다.

## 실행 파일

- `main.py`: 최종 실행 진입점
- `config.py`: 핀 번호, 거리 기준, 속도, 시간 설정

## 폴더 구조

- `hardware/`: 센서와 모터 같은 하드웨어 제어 모듈
- `sequences/`: 트리거 발생 시 실행되는 동작 순서
- `tests_manual/`: 부품별 수동 테스트 코드
- `archive/old_full_versions/`: 정리 전 통합본 원본 보관
- `archive/experiments/`: 기타 실험/빈 파일 보관

## 실행

```bash
python3 main.py
```

## 파일별 역할

### 최상위 파일

- `main.py`
  - 실제로 실행하는 메인 프로그램입니다.
  - 하드웨어 객체를 만들고, 리니어 액추에이터 초기 세팅을 한 뒤, 거리센서를 계속 읽습니다.
  - 거리값이 트리거 조건에 맞으면 `sequences/inspection_sequence.py`의 동작 순서를 별도 스레드로 실행합니다.

- `config.py`
  - 프로젝트의 주요 설정값을 모아둔 파일입니다.
  - GPIO 핀 번호, 거리 감지 기준, 모터 속도, 서보 각도, 스텝모터 스텝 수를 여기서 수정합니다.
  - 동작을 바꾸고 싶을 때 가장 먼저 확인할 파일입니다.

- `README.md`
  - 프로젝트 구조, 실행 방법, 파일 역할, 수정 위치를 설명하는 문서입니다.

### `hardware/`

- `hardware/distance_sensor.py`
  - TFmini UART 거리센서를 읽는 코드입니다.
  - TFmini의 9바이트 프레임을 해석해서 거리(cm)를 반환합니다.

- `hardware/actuator.py`
  - 리니어 액추에이터를 제어합니다.
  - BTS 드라이버의 `RPWM`, `LPWM`, `L_EN`, `R_EN` 핀을 사용합니다.
  - 현재는 전진(`extend`)과 정지(`stop`)만 사용합니다.

- `hardware/worm_motor.py`
  - 웜기어 모터들을 제어합니다.
  - `config.py`의 `WORM_MOTOR_PINS` 목록에 적힌 모터 수만큼 자동으로 생성합니다.
  - 웜기어를 2개에서 3개로 늘리고 싶으면 이 파일보다 `config.py`의 핀 목록을 먼저 수정하면 됩니다.

- `hardware/stepper_motor.py`
  - 스텝모터의 PUL/DIR 신호를 제어합니다.
  - `rotate_plus_90()`, `rotate_minus_90()`로 90도 회전을 실행합니다.

- `hardware/servo_motor.py`
  - 서보모터를 목표 각도까지 천천히 움직이는 코드입니다.
  - 내부 스레드가 주기적으로 현재 각도를 목표 각도 쪽으로 이동시킵니다.

### `sequences/`

- `sequences/inspection_sequence.py`
  - 거리센서 트리거가 발생했을 때 실행할 순서를 정의합니다.
  - 현재 순서는 웜기어 정지, 스텝모터 +90도, 서보 이동, 웜기어 재시작, 대기 후 서보 복귀입니다.

### `tests_manual/`

- `tests_manual/test_distance_sensor_raw.py`
  - 거리센서 raw 데이터 확인용입니다.

- `tests_manual/test_actuator_extend.py`
  - 리니어 액추에이터 전진 테스트용입니다.

- `tests_manual/test_worm_motors_2ch.py`
  - 웜기어 2개 동시 구동 테스트용입니다.

- `tests_manual/test_stepper_forward_reverse.py`
  - 스텝모터 정방향/역방향 회전 테스트용입니다.

- `tests_manual/test_servo_slow_move.py`
  - `gpiozero.AngularServo` 기반 서보 테스트용입니다.

- `tests_manual/test_servo_lgpio_pulse.py`
  - `lgpio` 기반 서보 펄스 테스트용입니다.

- `tests_manual/test_gpio_init.py`
  - GPIO와 시리얼 초기화가 되는지 확인하는 테스트용입니다.

### `archive/`

- `archive/old_full_versions/`
  - 정리 전 통합본 원본을 보관합니다.
  - 참고용이며, 새 개발은 `main.py`, `config.py`, `hardware/`, `sequences/` 기준으로 진행합니다.

- `archive/experiments/`
  - 실험용 파일 또는 빈 파일을 보관합니다.

## 무엇을 바꾸고 싶을 때 어디를 수정할까?

- 트리거 거리를 바꾸고 싶다
  - `config.py`의 `TRIGGER_DIST`, `RESET_DIST`

- 몇 번 연속 감지해야 동작할지 바꾸고 싶다
  - `config.py`의 `DETECT_COUNT`

- 트리거 후 다시 감지되기까지 최소 시간을 바꾸고 싶다
  - `config.py`의 `COOLDOWN`

- 리니어 액추에이터가 처음에 더 오래 또는 짧게 움직이게 하고 싶다
  - `config.py`의 `ACTUATOR_TIME`

- 리니어 액추에이터 속도를 바꾸고 싶다
  - `config.py`의 `ACTUATOR_SPEED`

- 웜기어 속도를 바꾸고 싶다
  - `config.py`의 `WORM_SPEED`

- 웜기어 모터를 추가하거나 핀을 바꾸고 싶다
  - `config.py`의 `WORM_MOTOR_PINS`

- 스텝모터가 90도를 덜 돌거나 더 돌면 보정하고 싶다
  - `config.py`의 `STEPS_90`

- 스텝모터 속도를 바꾸고 싶다
  - `config.py`의 `STEP_DELAY`

- 서보 목표 각도를 바꾸고 싶다
  - `config.py`의 `SERVO_TARGET_PLUS`, `SERVO_TARGET_HOME`

- 서보 움직임이 너무 느리거나 빠르다
  - `config.py`의 `SERVO_SPEED`

- 트리거 후 동작 순서 자체를 바꾸고 싶다
  - `sequences/inspection_sequence.py`

- 거리 감지 방식이나 TFmini 데이터 해석을 바꾸고 싶다
  - `hardware/distance_sensor.py`

- 시작/종료 흐름, 재감지 조건, 화면 출력 방식을 바꾸고 싶다
  - `main.py`

## 정리 기준

현재 최종 실행 흐름은 기존 `젭ㄹ라ㅏㄹ.py`를 기준으로 나누었습니다.
이전 파일들은 삭제하지 않고 `archive/`와 `tests_manual/`로 이동했습니다.
