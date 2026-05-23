#!/usr/bin/env python3
"""TFmini Machine Flow 실행 진입점.

이 파일은 하드웨어 객체 생성, 거리 감지, 중복 실행 방지, 종료 정리를 담당합니다.
감지 후 실제 모터 동작 순서는 flows/machine_flow.py에서 처리합니다.
"""

import threading
import time

import config
from flows.flow_state import FlowState
from flows.machine_flow import run_machine_flow
from hardware.actuator import LinearActuator
from hardware.distance_sensor import TFmini
from hardware.servo_motor import ServoController
from hardware.stepper_motor import StepperMotor
from hardware.worm_motor import WormMotors


def build_hardware():
    """config.py 값을 이용해 실제 하드웨어 제어 객체를 생성합니다."""
    sensor = TFmini(
        config.TFMINI_PORT,
        config.TFMINI_BAUDRATE,
        timeout=config.SERIAL_TIMEOUT,
    )
    actuator = LinearActuator(**config.ACTUATOR_PINS, speed=config.ACTUATOR_SPEED)
    worm_motors = WormMotors(config.WORM_MOTOR_PINS, config.WORM_SPEED)
    stepper = StepperMotor(
        **config.STEPPER_PINS,
        steps_90=config.STEPS_90,
        step_delay=config.STEP_DELAY,
        dir_delay=config.DIR_DELAY,
    )
    servo = ServoController(
        config.SERVO_GPIO,
        config.SERVO_SPEED,
        min_angle=config.SERVO_MIN_ANGLE,
        max_angle=config.SERVO_MAX_ANGLE,
        home_angle=config.SERVO_HOME_ANGLE,
        min_pulse_width=config.SERVO_MIN_PULSE_WIDTH,
        max_pulse_width=config.SERVO_MAX_PULSE_WIDTH,
    )
    return sensor, actuator, worm_motors, stepper, servo


def close_hardware(sensor, actuator, worm_motors, stepper, servo):
    """프로그램 종료 시 모든 장치의 close()를 안전하게 호출합니다."""
    for device in (worm_motors, actuator, stepper, servo, sensor):
        if device is None:
            continue
        try:
            device.close()
        except Exception as exc:
            print(f"[정리 경고] 장치 정리 중 문제 발생: {exc}")


STATE_LABELS = {
    FlowState.INIT: "초기화",
    FlowState.SENSOR_READY: "센서 준비 완료",
    FlowState.ACTUATOR_EXTENDED: "액추에이터 초기 전진 완료",
    FlowState.WORM_RUNNING: "웜기어 모터 기본 동작 중",
    FlowState.OBJECT_DETECTED: "물체 감지",
    FlowState.FLOW_RUNNING: "Flow 실행 중",
    FlowState.WAIT_REARM: "재감지 대기",
    FlowState.ERROR: "오류",
}


def set_state(state):
    """현재 상태를 로그로 출력하고 상태값을 반환합니다."""
    print(f"[메인] 상태: {STATE_LABELS.get(state, state.name)}")
    return state


def is_rearmed_distance(distance):
    """같은 물체가 감지 거리 경계에 있을 때 반복 실행되지 않도록 재감지 거리를 판단합니다."""
    return distance >= config.RESET_DIST and distance > config.TRIGGER_DIST


