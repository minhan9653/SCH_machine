"""서보모터 절대/상대 각도 제어 모듈."""

import threading
import time

from gpiozero import AngularServo


class ServoController:
    """일반 각도 제어 서보를 현재 각도 기준으로 천천히 이동시킵니다."""

    TICK = 0.05

    def __init__(
        self,
        gpio,
        speed,
        min_angle=-90.0,
        max_angle=90.0,
        home_angle=0.0,
        min_pulse_width=0.5 / 1000,
        max_pulse_width=2.5 / 1000,
    ):
        self._min_angle = float(min_angle)
        self._max_angle = float(max_angle)
        self._speed = float(speed)
        self._servo = AngularServo(
            gpio,
            min_angle=self._min_angle,
            max_angle=self._max_angle,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width,
        )
        self._angle = self.clamp_angle(home_angle)
        self._target = self._angle
        self._servo.angle = self._angle

        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def clamp_angle(self, angle):
        """서보 각도가 안전 범위를 벗어나지 않도록 제한합니다."""
        return max(self._min_angle, min(self._max_angle, float(angle)))

    def _run(self):
        """백그라운드에서 목표 각도까지 조금씩 이동합니다."""
        while not self._stop.is_set():
            with self._lock:
                current = self._angle
                target = self._target
                speed = self._speed

            diff = target - current
            if abs(diff) >= 0.05:
                step = min(abs(diff), speed * self.TICK)
                new_angle = current + step * (1 if diff > 0 else -1)
                with self._lock:
                    self._servo.angle = new_angle
                    self._angle = new_angle

            time.sleep(self.TICK)

    def move_to(self, angle):
        """목표 각도를 설정합니다. 실제 이동은 내부 스레드가 처리합니다."""
        target = self.clamp_angle(angle)
        with self._lock:
            self._target = target

    def move_relative(self, delta_deg):
        """현재 목표 각도를 기준으로 상대 이동합니다."""
        with self._lock:
            target = self._target + float(delta_deg)
        self.move_to(target)

    def move_relative_slow(self, delta_deg, seconds):
        """현재 각도 기준으로 상대 이동하고, 지정한 시간 동안 기다립니다."""
        seconds = max(0.0, float(seconds))
        with self._lock:
            start_angle = self._angle
            old_speed = self._speed

        target = self.clamp_angle(start_angle + float(delta_deg))
        travel = abs(target - start_angle)
        move_speed = travel / seconds if seconds > 0 and travel > 0 else old_speed

        with self._lock:
            self._speed = move_speed
            self._target = target

        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline and not self._stop.is_set():
            time.sleep(min(self.TICK, max(0.0, deadline - time.monotonic())))

        with self._lock:
            self._servo.angle = target
            self._angle = target
            self._target = target
            self._speed = old_speed

    @property
    def angle(self):
        """코드가 추적 중인 현재 서보 각도입니다."""
        with self._lock:
            return self._angle

    def stop(self):
        """현재 위치를 목표 위치로 잡아 추가 이동을 멈춥니다."""
        with self._lock:
            self._target = self._angle

    def close(self):
        """내부 스레드를 멈추고 서보 GPIO 자원을 해제합니다."""
        self.stop()
        self._stop.set()
        self._thread.join(timeout=0.3)
        self._servo.close()
