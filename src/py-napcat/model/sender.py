from enum import Enum
from typing import Optional

from .basic_event import Serializable


class UserSex(Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class UserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class FriendSender(Serializable):
    user_id: int
    nickname: str
    sex: UserSex
    group_id: Optional[int]

    def __init__(self, user_id: int, nickname: str, sex: UserSex, group_id: Optional[int] = None):
        self.user_id = user_id
        self.nickname = nickname
        self.sex = sex
        self.group_id = group_id

    def to_json(self) -> dict:
        data = {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "sex": self.sex.value
        }
        if self.group_id is not None:
            data["group_id"] = self.group_id
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendSender":
        return cls(json_dict["user_id"],
                   json_dict["nickname"],
                   UserSex(json_dict["sex"]),
                   json_dict.get("group_id"))


class GroupSender(Serializable):
    user_id: int
    nickname: str
    sex: UserSex
    role: UserRole
    card: Optional[str]

    def __init__(self, user_id: int, nickname: str, sex: UserSex, role: UserRole, card: Optional[str] = None):
        self.user_id = user_id
        self.nickname = nickname
        self.sex = sex
        self.role = role
        self.card = card

    def to_json(self) -> dict:
        data = {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "sex": self.sex.value,
            "role": self.role.value,
        }
        if self.card is not None:
            data["card"] = self.card
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupSender":
        return cls(json_dict["user_id"],
                   json_dict["nickname"],
                   UserSex(json_dict["sex"]),
                   UserRole(json_dict["role"]),
                   json_dict.get("card"))
