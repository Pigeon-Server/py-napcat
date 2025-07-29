from dataclasses import dataclass
from enum import Enum

from .basic_event import Serializable, PostType, BasicEvent


class MetaEventType(Enum):
    HEARTBEAT = "heartbeat"
    LIFECYCLE = "lifecycle"


class MetaEvent(BasicEvent):
    meta_event_type: MetaEventType

    def __init__(self, time: int, self_id: int, meta_event_type: MetaEventType):
        super().__init__(time, PostType.META, self_id)
        self.meta_event_type = meta_event_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["meta_event_type"] = self.meta_event_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "MetaEvent":
        return cls(json_dict["time"], json_dict["self_id"], MetaEventType(json_dict["meta_event_type"].value))


class HeartbeatEvent(MetaEvent):
    @dataclass
    class HeartbeatStatus(Serializable):
        online: bool
        good: bool

        def to_json(self) -> dict:
            return {"online": self.online, "good": self.good}

        @classmethod
        def from_json(cls, json_dict: dict) -> "HeartbeatEvent.HeartbeatStatus":
            return cls(json_dict["online"], json_dict["good"])

    status: HeartbeatStatus
    interval: int

    def __init__(self, time: int, self_id: int, status: HeartbeatStatus, interval: int):
        super().__init__(time, self_id, MetaEventType.HEARTBEAT)
        self.status = status
        self.interval = interval

    def to_json(self) -> dict:
        data = super().to_json()
        data["status"] = self.status.to_json()
        data["interval"] = self.interval
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "MetaEvent":
        return cls(json_dict["time"], json_dict["self_id"],
                   cls.HeartbeatStatus.from_json(json_dict["status"]), json_dict["interval"])


class LifeCycleEvent(MetaEvent):
    class LifeCycleType(Enum):
        ENABLE = "enable"
        DISABLE = "disable"
        CONNECT = "connect"

    sub_type: LifeCycleType

    def __init__(self, time: int, self_id: int, sub_type: LifeCycleType) -> None:
        super().__init__(time, self_id, MetaEventType.LIFECYCLE)
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["sub_type"] = self.sub_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "MetaEvent":
        return cls(json_dict["time"], json_dict["self_id"], cls.LifeCycleType(json_dict["sub_type"]))
