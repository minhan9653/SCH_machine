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
            print(f"[cleanup warning] {exc}")


def set_state(state):
    """현재 상태를 로그로 출력하고 상태값을 반환합니다."""
    print(f"[main] state: {state.name}")
    return state


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
        print("[main] TFmini ready")

        actuator.enable()
        worm_motors.enable()

        print("[main] linear actuator extend")
        actuator.extend()
        time.sleep(config.ACTUATOR_TIME)
        actuator.stop()
        state = set_state(FlowState.ACTUATOR_EXTENDED)
        print("[main] linear actuator done")

        worm_motors.forward()
        state = set_state(FlowState.WORM_RUNNING)
        print("[main] worm motor running")

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
                print(f"distance: {distance} cm")
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
                        f"[main] object detected: distance <= "
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

                # Flow가 끝나도 거리가 계속 가까우면 재실행하지 않습니다.
                # RESET_DIST 이상 멀어진 뒤에만 다음 감지를 허용합니다.
                if not flow_running.is_set() and distance >= config.RESET_DIST:
                    triggered = False
                    detect_hits = 0
                    state = set_state(FlowState.WORM_RUNNING)
                    print("[main] re-armed: distance >= RESET_DIST")

            time.sleep(config.LOOP_SLEEP_SECONDS)

    except KeyboardInterrupt:
        print("\n[main] stopping")
    except Exception as exc:
        state = set_state(FlowState.ERROR)
        print(f"[main error] {exc}")
    finally:
        # close 전에 먼저 모터 출력을 0으로 내려 안전하게 멈춥니다.
        if worm_motors is not None:
            try:
                worm_motors.stop()
            except Exception as exc:
                print(f"[cleanup warning] worm stop failed: {exc}")
        if actuator is not None:
            try:
                actuator.stop()
            except Exception as exc:
                print(f"[cleanup warning] actuator stop failed: {exc}")
        if servo is not None:
            try:
                servo.stop()
            except Exception as exc:
                print(f"[cleanup warning] servo stop failed: {exc}")
        close_hardware(sensor, actuator, worm_motors, stepper, servo)
        print("[main] cleanup completed")


if __name__ == "__main__":
    main()
