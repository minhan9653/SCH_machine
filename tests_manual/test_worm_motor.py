#!/usr/bin/env python3
"""웜기어 모터 그룹 단독 수동 테스트."""

import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import config
from hardware.worm_motor import WormMotors


def main():
    """웜기어 모터를 설정된 시간만큼 정방향으로 돌린 뒤 정지합니다."""
    worm_motors = WormMotors(config.WORM_MOTOR_PINS, config.WORM_SPEED)

    try:
        worm_motors.enable()
        print("[테스트] 웜기어 모터 정방향 동작 시작")
        worm_motors.forward()
        time.sleep(config.WORM_RUN_SECONDS)
        worm_motors.stop()
        print("[테스트] 웜기어 모터 정지")
    except KeyboardInterrupt:
        print("\n[테스트] 종료 요청 감지")
    finally:
        worm_motors.close()
        print("[테스트] 웜기어 모터 정리 완료")


if __name__ == "__main__":
    main()
