from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .basic_event import BasicEvent, PostType, Serializable


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


@dataclass
class File(Serializable):
    id: int
    name: str
    size: int
    busid: int

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "busid": self.busid
        }

    @classmethod
    def from_json(cls, json_dict: dict) -> "File":
        return cls(json_dict["id"], json_dict["name"], json_dict["size"], json_dict["busid"])


class NoticeEvent(BasicEvent):
    notice_type: NoticeType

    def __init__(self, time: int, self_id: int, notice_type: NoticeType) -> None:
        super().__init__(time, PostType.NOTICE, self_id)
        self.notice_type = notice_type

    def to_json(self) -> dict:
        return {
            "time": self.time,
            "post_type": self.post_type.value,
            "self_id": self.self_id,
            "notice_type": self.notice_type.value
        }

    @classmethod
    def from_json(cls, json_dict: dict) -> "NoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], NoticeType(json_dict["notice_type"]))

    @staticmethod
    def parse_notice_event(data: dict) -> "NoticeEvent":
        match NoticeType(data["notice_type"]):
            case NoticeType.GROUP_UPLOAD:
                return GroupUploadNoticeEvent.from_json(data)
            case NoticeType.GROUP_ADMIN:
                return GroupAdminNoticeEvent.from_json(data)
            case NoticeType.GROUP_DECREASE:
                return GroupDecreaseNoticeEvent.from_json(data)
            case NoticeType.GROUP_INCREASE:
                return GroupIncreaseNoticeEvent.from_json(data)
            case NoticeType.GROUP_BAN:
                return GroupBanNoticeEvent.from_json(data)
            case NoticeType.GROUP_RECALL:
                return GroupRecallNoticeEvent.from_json(data)
            case NoticeType.GROUP_CARD:
                return GroupCardNoticeEvent.from_json(data)
            case NoticeType.GROUP_MSG_EMOJI_LIKE:
                return GroupMsgEmojiLikeNoticeEvent.from_json(data)
            case NoticeType.FRIEND_ADD:
                return FriendAddNoticeEvent.from_json(data)
            case NoticeType.FRIEND_RECALL:
                return FriendRecallNoticeEvent.from_json(data)
            case NoticeType.LUCKY_KING:
                return LuckyKingNoticeEvent.from_json(data)
            case NoticeType.ESSENCE:
                return EssenceNoticeEvent.from_json(data)
            case NoticeType.HONOR:
                return HonorNoticeEvent.from_json(data)
            case NoticeType.POKE:
                return PokeNoticeEvent.from_json(data)
            case _:
                raise ValueError(f"Unknown notice type {data['notice_type']}")


class GroupUploadNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    file_info: File

    def __init__(self, time: int, self_id: int, group_id: int, user_id: int, file_info: File) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_UPLOAD)
        self.group_id = group_id
        self.user_id = user_id
        self.file_info = file_info

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["user_id"] = self.user_id
        data["file"] = self.file_info.to_json()
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupUploadNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["user_id"], File.from_json(json_dict["file"]))


class GroupAdminNoticeEvent(NoticeEvent):
    class GroupAdminType(Enum):
        SET = "set"
        UNSET = "unset"

    group_id: int
    user_id: int
    sub_type: GroupAdminType

    def __init__(self, time: int, self_id: int, group_id: int, user_id: int, sub_type: GroupAdminType) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_ADMIN)
        self.group_id = group_id
        self.user_id = user_id
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["user_id"] = self.user_id
        data["sub_type"] = self.sub_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupAdminNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["user_id"], cls.GroupAdminType(json_dict["sub_type"]))


class GroupDecreaseNoticeEvent(NoticeEvent):
    class GroupDecreaseType(Enum):
        LEAVE = "leave"
        KICK = "kick"
        KICK_ME = "kick_me"

    group_id: int
    operator_id: int
    user_id: int
    sub_type: GroupDecreaseType

    def __init__(self, time: int, self_id: int, group_id: int, operator_id: int, user_id: int,
                 sub_type: GroupDecreaseType) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_DECREASE)
        self.group_id = group_id
        self.operator_id = operator_id
        self.user_id = user_id
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["operator_id"] = self.operator_id
        data["user_id"] = self.user_id
        data["sub_type"] = self.sub_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupDecreaseNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["operator_id"], json_dict["user_id"], cls.GroupDecreaseType(json_dict["sub_type"]))


