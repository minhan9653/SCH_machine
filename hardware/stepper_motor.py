"""Stepper motor control.

PUL/DIR 방식 스텝모터 드라이버를 제어합니다.
PUL 핀에 짧은 펄스를 반복해서 보내고, DIR 핀으로 회전 방향을 정합니다.
"""

import time

from gpiozero import DigitalOutputDevice


class StepperMotor:
    """PUL/DIR 핀으로 제어되는 스텝모터입니다."""

    def __init__(self, pul, dir, steps_90, step_delay, dir_delay):
        # PUL은 펄스 신호입니다. 초기값을 True로 두어 대기 상태를 HIGH로 맞춥니다.
        self._pul = DigitalOutputDevice(pul, initial_value=True)

        # DIR은 회전 방향 신호입니다.
        self._dir = DigitalOutputDevice(dir, initial_value=True)

        # 90도 회전에 필요한 펄스 수와 펄스 간격입니다.
        self._steps_90 = steps_90
        self._step_delay = step_delay
        self._dir_delay = dir_delay

    def _step(self, steps):
        """지정한 횟수만큼 PUL 핀을 LOW/HIGH로 토글합니다."""
        for _ in range(steps):
            self._pul.off()
            time.sleep(self._step_delay)
            self._pul.on()
            time.sleep(self._step_delay)

    def rotate_plus_90(self):
        """DIR을 정방향으로 설정한 뒤 90도만큼 회전합니다."""
        self._dir.on()
        time.sleep(self._dir_delay)
        self._step(self._steps_90)

    def rotate_minus_90(self):
        """DIR을 역방향으로 설정한 뒤 90도만큼 회전합니다."""
        self._dir.off()
        time.sleep(self._dir_delay)
        self._step(self._steps_90)

    def close(self):
        """PUL 핀을 대기 상태로 돌리고 GPIO 자원을 해제합니다."""
        self._pul.on()
        self._pul.close()
        self._dir.close()
