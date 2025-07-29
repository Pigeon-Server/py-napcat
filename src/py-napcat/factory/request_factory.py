from ..model import RequestEvent, RequestType, FriendRequestEvent, GroupRequestEvent


class RequestFactory:
    @staticmethod
    def parse_request_event(data: dict) -> RequestEvent:
        match RequestType(data["request_type"]):
            case RequestType.FRIEND:
                return FriendRequestEvent.from_json(data)
            case RequestType.GROUP:
                return GroupRequestEvent.from_json(data)
            case _:
                raise ValueError(f"Unknown request type {data['request_type']}")
