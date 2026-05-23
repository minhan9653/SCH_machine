"""Linear actuator control.

BTS 계열 모터 드라이버 1개로 리니어 액추에이터를 전진/정지시키는 모듈입니다.
현재 프로젝트에서는 시작할 때 일정 시간 전진한 뒤 정지하는 용도로 사용합니다.
"""

from gpiozero import DigitalOutputDevice, PWMOutputDevice


class LinearActuator:
    """RPWM/LPWM/L_EN/R_EN 핀으로 제어되는 리니어 액추에이터입니다."""

    def __init__(self, rpwm, lpwm, l_en, r_en, speed=0.6):
        # RPWM/LPWM은 방향별 PWM 출력입니다.
        # 한쪽 PWM만 켜면 해당 방향으로 움직이고, 둘 다 0이면 정지합니다.
        self._rpwm = PWMOutputDevice(rpwm)
        self._lpwm = PWMOutputDevice(lpwm)

        # L_EN/R_EN은 드라이버 활성화 핀입니다.
        self._l_en = DigitalOutputDevice(l_en)
        self._r_en = DigitalOutputDevice(r_en)
        self._speed = speed

    def enable(self):
        """BTS 드라이버를 활성화합니다."""
        self._l_en.on()
        self._r_en.on()

    def disable(self):
        """BTS 드라이버를 비활성화합니다."""
        self._l_en.off()
        self._r_en.off()

    def extend(self, speed=None):
        """액추에이터를 전진 방향으로 움직입니다."""
        self._lpwm.value = 0.0
        self._rpwm.value = self._speed if speed is None else speed

    def stop(self):
        """양쪽 PWM을 0으로 내려 액추에이터를 정지합니다."""
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
