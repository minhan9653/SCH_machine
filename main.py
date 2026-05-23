#!/usr/bin/env python3
"""Final runtime entry point for the SCH machine.

이 파일은 전체 프로그램의 출발점입니다.
하드웨어 객체 생성, 시작 준비, 거리 감지 루프, 트리거 판단, 종료 정리를 담당합니다.
모터가 실제로 어떻게 움직이는지는 hardware/와 sequences/ 쪽 파일에 나누어져 있습니다.
"""

import sys
import threading
import time

import config
from hardware.actuator import LinearActuator
from hardware.distance_sensor import TFmini
from hardware.servo_motor import ServoController
from hardware.stepper_motor import StepperMotor
from hardware.worm_motor import WormMotors
from sequences.inspection_sequence import run_inspection_sequence


def build_hardware():
    """설정값(config.py)을 바탕으로 실제 하드웨어 제어 객체를 생성합니다."""
    sensor = TFmini(config.SERIAL_PORT, config.BAUDRATE)
    actuator = LinearActuator(**config.ACTUATOR_PINS, speed=config.ACTUATOR_SPEED)
    worm_motors = WormMotors(config.WORM_MOTOR_PINS, config.WORM_SPEED)
    stepper = StepperMotor(**config.STEPPER_PINS, steps_90=config.STEPS_90,
                           step_delay=config.STEP_DELAY, dir_delay=config.DIR_DELAY)
    servo = ServoController(config.SERVO_GPIO, config.SERVO_SPEED)
    return sensor, actuator, worm_motors, stepper, servo


def close_hardware(sensor, actuator, worm_motors, stepper, servo):
    """프로그램 종료 시 모든 장치를 정지하고 GPIO/시리얼 자원을 닫습니다."""
    for device in (actuator, worm_motors, stepper, servo, sensor):
        if device is not None:
            try:
                device.close()
            except Exception as exc:
                print(f"cleanup warning: {exc}")


def main():
    # None으로 먼저 선언해두면, 중간 초기화 실패가 나도 finally에서 안전하게 정리할 수 있습니다.
    sensor = actuator = worm_motors = stepper = servo = None

    # 트리거 시퀀스가 실행 중인지 표시하는 플래그입니다.
    # 이 값이 켜져 있으면 같은 물체에 대해 중복 시퀀스가 시작되지 않습니다.
    sequence_running = threading.Event()

    try:
        # 1. 하드웨어 객체 생성
        sensor, actuator, worm_motors, stepper, servo = build_hardware()

        # 2. BTS 드라이버 Enable 핀을 켭니다.
        actuator.enable()
        worm_motors.enable()

        # 3. 시작 시 리니어 액추에이터를 지정 시간만큼 전진시켜 초기 위치를 잡습니다.
        print(f"TFmini ready ({config.SERIAL_PORT})")
        print("linear actuator set...")
        actuator.extend()
        time.sleep(config.ACTUATOR_TIME)
        actuator.stop()
        print("linear actuator done")

        # 4. 기본 상태에서는 웜기어가 계속 전진합니다.
        worm_motors.forward()
        print("worm motors running")
        print("=" * 45)
        print("distance monitoring... Ctrl+C to stop")
        print("=" * 45)

        triggered = False
        detect_hits = 0
        last_trigger_time = 0.0

        # 5. 메인 감지 루프입니다. Ctrl+C가 들어올 때까지 계속 센서를 읽습니다.
        while True:
            distance = sensor.read_distance()

            if distance is not None:
                # 한 줄에 현재 거리와 서보 각도를 계속 갱신해서 보여줍니다.
                sys.stdout.write(
                    f"\rdistance: {distance:4d} cm  "
                    f"servo: {servo.angle:+6.1f} deg  "
                )
                sys.stdout.flush()

                now = time.time()

                if not triggered:
                    # 거리값이 기준 이하일 때만 연속 감지 횟수를 쌓습니다.
                    # 중간에 기준보다 멀어지면 0으로 초기화합니다.
                    detect_hits = detect_hits + 1 if distance <= config.TRIGGER_DIST else 0

                    # 연속 감지 횟수와 쿨다운 조건을 모두 만족하면 트리거 시퀀스를 시작합니다.
                    if (
                        detect_hits >= config.DETECT_COUNT
                        and now - last_trigger_time >= config.COOLDOWN
                    ):
                        triggered = True
                        last_trigger_time = now
                        detect_hits = 0
                        sequence_running.set()

                        # 모터 시퀀스는 시간이 걸리므로 별도 스레드에서 실행합니다.
                        # 이렇게 해야 메인 루프가 계속 거리센서를 읽고 화면을 갱신할 수 있습니다.
                        threading.Thread(
                            target=run_inspection_sequence,
                            args=(worm_motors, stepper, servo, sequence_running, config),
                            daemon=True,
                        ).start()
                elif not sequence_running.is_set() and distance >= config.RESET_DIST:
                    # 시퀀스가 끝났고 물체가 충분히 멀어졌을 때만 다음 트리거를 허용합니다.
                    triggered = False
                    detect_hits = 0
                    print("\n[ready for next trigger]")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nstopping...")
    finally:
        # 종료 시에는 close 전에 먼저 모터 출력을 0으로 내려 안전하게 멈춥니다.
        if worm_motors is not None:
            worm_motors.stop()
        if actuator is not None:
            actuator.stop()
        close_hardware(sensor, actuator, worm_motors, stepper, servo)
        print("system stopped")


if __name__ == "__main__":
    main()
