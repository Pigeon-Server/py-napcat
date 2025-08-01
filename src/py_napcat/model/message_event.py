from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Optional, Type

from .basic_event import BasicEvent, PostType
from .element import Element
from .exception import ParameterError, ParseError, ParserRegisteredError, UnregisteredEventError
from .sender import FriendSender, GroupSender


class MessageType(Enum):
    GROUP = "group"
    PRIVATE = "private"


@BasicEvent.register_event_parser(PostType.MESSAGE)
@BasicEvent.register_event_parser(PostType.MESSAGE_SENT)
@dataclass(frozen=True)
class MessageEvent(BasicEvent, ABC):
    _event_parser_registry: ClassVar[dict[MessageType, Type["MessageEvent"]]] = {}
    message_type: MessageType
    message_id: int
    user_id: int
    font: int
    message: list[Element]
    raw_message: str

    def __post_init__(self) -> None:
        assert None not in [self.message_type, self.message_id, self.user_id, self.font, self.raw_message, self.message]
        assert isinstance(self.message_type, MessageType)
        assert isinstance(self.message_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.font, int)
        assert isinstance(self.raw_message, str)
        assert isinstance(self.message, list)

    @classmethod
    def from_json(cls, json_dict: dict) -> "MessageEvent":
        raise NotImplementedError

    @property
    def text(self) -> str:
        return " ".join([message.text for message in self.message])

    @property
    def is_group_message(self) -> bool:
        return self.message_type == MessageType.GROUP

    @property
    def is_private_message(self) -> bool:
        return self.message_type == MessageType.PRIVATE

    @classmethod
    def register_event_parser(cls, event: MessageType):
        def decorator(event_parser_class: Type["MessageEvent"]):
            if event in cls._event_parser_registry:
                raise ParserRegisteredError(f"Parser for {event} already registered")
            cls._event_parser_registry[event] = event_parser_class
            return event_parser_class

        return decorator

    @classmethod
    def parse_event(cls, data: dict) -> "BasicEvent":
        try:
            event_type = MessageType(data["message_type"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Unknown event type: {data["message_type"]}") from e
        if target_class := cls._event_parser_registry.get(event_type):
            try:
                return target_class.from_json(data)
            except Exception as e:
                raise ParseError(f"Failed to parse {event_type.value} event") from e

        raise UnregisteredEventError(f"No parser registered for event type: {event_type.value}")


@MessageEvent.register_event_parser(MessageType.GROUP)
@dataclass(frozen=True)
class GroupMessageEvent(MessageEvent):
    class GroupMessageType(Enum):
        NORMAL = "normal"
        ANONYMOUS = "anonymous"
        NOTICE = "notice"

    sub_type: GroupMessageType
    group_id: int
    sender: GroupSender

    def __post_init__(self) -> None:
        super().__post_init__()
        assert None not in [self.sub_type, self.group_id, self.sender]
        assert isinstance(self.sub_type, self.GroupMessageType)
        assert isinstance(self.group_id, int)
        assert isinstance(self.sender, GroupSender)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupMessageEvent":
        try:
            return cls(time=json_dict["time"],
                       post_type=PostType(json_dict["post_type"]),
                       self_id=json_dict["self_id"],
                       message_type=MessageType(json_dict["message_type"]),
                       message_id=json_dict["message_id"],
                       user_id=json_dict["user_id"],
                       font=json_dict["font"],
                       raw_message=json_dict["raw_message"],
                       message=[Element.parse_element(item) for item in json_dict["message"]],
                       sub_type=cls.GroupMessageType(json_dict["sub_type"]),
                       group_id=json_dict["group_id"],
                       sender=GroupSender.from_json(json_dict["sender"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid event type: {e}") from e

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}(time={self.time}, post_type={self.post_type}, self_id={self.self_id}, "
                f"message_type={self.message_type}, message_id={self.message_id}, user_id={self.user_id}, "
                f"font={self.font}, raw_message={self.raw_message}, message={self.message}, "
                f"sub_type={self.sub_type}, group_id={self.group_id}, sender={self.sender})")

    @property
    def is_anonymous_message(self) -> bool:
        return self.sub_type == self.GroupMessageType.ANONYMOUS

    @property
    def is_notice_message(self) -> bool:
        return self.sub_type == self.GroupMessageType.NOTICE

    @property
    def is_normal_message(self) -> bool:
        return self.sub_type == self.GroupMessageType.NORMAL


@MessageEvent.register_event_parser(MessageType.PRIVATE)
@dataclass(frozen=True)
class FriendMessageEvent(MessageEvent):
    class FriendMessageType(Enum):
        FRIEND = "friend"
        GROUP = "group"

    sub_type: FriendMessageType
    sender: FriendSender
    target_id: Optional[int]
    temp_source: Optional[int]

    def __post_init__(self) -> None:
        super().__post_init__()
        assert None not in [self.sub_type, self.sender]
        assert isinstance(self.sub_type, self.FriendMessageType)
        assert isinstance(self.sender, FriendSender)

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendMessageEvent":
        try:
            return cls(time=json_dict["time"],
                       post_type=PostType(json_dict["post_type"]),
                       self_id=json_dict["self_id"],
                       message_type=MessageType(json_dict["message_type"]),
                       message_id=json_dict["message_id"],
                       user_id=json_dict["user_id"],
                       font=json_dict["font"],
                       raw_message=json_dict["raw_message"],
                       message=[Element.parse_element(item) for item in json_dict["message"]],
                       sub_type=cls.FriendMessageType(json_dict["sub_type"]),
                       sender=FriendSender.from_json(json_dict["sender"]),
                       target_id=json_dict.get("target_id"),
                       temp_source=json_dict.get("temp_source"))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid event type: {e}") from e

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}(time={self.time}, post_type={self.post_type}, self_id={self.self_id}, "
                f"message_type={self.message_type}, message_id={self.message_id}, user_id={self.user_id}, "
                f"font={self.font}, raw_message={self.raw_message}, message={self.message}, "
                f"sub_type={self.sub_type}, sender={self.sender}, target_id={self.target_id}, "
                f"temp_source={self.temp_source})")

    @property
    def is_friend_message(self) -> bool:
        return self.sub_type == self.FriendMessageType.FRIEND

    @property
    def is_temporary_message(self) -> bool:
        return self.sub_type == self.FriendMessageType.GROUP
