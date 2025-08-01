from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Optional, Type

from .basic_event import BasicEvent, PostType, Serializable
from .exception import NonSerializableError, ParameterError, ParseError, ParserRegisteredError, UnregisteredEventError


class NoticeType(Enum):
    GROUP_UPLOAD = "group_upload"  # 群文件上传
    GROUP_ADMIN = "group_admin"  # 群管理员变动
    GROUP_DECREASE = "group_decrease"  # 群成员减少
    GROUP_INCREASE = "group_increase"  # 群成员增加
    GROUP_BAN = "group_ban"  # 群禁言
    GROUP_RECALL = "group_recall"  # 群消息撤回
    GROUP_CARD = "group_card"  # 群名片变更
    GROUP_MSG_EMOJI_LIKE = "group_msg_emoji_like"  # 群表情回应
    FRIEND_ADD = "friend_add"  # 新添加好友
    FRIEND_RECALL = "friend_recall"  # 好友消息撤回
    LUCKY_KING = "lucky_king"  # 运气王
    ESSENCE = "essence"  # 群精华
    HONOR = "honor"  # 荣誉变更
    POKE = "poke"  # 戳一戳


@dataclass(frozen=True)
class NoticeEvent(BasicEvent, ABC):
    _event_parser_registry: ClassVar[dict[NoticeType, Type["NoticeEvent"]]] = {}
    notice_type: NoticeType

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.notice_type, NoticeType)

    @classmethod
    def register_event_parser(cls, event: NoticeType):
        def decorator(event_parser_class: Type["NoticeEvent"]):
            if event in cls._event_parser_registry:
                raise ParserRegisteredError(f"Parser for {event} already registered")
            cls._event_parser_registry[event] = event_parser_class
            return event_parser_class

        return decorator

    @classmethod
    def parse_event(cls, data: dict) -> "BasicEvent":
        try:
            event_type = NoticeType(data["notice_type"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Unknown event type: {data["notice_type"]}") from e
        if target_class := cls._event_parser_registry.get(event_type):
            try:
                return target_class.from_json(data)
            except Exception as e:
                raise ParseError(f"Failed to parse {event_type.value} event") from e

        raise UnregisteredEventError(f"No parser registered for event type: {event_type.value}")


@NoticeEvent.register_event_parser(NoticeType.GROUP_UPLOAD)
@dataclass(frozen=True)
class GroupUploadNoticeEvent(NoticeEvent):
    @dataclass(frozen=True)
    class File(Serializable):
        id: int
        name: str
        size: int
        busid: int

        def __post_init__(self) -> None:
            assert isinstance(self.id, int)
            assert isinstance(self.name, str)
            assert isinstance(self.size, int)
            assert isinstance(self.busid, int)

        def to_json(self) -> dict:
            raise NonSerializableError(f"This class is non-serializable")

        @classmethod
        def from_json(cls, json_dict: dict) -> "GroupUploadNoticeEvent.File":
            try:
                return cls(id=json_dict["id"],
                           name=json_dict["name"],
                           size=json_dict["size"],
                           busid=json_dict["busid"])
            except KeyError as e:
                raise ParameterError(f"Missing required field: {e}") from e

    group_id: int
    user_id: int
    file_info: File

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.file_info, self.File)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupUploadNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_UPLOAD,
                       group_id=json_dict["group_id"],
                       user_id=json_dict["user_id"],
                       file_info=cls.File.from_json(json_dict["file"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.GROUP_ADMIN)
@dataclass(frozen=True)
class GroupAdminNoticeEvent(NoticeEvent):
    class GroupAdminType(Enum):
        SET = "set"
        UNSET = "unset"

    group_id: int
    user_id: int
    sub_type: GroupAdminType

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.sub_type, self.GroupAdminType)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupAdminNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_ADMIN,
                       group_id=json_dict["group_id"],
                       user_id=json_dict["user_id"],
                       sub_type=cls.GroupAdminType(json_dict["sub_type"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid sub type: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.GROUP_DECREASE)
@dataclass(frozen=True)
class GroupDecreaseNoticeEvent(NoticeEvent):
    class GroupDecreaseType(Enum):
        LEAVE = "leave"
        KICK = "kick"
        KICK_ME = "kick_me"

    group_id: int
    operator_id: int
    user_id: int
    sub_type: GroupDecreaseType

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.operator_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.sub_type, self.GroupDecreaseType)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupDecreaseNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_DECREASE,
                       group_id=json_dict["group_id"],
                       operator_id=json_dict["operator_id"],
                       user_id=json_dict["user_id"],
                       sub_type=cls.GroupDecreaseType(json_dict["sub_type"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid sub type: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.GROUP_INCREASE)
@dataclass(frozen=True)
class GroupIncreaseNoticeEvent(NoticeEvent):
    class GroupIncreaseType(Enum):
        APPROVE = "approve"
        INVITE = "invite"

    group_id: int
    operator_id: int
    user_id: int
    sub_type: GroupIncreaseType

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.operator_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.sub_type, self.GroupIncreaseType)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupIncreaseNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_INCREASE,
                       group_id=json_dict["group_id"],
                       operator_id=json_dict["operator_id"],
                       user_id=json_dict["user_id"],
                       sub_type=cls.GroupIncreaseType(json_dict["sub_type"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid sub type: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.GROUP_BAN)
@dataclass(frozen=True)
class GroupBanNoticeEvent(NoticeEvent):
    class GroupBanType(Enum):
        BAN = "ban"
        LIFT_BAN = "lift_ban"

    group_id: int
    operator_id: int
    user_id: int
    duration: int
    sub_type: GroupBanType

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.operator_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.duration, int)
        assert isinstance(self.sub_type, self.GroupBanType)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupBanNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_BAN,
                       group_id=json_dict["group_id"],
                       operator_id=json_dict["operator_id"],
                       user_id=json_dict["user_id"],
                       duration=json_dict["duration"],
                       sub_type=cls.GroupBanType(json_dict["sub_type"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid sub type: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.GROUP_RECALL)
@dataclass(frozen=True)
class GroupRecallNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    operator_id: int
    message_id: int

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.operator_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.message_id, int)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupRecallNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_RECALL,
                       group_id=json_dict["group_id"],
                       user_id=json_dict["user_id"],
                       operator_id=json_dict["operator_id"],
                       message_id=json_dict["message_id"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.GROUP_CARD)
@dataclass(frozen=True)
class GroupCardNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    card_new: str
    card_old: str

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.card_new, str)
        assert isinstance(self.card_old, str)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupCardNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_CARD,
                       group_id=json_dict["group_id"],
                       user_id=json_dict["user_id"],
                       card_new=json_dict["card_new"],
                       card_old=json_dict["card_old"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.GROUP_MSG_EMOJI_LIKE)
