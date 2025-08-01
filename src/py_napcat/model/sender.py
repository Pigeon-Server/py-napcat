from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .basic_event import Serializable
from .exception import NonSerializableError, ParameterError


class UserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


@dataclass(frozen=True)
class FriendSender(Serializable):
    user_id: int
    nickname: str
    group_id: Optional[int]

    def to_json(self) -> dict:
        raise NonSerializableError(f"This class is non-serializable")

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendSender":
        try:
            return cls(user_id=json_dict["user_id"],
                       nickname=json_dict["nickname"],
                       group_id=json_dict.get("group_id"))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e


@dataclass(frozen=True)
class GroupSender(Serializable):
    user_id: int
    nickname: str
    role: UserRole
    card: Optional[str]

    def to_json(self) -> dict:
        raise NonSerializableError(f"This class is non-serializable")

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupSender":
        try:
            return cls(user_id=json_dict["user_id"],
                       nickname=json_dict["nickname"],
                       role=UserRole(json_dict["role"]),
                       card=json_dict.get("card"))
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Invalid event type: {e}") from e
