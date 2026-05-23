"""BTS 드라이버 기반 리니어 액추에이터 제어 모듈."""

from gpiozero import DigitalOutputDevice, PWMOutputDevice


class LinearActuator:
    """RPWM/LPWM 방향 PWM과 enable 핀으로 액추에이터를 제어합니다."""

    def __init__(self, rpwm, lpwm, l_en, r_en, speed=0.6):
        self._rpwm = PWMOutputDevice(rpwm)
        self._lpwm = PWMOutputDevice(lpwm)
        self._l_en = DigitalOutputDevice(l_en)
        self._r_en = DigitalOutputDevice(r_en)
        self._speed = speed

    def enable(self):
        """드라이버 출력을 활성화합니다."""
        self._l_en.on()
        self._r_en.on()

    def disable(self):
        """드라이버 출력을 비활성화합니다."""
        self._l_en.off()
        self._r_en.off()

    def extend(self, speed=None):
        """액추에이터를 전진 방향으로 움직입니다."""
        self._lpwm.value = 0.0
        self._rpwm.value = self._speed if speed is None else speed

    def retract(self, speed=None):
        """액추에이터를 후진 방향으로 움직입니다."""
        self._rpwm.value = 0.0
        self._lpwm.value = self._speed if speed is None else speed

    def stop(self):
        """양쪽 PWM을 0으로 내려 정지합니다."""
        self._rpwm.value = 0.0
        self._lpwm.value = 0.0

    def close(self):
        """정지, 비활성화, GPIO 자원 해제를 순서대로 수행합니다."""
        self.stop()
        self.disable()
        self._rpwm.close()
        self._lpwm.close()
        self._l_en.close()
        self._r_en.close()
