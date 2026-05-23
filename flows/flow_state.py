"""main.py에서 상태 로그를 명확하게 남기기 위한 Flow 상태 Enum."""

from enum import Enum, auto


class FlowState(Enum):
    # 상태를 과하게 복잡하게 쓰지 않고, 로그와 재감지 상태 확인 용도로만 사용합니다.
    INIT = auto()
    SENSOR_READY = auto()
    ACTUATOR_EXTENDED = auto()
    WORM_RUNNING = auto()
    OBJECT_DETECTED = auto()
    FLOW_RUNNING = auto()
    WAIT_REARM = auto()
    ERROR = auto()
