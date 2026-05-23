"""PUL/DIR 방식 스텝모터 제어 모듈."""

import time

from gpiozero import DigitalOutputDevice


class StepperMotor:
    """펄스(PUL)와 방향(DIR) 핀으로 스텝모터 드라이버를 제어합니다."""

    def __init__(self, pul, dir, steps_90, step_delay, dir_delay):
        self._pul = DigitalOutputDevice(pul, initial_value=True)
        self._dir = DigitalOutputDevice(dir, initial_value=True)
        self._steps_90 = steps_90
        self._step_delay = step_delay
        self._dir_delay = dir_delay

    def _step(self, steps):
        """지정한 횟수만큼 PUL 핀에 펄스를 보냅니다."""
        for _ in range(steps):
            self._pul.off()
            time.sleep(self._step_delay)
            self._pul.on()
            time.sleep(self._step_delay)

    def rotate_plus_90(self):
        """정방향으로 90도 회전합니다."""
        self._dir.on()
        time.sleep(self._dir_delay)
        self._step(self._steps_90)

    def rotate_minus_90(self):
        """역방향으로 90도 회전합니다."""
        self._dir.off()
        time.sleep(self._dir_delay)
        self._step(self._steps_90)

    def close(self):
        """PUL 핀을 대기 상태로 돌리고 GPIO 자원을 해제합니다."""
        self._pul.on()
        self._pul.close()
        self._dir.close()
