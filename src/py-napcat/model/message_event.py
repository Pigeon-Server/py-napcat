from enum import Enum
from typing import Optional

from .basic_event import PostType, BasicEvent
from .element import Element
from .sender import GroupSender, FriendSender
from .message_factory import MessageFactory


class MessageType(Enum):
    GROUP = "group"
    PRIVATE = "private"


class MessageEvent(BasicEvent):
    message_type: MessageType
    message_id: int
    user_id: int
    font: int
    message: list[Element]
    raw_message: str

    def __init__(self, time: int, post_type: PostType, self_id: int, message_type: MessageType, message_id: int,
                 user_id: int, font: int, raw_message: str, message: list[Element]) -> None:
        super().__init__(time, post_type, self_id)
        self.message_type = message_type
        self.message_id = message_id
        self.user_id = user_id
        self.font = font
        self.message = message
        self.raw_message = raw_message

    def to_json(self) -> dict:
        data = super().to_json()
        data["message_type"] = self.message_type.value
        data["message_id"] = self.message_id
        data["user_id"] = self.user_id
        data["font"] = self.font
        data["raw_message"] = self.raw_message
        data["message"] = [item.to_json() for item in self.message]
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "MessageEvent":
        return cls(json_dict["time"], PostType(json_dict["post_type"]), json_dict["self_id"],
                   MessageType(json_dict["message_type"]), json_dict["message_id"], json_dict["user_id"],
                   json_dict["font"], json_dict["raw_message"],
                   [MessageFactory.parse_element(item) for item in json_dict["message"]])


class GroupMessageEvent(MessageEvent):
    class GroupMessageType(Enum):
        NORMAL = "normal"
        ANONYMOUS = "anonymous"
        NOTICE = "notice"

    sub_type: GroupMessageType
    group_id: int
    sender: GroupSender

    def __init__(self, time: int, post_type: PostType, self_id: int, message_id: int,
                 user_id: int, font: int, raw_message: str, message: list[Element],
                 sub_type: GroupMessageType, group_id: int, sender: GroupSender) -> None:
        super().__init__(time, post_type, self_id, MessageType.GROUP,
                         message_id, user_id, font, raw_message, message)
        self.group_id = group_id
        self.sender = sender
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["sender"] = self.sender.to_json()
        data["sub_type"] = self.sub_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupMessageEvent":
        return cls(json_dict["time"], PostType(json_dict["post_type"]), json_dict["self_id"],
                   json_dict["message_id"], json_dict["user_id"], json_dict["font"],
                   json_dict["raw_message"], [MessageFactory.parse_element(item) for item in json_dict["message"]],
                   cls.GroupMessageType(json_dict["sub_type"]), json_dict["group_id"],
                   GroupSender.from_json(json_dict["sender"]))


class FriendMessageEvent(MessageEvent):
    class FriendMessageType(Enum):
        FRIEND = "friend"
        GROUP = "group"

    sub_type: FriendMessageType
    sender: FriendSender
    target_id: Optional[int]
    temp_source: Optional[int]

    def __init__(self, time: int, post_type: PostType, self_id: int, message_id: int,
                 user_id: int, font: int, raw_message: str, message: list[Element],
                 sub_type: FriendMessageType, sender: FriendSender, target_id: Optional[int] = None,
                 temp_source: Optional[int] = None) -> None:
        super().__init__(time, post_type, self_id, MessageType.PRIVATE, message_id,
                         user_id, font, raw_message, message)
        self.target_id = target_id
        self.temp_source = temp_source
        self.sender = sender
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["sender"] = self.sender.to_json()
        data["sub_type"] = self.sub_type.value
        if self.target_id is not None:
            data["target_id"] = self.target_id
        if self.temp_source is not None:
            data["temp_source"] = self.temp_source
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendMessageEvent":
        return cls(json_dict["time"], PostType(json_dict["post_type"]), json_dict["self_id"],
                   json_dict["message_id"], json_dict["user_id"], json_dict["font"],
                   json_dict["raw_message"], [MessageFactory.parse_element(item) for item in json_dict["message"]],
                   cls.FriendMessageType(json_dict["sub_type"]), FriendSender.from_json(json_dict["sender"]),
                   json_dict.get("target_id"), json_dict.get("temp_source"))
