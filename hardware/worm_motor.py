"""Worm gear motor control.

BTS 계열 드라이버에 연결된 웜기어 모터 여러 개를 한 번에 제어합니다.
모터 수는 config.py의 WORM_MOTOR_PINS 목록 길이에 따라 결정됩니다.
"""

from gpiozero import DigitalOutputDevice, PWMOutputDevice


class BtsMotor:
    """BTS 드라이버 1개에 연결된 DC 모터 1개를 제어합니다."""

    def __init__(self, rpwm, lpwm, l_en, r_en):
        # RPWM/LPWM은 방향 제어용 PWM 핀입니다.
        self._rpwm = PWMOutputDevice(rpwm)
        self._lpwm = PWMOutputDevice(lpwm)

        # Enable 핀이 꺼져 있으면 PWM 값을 줘도 모터가 돌지 않습니다.
        self._l_en = DigitalOutputDevice(l_en)
        self._r_en = DigitalOutputDevice(r_en)

    def enable(self):
        """드라이버 출력을 허용합니다."""
        self._l_en.on()
        self._r_en.on()

    def disable(self):
        """드라이버 출력을 차단합니다."""
        self._l_en.off()
        self._r_en.off()

    def forward(self, speed):
        """정방향 회전. speed는 0.0~1.0 범위의 PWM duty 값입니다."""
        self._lpwm.value = 0.0
        self._rpwm.value = speed

    def stop(self):
        """양쪽 PWM을 0으로 내려 모터를 정지합니다."""
        self._rpwm.value = 0.0
        self._lpwm.value = 0.0

    def close(self):
        """모터를 멈추고 GPIO 자원을 해제합니다."""
        self.stop()
        self.disable()
        self._rpwm.close()
        self._lpwm.close()
        self._l_en.close()
        self._r_en.close()


class WormMotors:
    """여러 웜기어 모터를 한 그룹처럼 다루는 클래스입니다."""

    def __init__(self, pin_sets, speed):
        # pin_sets 안의 dict 하나가 모터 1개입니다.
        # 예: [{"rpwm": 12, "lpwm": 13, ...}, {"rpwm": 20, ...}]
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
        """그룹 안의 모든 웜기어를 같은 속도로 정방향 회전시킵니다."""
        run_speed = self._speed if speed is None else speed
        for motor in self._motors:
            motor.forward(run_speed)

    def stop(self):
        """그룹 안의 모든 웜기어를 정지합니다."""
        for motor in self._motors:
            motor.stop()

    def close(self):
        """그룹 안의 모든 모터 자원을 정리합니다."""
        for motor in self._motors:
            motor.close()
