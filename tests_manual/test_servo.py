#!/usr/bin/env python3
"""서보모터 상대 이동 단독 수동 테스트."""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import config
from hardware.servo_motor import ServoController


def main():
    """서보를 +4도 천천히 이동한 뒤 -4도 복귀시킵니다."""
    servo = ServoController(
        config.SERVO_GPIO,
        config.SERVO_SPEED,
        min_angle=config.SERVO_MIN_ANGLE,
        max_angle=config.SERVO_MAX_ANGLE,
        home_angle=config.SERVO_HOME_ANGLE,
        min_pulse_width=config.SERVO_MIN_PULSE_WIDTH,
        max_pulse_width=config.SERVO_MAX_PULSE_WIDTH,
    )

    try:
        print(f"[테스트] 현재 서보 각도: {servo.angle:+.1f}도")
        servo.move_relative_slow(config.SERVO_MOVE_DEG, config.SERVO_MOVE_SECONDS)
        print(f"[테스트] +방향 이동 후 각도: {servo.angle:+.1f}도")
        servo.move_relative_slow(-config.SERVO_MOVE_DEG, config.SERVO_MOVE_SECONDS)
        print(f"[테스트] -방향 복귀 후 각도: {servo.angle:+.1f}도")
    except KeyboardInterrupt:
        print("\n[테스트] 종료 요청 감지")
    finally:
        servo.close()
        print("[테스트] 서보 정리 완료")


if __name__ == "__main__":
    main()
