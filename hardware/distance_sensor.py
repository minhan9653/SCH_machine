"""TFmini distance sensor driver.

TFmini는 UART로 9바이트짜리 프레임을 계속 보냅니다.
이 모듈은 그 프레임에서 거리(cm)를 뽑아 main.py가 쓰기 쉽게 만들어줍니다.
"""

import serial


class TFmini:
    """TFmini UART 거리센서 1개를 다루는 클래스입니다."""

    def __init__(self, port, baudrate, timeout=0.1):
        # serial.Serial은 실제 /dev/serial0 장치를 엽니다.
        # Raspberry Pi UART 설정이 꺼져 있으면 여기서 예외가 발생할 수 있습니다.
        self._serial = serial.Serial(port, baudrate, timeout=timeout)

        # UART 데이터는 중간부터 읽힐 수 있으므로 버퍼에 모아두고 프레임 헤더를 찾습니다.
        self._buffer = bytearray()

    def read_distance(self):
        """새 거리값이 있으면 cm 단위 정수를, 아직 없으면 None을 반환합니다."""

        # 현재 들어와 있는 모든 바이트를 내부 버퍼에 추가합니다.
        if self._serial.in_waiting:
            self._buffer.extend(self._serial.read(self._serial.in_waiting))

        # TFmini 기본 프레임은 9바이트입니다. 최소 9바이트가 쌓였을 때만 파싱합니다.
        while len(self._buffer) >= 9:
            # 정상 프레임은 0x59 0x59로 시작합니다.
            if self._buffer[0] == 0x59 and self._buffer[1] == 0x59:
                frame = self._buffer[:9]

                # 체크섬이 맞는 프레임만 유효한 거리값으로 사용합니다.
                if (sum(frame[:8]) & 0xFF) == frame[8]:
                    distance = frame[2] + (frame[3] << 8)
                    del self._buffer[:9]
                    return distance

            # 헤더가 아니거나 체크섬이 틀리면 한 바이트씩 버리며 다음 헤더를 찾습니다.
            del self._buffer[:1]

        return None

    def close(self):
        """시리얼 포트를 닫습니다."""
        if self._serial.is_open:
            self._serial.close()
