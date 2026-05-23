#!/usr/bin/env python3
"""TFmini 거리센서 단독 수동 테스트."""

import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import config
from hardware.distance_sensor import TFmini


def main():
    """TFmini를 연결하고 거리값 또는 None을 반복 출력합니다."""
    sensor = TFmini(
        config.TFMINI_PORT,
        config.TFMINI_BAUDRATE,
        timeout=config.SERIAL_TIMEOUT,
    )
    print("[test] TFmini connected")

    try:
        while True:
            distance = sensor.read_distance()
            if distance is None:
                print("distance: None")
            else:
                print(f"distance: {distance} cm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[test] stopping")
    finally:
        sensor.close()
        print("[test] closed")


if __name__ == "__main__":
    main()