class GroupIncreaseNoticeEvent(NoticeEvent):
    class GroupIncreaseType(Enum):
        APPROVE = "approve"
        INVITE = "invite"

    group_id: int
    operator_id: int
    user_id: int
    sub_type: GroupIncreaseType

    def __init__(self, time: int, self_id: int, group_id: int, operator_id: int, user_id: int,
                 sub_type: GroupIncreaseType) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_INCREASE)
        self.group_id = group_id
        self.operator_id = operator_id
        self.user_id = user_id
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["operator_id"] = self.operator_id
        data["user_id"] = self.user_id
        data["sub_type"] = self.sub_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupIncreaseNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["operator_id"], json_dict["user_id"], cls.GroupIncreaseType(json_dict["sub_type"]))


class GroupBanNoticeEvent(NoticeEvent):
    class GroupBanType(Enum):
        BAN = "ban"
        LIFT_BAN = "lift_ban"

    group_id: int
    operator_id: int
    user_id: int
    duration: int
    sub_type: GroupBanType

    def __init__(self, time: int, self_id: int, group_id: int, operator_id: int, user_id: int, duration: int,
                 sub_type: GroupBanType) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_BAN)
        self.group_id = group_id
        self.operator_id = operator_id
        self.user_id = user_id
        self.duration = duration
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["operator_id"] = self.operator_id
        data["user_id"] = self.user_id
        data["duration"] = self.duration
        data["sub_type"] = self.sub_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupBanNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["operator_id"], json_dict["user_id"], json_dict["duration"],
                   cls.GroupBanType(json_dict["sub_type"]))


class GroupRecallNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    operator_id: int
    message_id: int

    def __init__(self, time: int, self_id: int, group_id: int, user_id: int, operator_id: int, message_id: int) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_RECALL)
        self.group_id = group_id
        self.user_id = user_id
        self.operator_id = operator_id
        self.message_id = message_id

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["user_id"] = self.user_id
        data["operator_id"] = self.operator_id
        data["message_id"] = self.message_id
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupRecallNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["user_id"], json_dict["operator_id"], json_dict["message_id"])


class GroupCardNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    card_new: str
    card_old: str

    def __init__(self, time: int, self_id: int, group_id: int, user_id: int, card_new: str, card_old: str) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_CARD)
        self.group_id = group_id
        self.user_id = user_id
        self.card_new = card_new
        self.card_old = card_old

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["user_id"] = self.user_id
        data["card_new"] = self.card_new
        data["card_old"] = self.card_old
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupCardNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["user_id"], json_dict["card_new"], json_dict["card_old"])


class GroupMsgEmojiLikeNoticeEvent(NoticeEvent):
    group_id: int
    user_id: Optional[int]
    operator_id: Optional[int]
    message_id: int
    likes: Optional[int]
    code: Optional[int]
    count: int

    def __init__(self, time: int, self_id: int, group_id: int,
                 message_id: int, count: int,
                 user_id: Optional[int] = None, operator_id: Optional[int] = None,
                 likes: Optional[int] = None, code: Optional[int] = None) -> None:
        super().__init__(time, self_id, NoticeType.GROUP_MSG_EMOJI_LIKE)
        self.group_id = group_id
        self.user_id = user_id
        self.operator_id = operator_id
        self.message_id = message_id
        self.likes = likes
        self.code = code
        self.count = count

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["message_id"] = self.message_id
        data["count"] = self.count
        if self.user_id is not None:
            data["user_id"] = self.user_id
        if self.operator_id is not None:
            data["operator_id"] = self.operator_id
        if self.likes is not None:
            data["likes"] = self.likes
        if self.code is not None:
            data["code"] = self.code
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupMsgEmojiLikeNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["message_id"], json_dict["count"],
                   json_dict.get("user_id"), json_dict.get("operator_id"),
                   json_dict.get("likes"), json_dict.get("code"))


