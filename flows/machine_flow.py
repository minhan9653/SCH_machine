"""물체 감지 후 실행되는 전체 장비 Flow."""

import time


def run_machine_flow(worm_motors, stepper, servo, flow_running_event, config):
    """감지 1회에 대해 모터 시퀀스를 한 번만 실행합니다."""
    try:
        print("[동작] 물체 감지 Flow 시작")

        # 1. 감지 즉시 웜기어 모터를 정지합니다.
        worm_motors.stop()
        print("[동작] 웜기어 모터 정지")

        # 2. 스텝모터를 +90도 회전합니다.
        stepper.rotate_plus_90()
        print("[동작] 스텝모터 +90도 회전 완료")

        # 3. 서보를 +방향으로 2초 동안 약 4도 이동합니다.
        servo.move_relative_slow(config.SERVO_MOVE_DEG, config.SERVO_MOVE_SECONDS)
        print(f"[동작] 서보 +방향 {config.SERVO_MOVE_DEG:g}도 이동 완료")

        # 4. 웜기어 모터를 5초 동안 다시 동작시킵니다.
        worm_motors.forward()
        print(f"[동작] 웜기어 모터 {config.WORM_RUN_SECONDS:g}초 동작 시작")
        time.sleep(config.WORM_RUN_SECONDS)

        # 5. 5초 동작 후 웜기어 모터를 정지합니다.
        worm_motors.stop()
        print("[동작] 웜기어 모터 5초 동작 완료")
        print("[동작] 웜기어 모터 정지")

        # 6. 서보를 -방향으로 같은 각도만큼 이동해 원래 위치로 복귀합니다.
        servo.move_relative_slow(-config.SERVO_MOVE_DEG, config.SERVO_MOVE_SECONDS)
        print(f"[동작] 서보 -방향 {config.SERVO_MOVE_DEG:g}도 복귀 완료")

        # 7. 스텝모터를 -90도 회전해 원래 위치로 복귀합니다.
        stepper.rotate_minus_90()
        print("[동작] 스텝모터 -90도 복귀 완료")

        # 8. Flow가 끝나면 웜기어 모터를 기본 구동 상태로 되돌립니다.
        worm_motors.forward()
        print("[동작] 웜기어 모터 재시작")

    except Exception as exc:
        # Flow 중 예외가 나면 안전을 위해 웜기어 모터를 먼저 정지합니다.
        try:
            worm_motors.stop()
        except Exception:
            pass
        print(f"[동작 오류] {exc}")
    finally:
        # 어떤 경우에도 Flow 실행 플래그를 내려 main.py가 상태를 알 수 있게 합니다.
        flow_running_event.clear()
