"""Trigger sequence.

거리센서가 조건을 만족했을 때 실제로 실행되는 동작 순서입니다.
동작 순서를 바꾸고 싶다면 이 파일의 run_inspection_sequence() 안을 수정하면 됩니다.
"""

import time


def run_inspection_sequence(worm_motors, stepper, servo, running_event, config):
    """트리거 1회에 대한 기계 동작을 순서대로 실행합니다."""
    try:
        print("\n[trigger]")

        # 1. 물체가 감지되면 먼저 웜기어를 멈춰서 다음 동작을 안정적으로 시작합니다.
        worm_motors.stop()
        print("  1. worm motors stopped")

        # 2. 스텝모터는 동기 실행입니다. 90도 회전이 끝날 때까지 다음 줄로 넘어가지 않습니다.
        print("  2. stepper +90 deg...")
        stepper.rotate_plus_90()
        print("  2. stepper done")

        # 3. 서보는 목표 각도만 지정합니다.
        # 실제 이동은 ServoController 내부 스레드가 천천히 처리합니다.
        servo.move_to(config.SERVO_TARGET_PLUS)
        print(
            f"  3. servo target {config.SERVO_TARGET_PLUS:+.1f} deg "
            f"at {config.SERVO_SPEED:.1f} deg/s"
        )

        # 4. 스텝모터 회전 후 웜기어를 다시 구동합니다.
        worm_motors.forward()
        print("  4. worm motors restarted")

        # 5. 지정 시간 뒤 서보를 원점 목표로 되돌립니다.
        # SERVO_SPEED가 느리면 이 시간 안에 목표 각도까지 도달하지 못할 수 있습니다.
        print(f"  5. wait {config.SERVO_REVERSE_DELAY:.1f}s, then servo home")
        time.sleep(config.SERVO_REVERSE_DELAY)
        servo.move_to(config.SERVO_TARGET_HOME)
        print(f"  5. servo target {config.SERVO_TARGET_HOME:+.1f} deg")

        print("[sequence done]\n")
    except Exception as exc:
        # 시퀀스 중 오류가 나면 웜기어를 멈춘 뒤 오류를 표시합니다.
        worm_motors.stop()
        print(f"\n[sequence error] {exc}")
    finally:
        # 성공/실패와 관계없이 실행 중 플래그를 내려야 다음 트리거 판단이 정상 동작합니다.
        running_event.clear()
