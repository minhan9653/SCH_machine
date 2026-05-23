#!/usr/bin/env python3
"""리니어 액추에이터 단독 수동 테스트."""

import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import config
from hardware.actuator import LinearActuator


def main():
    """설정된 시간만큼 액추에이터를 전진시킨 뒤 정지합니다."""
    actuator = LinearActuator(**config.ACTUATOR_PINS, speed=config.ACTUATOR_SPEED)

    try:
        actuator.enable()
        print("[테스트] 리니어 액추에이터 전진 시작")
        actuator.extend()
        time.sleep(config.ACTUATOR_TIME)
        actuator.stop()
        print("[테스트] 리니어 액추에이터 정지")
    except KeyboardInterrupt:
        print("\n[테스트] 종료 요청 감지")
    finally:
        actuator.close()
        print("[테스트] 액추에이터 정리 완료")


if __name__ == "__main__":
    main()