def main():
    """메인 실행 루프입니다."""
    # 중간 초기화 실패가 나도 finally에서 안전하게 정리할 수 있도록 None으로 시작합니다.
    sensor = actuator = worm_motors = stepper = servo = None

    # Flow 실행 중에는 같은 물체로 Flow가 중복 실행되지 않도록 Event를 사용합니다.
    flow_running = threading.Event()
    state = set_state(FlowState.INIT)

    try:
        sensor, actuator, worm_motors, stepper, servo = build_hardware()
        state = set_state(FlowState.SENSOR_READY)
        print("[메인] TFmini 거리센서 준비 완료")

        actuator.enable()
        worm_motors.enable()

        print("[메인] 리니어 액추에이터 초기 전진 시작")
        actuator.extend()
        time.sleep(config.ACTUATOR_TIME)
        actuator.stop()
        state = set_state(FlowState.ACTUATOR_EXTENDED)
        print("[메인] 리니어 액추에이터 초기 전진 완료")

        worm_motors.forward()
        state = set_state(FlowState.WORM_RUNNING)
        print("[메인] 웜기어 모터 기본 동작 시작")

        # triggered=True이면 물체가 아직 가까이 있어서 재감지를 막는 상태입니다.
        triggered = False

        # 거리값이 기준 이하로 연속 감지된 횟수입니다.
        detect_hits = 0
        last_trigger_time = 0.0
        last_distance_log = 0.0

        while True:
            distance = sensor.read_distance()
            now = time.monotonic()

            if distance is None:
                # 센서 읽기 실패는 프로그램 종료가 아니라 다음 루프에서 재시도합니다.
                time.sleep(config.LOOP_SLEEP_SECONDS)
                continue

            if now - last_distance_log >= config.DISTANCE_LOG_INTERVAL_SECONDS:
                print(f"거리: {distance} cm")
                last_distance_log = now

            if not triggered:
                if distance <= config.TRIGGER_DIST:
                    detect_hits += 1
                else:
                    detect_hits = 0

                # 연속 감지 횟수, 쿨다운, Flow 미실행 상태를 모두 만족해야 시작합니다.
                cooldown_ready = now - last_trigger_time >= config.COOLDOWN_SECONDS
                if (
                    detect_hits >= config.DETECT_COUNT
                    and cooldown_ready
                    and not flow_running.is_set()
                ):
                    print(
                        f"[메인] 물체 감지: 거리 <= "
                        f"{config.TRIGGER_DIST}cm"
                    )
                    triggered = True
                    detect_hits = 0
                    last_trigger_time = now
                    flow_running.set()
                    state = set_state(FlowState.FLOW_RUNNING)

                    # Flow는 시간이 걸리므로 별도 스레드에서 실행합니다.
                    # 메인 루프는 계속 센서값을 읽으면서 재감지 조건을 관리합니다.
                    threading.Thread(
                        target=run_machine_flow,
                        args=(worm_motors, stepper, servo, flow_running, config),
                        daemon=True,
                    ).start()

            else:
                if state is FlowState.FLOW_RUNNING and not flow_running.is_set():
                    state = set_state(FlowState.WAIT_REARM)
                    print(
                        f"[메인] 거리값이 {config.TRIGGER_DIST}cm 기준보다 "
                        "멀어질 때까지 재감지를 대기합니다"
                    )

                # Flow가 끝나도 거리가 계속 가까우면 재실행하지 않습니다.
                # RESET_DIST 이상이면서 TRIGGER_DIST보다 멀어진 뒤에만 다음 감지를 허용합니다.
                if not flow_running.is_set() and is_rearmed_distance(distance):
                    triggered = False
                    detect_hits = 0
                    state = set_state(FlowState.WORM_RUNNING)
                    print(
                        f"[메인] 재감지 가능: 거리 > "
                        f"{config.TRIGGER_DIST}cm"
                    )

            time.sleep(config.LOOP_SLEEP_SECONDS)

    except KeyboardInterrupt:
        print("\n[메인] 종료 요청 감지, 장치를 정리합니다")
    except Exception as exc:
        state = set_state(FlowState.ERROR)
        print(f"[메인 오류] {exc}")
    finally:
        # close 전에 먼저 모터 출력을 0으로 내려 안전하게 멈춥니다.
        if worm_motors is not None:
            try:
                worm_motors.stop()
            except Exception as exc:
                print(f"[정리 경고] 웜기어 모터 정지 실패: {exc}")
        if actuator is not None:
            try:
                actuator.stop()
            except Exception as exc:
                print(f"[정리 경고] 액추에이터 정지 실패: {exc}")
        if servo is not None:
            try:
                servo.stop()
            except Exception as exc:
                print(f"[정리 경고] 서보 정지 실패: {exc}")
        close_hardware(sensor, actuator, worm_motors, stepper, servo)
        print("[메인] 장치 정리 완료")


if __name__ == "__main__":
    main()
