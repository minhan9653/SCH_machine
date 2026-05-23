"""TFmini UART 거리센서 드라이버.

TFmini는 0x59 0x59로 시작하는 9바이트 프레임을 UART로 계속 보냅니다.
이 모듈은 프레임을 찾아 체크섬을 확인한 뒤 거리값(cm)을 반환합니다.
"""

import serial


class TFmini:
    """TFmini 9바이트 프레임을 읽어 거리값(cm)을 반환하는 클래스입니다."""

    FRAME_HEADER = (0x59, 0x59)
    FRAME_SIZE = 9

    def __init__(self, port, baudrate, timeout=0.1):
        self._serial = serial.Serial(port, baudrate, timeout=timeout)
        self._buffer = bytearray()

    def read_distance(self):
        """거리값이 있으면 cm 단위 정수, 없거나 실패하면 None을 반환합니다."""
        try:
            waiting = self._serial.in_waiting
            if waiting:
                self._buffer.extend(self._serial.read(waiting))

            # 버퍼 중간부터 읽히는 경우가 있어 헤더를 찾을 때까지 한 바이트씩 버립니다.
            while len(self._buffer) >= self.FRAME_SIZE:
                if (
                    self._buffer[0] == self.FRAME_HEADER[0]
                    and self._buffer[1] == self.FRAME_HEADER[1]
                ):
                    frame = self._buffer[: self.FRAME_SIZE]
                    # 체크섬이 맞는 프레임만 유효한 거리값으로 사용합니다.
                    if (sum(frame[:8]) & 0xFF) == frame[8]:
                        distance = frame[2] + (frame[3] << 8)
                        del self._buffer[: self.FRAME_SIZE]
                        return distance

                del self._buffer[:1]
        except Exception as exc:
            print(f"[sensor warning] read failed: {exc}")
            return None

        return None

    def close(self):
        """UART 포트를 닫습니다."""
        try:
            if self._serial.is_open:
                self._serial.close()
        except Exception as exc:
            print(f"[sensor warning] close failed: {exc}")
