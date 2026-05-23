"""Servo motor controller.

gpiozero.AngularServo를 감싸서 목표 각도까지 일정 속도로 천천히 이동시킵니다.
move_to()는 목표만 바꾸고, 실제 이동은 내부 스레드가 계속 처리합니다.
"""

import threading
import time

from gpiozero import AngularServo


class ServoController:
    """표준 PWM 서보를 목표 각도 기반으로 제어합니다."""

    # 내부 제어 루프 주기입니다. 0.05초마다 현재 각도를 조금씩 목표 쪽으로 이동합니다.
    TICK = 0.05

    def __init__(self, gpio, speed):
        # min/max pulse width는 일반적인 0.5ms~2.5ms 서보 범위입니다.
        # 사용하는 서보의 사양이 다르면 이 값을 조정해야 합니다.
        self._servo = AngularServo(
            gpio,
            min_angle=-90,
            max_angle=90,
            min_pulse_width=0.5 / 1000,
            max_pulse_width=2.5 / 1000,
        )

        # speed는 초당 이동 각도(deg/s)입니다.
        self._speed = speed
        self._angle = 0.0
        self._target = 0.0

        # 메인 스레드와 서보 제어 스레드가 같은 값을 건드리므로 Lock으로 보호합니다.
        self._lock = threading.Lock()
        self._stop = threading.Event()

        # daemon=True라서 프로그램 종료 시 이 스레드가 프로세스를 붙잡지 않습니다.
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        """목표 각도를 향해 서보를 조금씩 움직이는 내부 루프입니다."""
        step_max = self._speed * self.TICK

        while not self._stop.is_set():
            with self._lock:
                current = self._angle
                target = self._target

            diff = target - current
            if abs(diff) >= 0.05:
                # 한 tick에서 이동할 수 있는 최대 각도만큼만 움직여 속도를 제한합니다.
                step = min(abs(diff), step_max)
                new_angle = current + step * (1 if diff > 0 else -1)

                with self._lock:
                    self._servo.angle = new_angle
                    self._angle = new_angle

            time.sleep(self.TICK)

    def move_to(self, target):
        """서보 목표 각도를 설정합니다. 실제 이동은 _run()에서 비동기로 처리됩니다."""
        # 서보 범위를 넘는 값이 들어와도 -90~90 사이로 제한합니다.
        target = max(-90.0, min(90.0, float(target)))
        with self._lock:
            self._target = target

    @property
    def angle(self):
        """현재 코드가 추적하는 서보 각도입니다."""
        with self._lock:
            return self._angle

    def close(self):
        """내부 스레드를 멈추고 서보를 0도로 돌린 뒤 GPIO 자원을 해제합니다."""
        self._stop.set()
        self._thread.join(timeout=0.3)
        self._servo.angle = 0
        self._servo.close()
