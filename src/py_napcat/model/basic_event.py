from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Type

from async_event_bus import AbstractEvent, EventBus

from .exception import EventReceivedOnlyError, ParameterError, ParseError, ParserRegisteredError, UnregisteredEventError

event_bus: EventBus = EventBus()


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


@dataclass(frozen=True)
class BasicEvent(Serializable, AbstractEvent):
    _event_parser_registry: ClassVar[dict[PostType, Type["BasicEvent"]]] = {}
    time: int
    post_type: PostType
    self_id: int

    def __post_init__(self):
        assert None not in [self.time, self.post_type, self.self_id]
        assert isinstance(self.post_type, PostType)
        assert isinstance(self.self_id, int)
        assert isinstance(self.time, int)

    def to_json(self) -> dict:
        raise EventReceivedOnlyError(f"Events can only be accepted and not sent")

    @classmethod
    def from_json(cls, json_dict: dict) -> "BasicEvent":
        try:
            return cls(time=json_dict["time"],
                       post_type=PostType(json_dict["post_type"]),
                       self_id=json_dict["self_id"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid event type: {e}") from e

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(time={self.time}, post_type={self.post_type}, self_id={self.self_id})"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def register_event_parser(cls, event: PostType):
        def decorator(event_parser_class: Type["BasicEvent"]):
            if event in cls._event_parser_registry:
                raise ParserRegisteredError(f"Parser for {event} already registered")
            cls._event_parser_registry[event] = event_parser_class
            return event_parser_class

        return decorator

    @classmethod
    def parse_event(cls, data: dict) -> "BasicEvent":
        try:
            event_type = PostType(data["post_type"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Unknown event type: {data["post_type"]}") from e
        if target_class := cls._event_parser_registry.get(event_type):
            try:
                return target_class.parse_event(data)
            except Exception as e:
                raise ParseError(f"Failed to parse {event_type.value} event") from e

        raise UnregisteredEventError(f"No parser registered for event type: {event_type.value}")
