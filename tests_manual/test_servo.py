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
        print(f"[test] current angle: {servo.angle:+.1f} deg")
        servo.move_relative_slow(config.SERVO_MOVE_DEG, config.SERVO_MOVE_SECONDS)
        print(f"[test] after +move: {servo.angle:+.1f} deg")
        servo.move_relative_slow(-config.SERVO_MOVE_DEG, config.SERVO_MOVE_SECONDS)
        print(f"[test] after -move: {servo.angle:+.1f} deg")
    except KeyboardInterrupt:
        print("\n[test] stopping")
    finally:
        servo.close()
        print("[test] closed")


if __name__ == "__main__":
    main()