@dataclass(frozen=True)
class GroupMsgEmojiLikeNoticeEvent(NoticeEvent):
    group_id: int
    user_id: Optional[int]
    operator_id: Optional[int]
    message_id: int
    likes: Optional[int]
    code: Optional[int]
    count: int

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.message_id, int)
        assert isinstance(self.count, int)

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupMsgEmojiLikeNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.GROUP_MSG_EMOJI_LIKE,
                       group_id=json_dict["group_id"],
                       message_id=json_dict["message_id"],
                       count=json_dict["count"],
                       user_id=json_dict.get("user_id"),
                       operator_id=json_dict.get("operator_id"),
                       likes=json_dict.get("likes"),
                       code=json_dict.get("code"))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.FRIEND_ADD)
@dataclass(frozen=True)
class FriendAddNoticeEvent(NoticeEvent):
    user_id: int

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.user_id, int)

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendAddNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.FRIEND_ADD,
                       user_id=json_dict["user_id"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.FRIEND_RECALL)
@dataclass(frozen=True)
class FriendRecallNoticeEvent(NoticeEvent):
    user_id: int
    message_id: int

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.user_id, int)
        assert isinstance(self.message_id, int)

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendRecallNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.FRIEND_RECALL,
                       user_id=json_dict["user_id"],
                       message_id=json_dict["message_id"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.LUCKY_KING)
@dataclass(frozen=True)
class LuckyKingNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    target_id: int
    sub_type = "lucky_king"

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.target_id, int)

    @classmethod
    def from_json(cls, json_dict: dict) -> "LuckyKingNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.LUCKY_KING,
                       group_id=json_dict["group_id"],
                       user_id=json_dict["user_id"],
                       target_id=json_dict["target_id"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.ESSENCE)
@dataclass(frozen=True)
class EssenceNoticeEvent(NoticeEvent):
    class EssenceType(Enum):
        ADD = "add"
        DELETE = "delete"

    group_id: int
    message_id: int
    sender_id: int
    operator_id: int
    sub_type: EssenceType

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.message_id, int)
        assert isinstance(self.sender_id, int)
        assert isinstance(self.operator_id, int)
        assert isinstance(self.sub_type, self.EssenceType)

    @classmethod
    def from_json(cls, json_dict: dict) -> "EssenceNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.ESSENCE,
                       group_id=json_dict["group_id"],
                       message_id=json_dict["message_id"],
                       sender_id=json_dict["sender_id"],
                       operator_id=json_dict["operator_id"],
                       sub_type=cls.EssenceType(json_dict["sub_type"]))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid sub type: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.HONOR)
@dataclass(frozen=True)
class HonorNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    honor_type: str
    sub_type = "honor"

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.group_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self.honor_type, str)

    @classmethod
    def from_json(cls, json_dict: dict) -> "HonorNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.HONOR,
                       group_id=json_dict["group_id"],
                       user_id=json_dict["user_id"],
                       honor_type=json_dict["honor_type"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@NoticeEvent.register_event_parser(NoticeType.POKE)
@dataclass(frozen=True)
class PokeNoticeEvent(NoticeEvent):
    group_id: Optional[int]
    user_id: int
    target_id: int
    sub_type = "poke"

    def __post_init__(self) -> None:
        super().__post_init__()
        assert isinstance(self.user_id, int)
        assert isinstance(self.target_id, int)

    @classmethod
    def from_json(cls, json_dict: dict) -> "PokeNoticeEvent":
        try:
            return cls(time=json_dict["time"],
                       self_id=json_dict["self_id"],
                       post_type=PostType.NOTICE,
                       notice_type=NoticeType.POKE,
                       user_id=json_dict["user_id"],
                       target_id=json_dict["target_id"],
                       group_id=json_dict.get("group_id"))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid event type: {e}") from e
