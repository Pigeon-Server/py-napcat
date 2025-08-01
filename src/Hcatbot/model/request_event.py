from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Type

from .basic_event import BasicEvent, PostType
from .exception import ParameterError, ParseError, ParserRegisteredError, UnregisteredEventError


class RequestType(Enum):
    FRIEND = "friend"
    GROUP = "group"


@BasicEvent.register_event_parser(PostType.REQUEST)
@dataclass(frozen=True)
class RequestEvent(BasicEvent, ABC):
    _event_parser_registry: ClassVar[dict[RequestType, Type["RequestEvent"]]] = {}
    request_type: RequestType
    flag: str
    user_id: int
    comment: str

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.request_type, RequestType)
        assert isinstance(self.flag, str)
        assert isinstance(self.user_id, int)
        assert isinstance(self.comment, str)

    @classmethod
    def register_event_parser(cls, event: RequestType):
        def decorator(event_parser_class: Type["RequestEvent"]):
            if event in cls._event_parser_registry:
                raise ParserRegisteredError(f"Parser for {event} already registered")
            cls._event_parser_registry[event] = event_parser_class
            return event_parser_class

        return decorator

    @classmethod
    def parse_event(cls, data: dict) -> "BasicEvent":
        try:
            event_type = RequestType(data["request_type"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Unknown event type: {data["request_type"]}") from e
        if target_class := cls._event_parser_registry.get(event_type):
            try:
                return target_class.from_json(data)
            except Exception as e:
                raise ParseError(f"Failed to parse {event_type.value} event") from e

        raise UnregisteredEventError(f"No parser registered for event type: {event_type.value}")


@RequestEvent.register_event_parser(RequestType.FRIEND)
@dataclass(frozen=True)
class FriendRequestEvent(RequestEvent):
    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendRequestEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.REQUEST,
                       request_type=RequestType.FRIEND,
                       flag=json_dict["flag"],
                       user_id=json_dict["user_id"],
                       comment=json_dict["comment"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@RequestEvent.register_event_parser(RequestType.GROUP)
@dataclass(frozen=True)
class GroupRequestEvent(RequestEvent):
    class GroupRequestType(Enum):
        ADD = "add"
        INVITE = "invite"

    sub_request_type: GroupRequestType
    group_id: int

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.sub_request_type, self.GroupRequestType)
        assert isinstance(self.group_id, int)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupRequestEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.REQUEST,
                       request_type=RequestType.GROUP,
                       flag=json_dict["flag"],
                       user_id=json_dict["user_id"],
                       comment=json_dict["comment"],
                       sub_request_type=cls.GroupRequestType(json_dict["sub_type"]),
                       group_id=json_dict["group_id"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid sub type: {e}") from e
