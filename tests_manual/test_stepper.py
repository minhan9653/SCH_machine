#!/usr/bin/env python3
"""스텝모터 +90도 단독 수동 테스트."""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import config
from hardware.stepper_motor import StepperMotor


def main():
    """스텝모터를 +90도 방향으로 1회 회전합니다."""
    stepper = StepperMotor(
        **config.STEPPER_PINS,
        steps_90=config.STEPS_90,
        step_delay=config.STEP_DELAY,
        dir_delay=config.DIR_DELAY,
    )

    try:
        print("[test] stepper +90")
        stepper.rotate_plus_90()
        print("[test] stepper +90 done")
    except KeyboardInterrupt:
        print("\n[test] stopping")
    finally:
        stepper.close()
        print("[test] closed")


if __name__ == "__main__":
    main()
