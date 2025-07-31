from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from async_event_bus import AbstractEvent


class Serializable(ABC):
    @abstractmethod
    def to_json(self) -> dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_json(cls, json_dict: dict) -> "Serializable":
        raise NotImplementedError


class PostType(Enum):
    META = "meta_event"
    MESSAGE = "message"
    MESSAGE_SENT = "message_sent"
    NOTICE = "notice"
    REQUEST = "request"


@dataclass
class BasicEvent(Serializable, AbstractEvent):
    time: int
    post_type: PostType
    self_id: int

    def to_json(self) -> dict:
        return {
            "time": self.time,
            "post_type": self.post_type.value,
            "self_id": self.self_id
        }

    @classmethod
    def from_json(cls, json_dict: dict) -> "BasicEvent":
        return cls(json_dict["time"], PostType(json_dict["post_type"]), json_dict["self_id"])
