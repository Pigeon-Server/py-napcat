from enum import Enum

from .basic_event import BasicEvent, PostType


class RequestType(Enum):
    FRIEND = "friend"
    GROUP = "group"


class RequestEvent(BasicEvent):
    request_type: RequestType
    flag: str
    user_id: int
    comment: str

    def __init__(self, time: int, self_id: int, request_type: RequestType, flag: str, user_id: int,
                 comment: str) -> None:
        super().__init__(time, PostType.REQUEST, self_id)
        self.request_type = request_type
        self.flag = flag
        self.user_id = user_id
        self.comment = comment

    def to_json(self) -> dict:
        data = super().to_json()
        data["flag"] = self.flag
        data["user_id"] = self.user_id
        data["comment"] = self.comment
        data["request_type"] = self.request_type.value
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "RequestEvent":
        return cls(json_dict["time"], json_dict["self_id"], RequestType(json_dict["request_type"]),
                   json_dict["flag"], json_dict["user_id"], json_dict["comment"])


class FriendRequestEvent(RequestEvent):
    def __init__(self, time: int, self_id: int, flag: str, user_id: int, comment: str) -> None:
        super().__init__(time, self_id, RequestType.FRIEND, flag, user_id, comment)

    @classmethod
    def from_json(cls, json_dict: dict) -> "FriendRequestEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["flag"],
                   json_dict["user_id"], json_dict["comment"])


class GroupRequestEvent(RequestEvent):
    class GroupRequestType(Enum):
        ADD = "add"
        INVITE = "invite"

    sub_request_type: GroupRequestType
    group_id: int

    def __init__(self, time: int, self_id: int, flag: str, user_id: int, comment: str,
                 sub_request_type: GroupRequestType, group_id: int) -> None:
        super().__init__(time, self_id, RequestType.GROUP, flag, user_id, comment)
        self.sub_request_type = sub_request_type
        self.group_id = group_id

    def to_json(self) -> dict:
        data = super().to_json()
        data["sub_type"] = self.sub_request_type.value
        data["group_id"] = self.group_id
        return data

    @classmethod
    def from_json(cls, json_dict: dict) -> "GroupRequestEvent":
        return cls(json_dict["time"], json_dict["self_id"], json_dict["flag"],
                   json_dict["user_id"], json_dict["comment"],
                   cls.GroupRequestType(json_dict["sub_type"]), json_dict["group_id"])
