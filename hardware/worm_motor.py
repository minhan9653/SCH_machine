"""BTS 드라이버 기반 웜기어 모터 그룹 제어 모듈."""

from gpiozero import DigitalOutputDevice, PWMOutputDevice


class BtsMotor:
    """BTS 드라이버 1개에 연결된 DC 모터 1개를 제어합니다."""

    def __init__(self, rpwm, lpwm, l_en, r_en):
        self._rpwm = PWMOutputDevice(rpwm)
        self._lpwm = PWMOutputDevice(lpwm)
        self._l_en = DigitalOutputDevice(l_en)
        self._r_en = DigitalOutputDevice(r_en)

    def enable(self):
        """드라이버 출력을 활성화합니다."""
        self._l_en.on()
        self._r_en.on()

    def disable(self):
        """드라이버 출력을 비활성화합니다."""
        self._l_en.off()
        self._r_en.off()

    def forward(self, speed):
        """정방향으로 회전합니다."""
        self._lpwm.value = 0.0
        self._rpwm.value = speed

    def stop(self):
        """모터를 정지합니다."""
        self._rpwm.value = 0.0
        self._lpwm.value = 0.0

    def close(self):
        """정지 후 GPIO 자원을 해제합니다."""
        self.stop()
        self.disable()
        self._rpwm.close()
        self._lpwm.close()
        self._l_en.close()
        self._r_en.close()


class WormMotors:
    """여러 웜기어 모터를 하나의 그룹처럼 제어합니다."""

    def __init__(self, pin_sets, speed):
        self._motors = [BtsMotor(**pins) for pins in pin_sets]
        self._speed = speed

    def enable(self):
        """그룹 안의 모든 모터 드라이버를 활성화합니다."""
        for motor in self._motors:
            motor.enable()

    def disable(self):
        """그룹 안의 모든 모터 드라이버를 비활성화합니다."""
        for motor in self._motors:
            motor.disable()

    def forward(self, speed=None):
        """그룹 안의 모든 웜기어 모터를 정방향으로 회전시킵니다."""
        run_speed = self._speed if speed is None else speed
        for motor in self._motors:
            motor.forward(run_speed)

    def stop(self):
        """그룹 안의 모든 웜기어 모터를 정지합니다."""
        for motor in self._motors:
            motor.stop()

    def close(self):
        """그룹 안의 모든 모터 자원을 정리합니다."""
        for motor in self._motors:
            motor.close()
