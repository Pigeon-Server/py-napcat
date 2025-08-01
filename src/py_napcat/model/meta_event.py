from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Type

from .basic_event import Serializable, PostType, BasicEvent
from .exception import NonSerializableError, ParameterError, ParseError, ParserRegisteredError, UnregisteredEventError


class MetaType(Enum):
    HEARTBEAT = "heartbeat"
    LIFECYCLE = "lifecycle"


@BasicEvent.register_event_parser(PostType.META)
@dataclass(frozen=True)
class MetaEvent(BasicEvent, ABC):
    _event_parser_registry: ClassVar[dict[MetaType, Type["MetaEvent"]]] = {}
    meta_event_type: MetaType

    @classmethod
    def register_event_parser(cls, event: MetaType):
        def decorator(event_parser_class: Type["MetaEvent"]):
            if event in cls._event_parser_registry:
                raise ParserRegisteredError(f"Parser for {event} already registered")
            cls._event_parser_registry[event] = event_parser_class
            return event_parser_class

        return decorator

    @classmethod
    def parse_event(cls, data: dict) -> "BasicEvent":
        try:
            event_type = MetaType(data["meta_event_type"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Unknown event type: {data["meta_event_type"]}") from e
        if target_class := cls._event_parser_registry.get(event_type):
            try:
                return target_class.from_json(data)
            except Exception as e:
                raise ParseError(f"Failed to parse {event_type.value} event") from e

        raise UnregisteredEventError(f"No parser registered for event type: {event_type.value}")


@MetaEvent.register_event_parser(MetaType.HEARTBEAT)
@dataclass(frozen=True)
class HeartbeatEvent(MetaEvent):
    @dataclass(frozen=True)
    class HeartbeatStatus(Serializable):
        online: bool
        good: bool

        def __post_init__(self) -> None:
            assert self.online is not None
            assert self.good is not None
            assert isinstance(self.online, bool)
            assert isinstance(self.good, bool)

        def to_json(self) -> dict:
            raise NonSerializableError(f"This class is non-serializable")

        @classmethod
        def from_json(cls, json_dict: dict) -> "HeartbeatEvent.HeartbeatStatus":
            try:
                return cls(online=json_dict["online"],
                           good=json_dict["good"])
            except KeyError as e:
                raise ParameterError(f"Missing required field: {e}") from e

    status: HeartbeatStatus
    interval: int

    @classmethod
    def from_json(cls, json_dict: dict) -> "MetaEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       meta_event_type=MetaType.HEARTBEAT,
                       post_type=PostType.META,
                       status=cls.HeartbeatStatus.from_json(json_dict["status"]),
                       interval=json_dict["interval"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid event type: {e}") from e


@MetaEvent.register_event_parser(MetaType.LIFECYCLE)
@dataclass(frozen=True)
class LifeCycleEvent(MetaEvent):
    class LifeCycleType(Enum):
        ENABLE = "enable"
        DISABLE = "disable"
        CONNECT = "connect"

    sub_type: LifeCycleType

    @classmethod
    def from_json(cls, json_dict: dict) -> "MetaEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       meta_event_type=MetaType.LIFECYCLE,
                       post_type=PostType.META,
                       sub_type=cls.LifeCycleType(json_dict["sub_type"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid event type: {e}") from e
