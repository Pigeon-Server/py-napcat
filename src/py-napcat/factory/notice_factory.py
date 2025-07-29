from ..model import NoticeEvent, NoticeType, GroupUploadNoticeEvent, GroupAdminNoticeEvent, GroupDecreaseNoticeEvent, \
    GroupIncreaseNoticeEvent, GroupBanNoticeEvent, GroupRecallNoticeEvent, GroupCardNoticeEvent, \
    GroupMsgEmojiLikeNoticeEvent, FriendAddNoticeEvent, FriendRecallNoticeEvent, LuckyKingNoticeEvent, \
    EssenceNoticeEvent, HonorNoticeEvent, PokeNoticeEvent


class NoticeFactory:
    @staticmethod
    def parse_notice_event(data: dict) -> NoticeEvent:
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