class FriendAddNoticeEvent(NoticeEvent):
    user_id: int

    def __init__(self, time: int, self_id: int, user_id: int) -> None:
        super().__init__(time, self_id, NoticeType.FRIEND_ADD)
        self.user_id = user_id

    def to_json(self) -> dict:
        data = super().to_json()
        data["user_id"] = self.user_id
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendAddNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["user_id"])


class FriendRecallNoticeEvent(NoticeEvent):
    user_id: int
    message_id: int

    def __init__(self, time: int, self_id: int, user_id: int, message_id: int) -> None:
        super().__init__(time, self_id, NoticeType.FRIEND_RECALL)
        self.user_id = user_id
        self.message_id = message_id

    def to_json(self) -> dict:
        data = super().to_json()
        data["user_id"] = self.user_id
        data["message_id"] = self.message_id
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendRecallNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"],
                   json_dict["user_id"], json_dict["message_id"])


class LuckyKingNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    target_id: int
    sub_type = "lucky_king"

    def __init__(self, time: int, self_id: int, group_id: int, user_id: int, target_id: int) -> None:
        super().__init__(time, self_id, NoticeType.LUCKY_KING)
        self.group_id = group_id
        self.user_id = user_id
        self.target_id = target_id

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["user_id"] = self.user_id
        data["target_id"] = self.target_id
        data["sub_type"] = self.sub_type
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "LuckyKingNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["user_id"], json_dict["target_id"])


class EssenceNoticeEvent(NoticeEvent):
    class EssenceType(Enum):
        ADD = "add"
        DELETE = "delete"

    group_id: int
    message_id: int
    sender_id: int
    operator_id: int
    sub_type: EssenceType

    def __init__(self, time: int, self_id: int, group_id: int, message_id: int,
                 sender_id: int, operator_id: int, sub_type: EssenceType) -> None:
        super().__init__(time, self_id, NoticeType.ESSENCE)
        self.group_id = group_id
        self.message_id = message_id
        self.sender_id = sender_id
        self.operator_id = operator_id
        self.sub_type = sub_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["message_id"] = self.message_id
        data["sender_id"] = self.sender_id
        data["operator_id"] = self.operator_id
        data["sub_type"] = self.sub_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "EssenceNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["message_id"], json_dict["sender_id"], json_dict["operator_id"],
                   cls.EssenceType(json_dict["sub_type"]))


class HonorNoticeEvent(NoticeEvent):
    group_id: int
    user_id: int
    honor_type: str
    sub_type = "honor"

    def __init__(self, time: int, self_id: int, group_id: int, user_id: int, honor_type: str) -> None:
        super().__init__(time, self_id, NoticeType.HONOR)
        self.group_id = group_id
        self.user_id = user_id
        self.honor_type = honor_type

    def to_json(self) -> dict:
        data = super().to_json()
        data["group_id"] = self.group_id
        data["user_id"] = self.user_id
        data["honor_type"] = self.honor_type
        data["sub_type"] = self.sub_type
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "HonorNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["group_id"],
                   json_dict["user_id"], json_dict["honor_type"])


class PokeNoticeEvent(NoticeEvent):
    group_id: Optional[int]
    user_id: int
    target_id: int
    sub_type = "poke"

    def __init__(self, time: int, self_id: int, user_id: int, target_id: int, group_id: Optional[int] = None) -> None:
        super().__init__(time, self_id, NoticeType.POKE)
        self.group_id = group_id
        self.user_id = user_id
        self.target_id = target_id

    def to_json(self) -> dict:
        data = super().to_json()
        data["user_id"] = self.user_id
        data["target_id"] = self.target_id
        data["sub_type"] = self.sub_type
        if self.group_id is not None:
            data["group_id"] = self.group_id
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "PokeNoticeEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["user_id"],
                   json_dict["target_id"], json_dict.get("group_id"))
