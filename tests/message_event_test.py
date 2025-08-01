from typing import Type

import pytest

from Hcatbot import BasicEvent
from Hcatbot.model.message_event import FriendMessageEvent, GroupMessageEvent, MessageEvent


@pytest.mark.parametrize("data, expected_class, expected_message", [
    ({"self_id": 111, "user_id": 111, "time": 111, "message_id": 111, "message_seq": 111, "real_id": 111,
      "real_seq": "111", "message_type": "group",
      "sender": {"user_id": 111, "nickname": "111", "card": "HAZ0921/5740/1928832/mc就很难", "role": "member"},
      "raw_message": "[CQ:reply,id=576826342]好看", "font": 14, "sub_type": "normal",
      "message": [{"type": "reply", "data": {"id": "576826342"}}, {"type": "text", "data": {"text": "好看"}}],
      "message_format": "array", "post_type": "message", "group_id": 111}, GroupMessageEvent, "[回复](576826342) 好看"),
    ({"self_id": 111, "user_id": 111, "time": 111, "message_id": 111, "message_seq": 111, "real_id": 111,
      "real_seq": "111", "message_type": "group",
      "sender": {"user_id": 111, "nickname": "111", "card": "HAZ0921/5740/1928832/mc就很难", "role": "member"},
      "raw_message": "6", "font": 14, "sub_type": "normal", "message": [{"type": "text", "data": {"text": "6"}}],
      "message_format": "array", "post_type": "message", "group_id": 111}, GroupMessageEvent, "6"),
    ({"self_id": 111, "user_id": 111, "time": 111, "message_id": 111, "message_seq": 111, "real_id": 111,
      "real_seq": "111", "message_type": "private", "sender": {"user_id": 111, "nickname": "半旧无妨", "card": ""},
      "raw_message": "111", "font": 14, "sub_type": "friend", "message": [{"type": "image", "data": {
            "summary": "[动画表情]", "file": "123.gif", "sub_type": 2, "url": "111", "file_size": "111"}}],
      "message_format": "array", "post_type": "message", "target_id": 111}, FriendMessageEvent, "[动画表情]"),
    ({"self_id": 111, "user_id": 111, "time": 111, "message_id": 111, "message_seq": 111, "real_id": 111,
      "real_seq": "23", "message_type": "private", "sender": {"user_id": 111, "nickname": "半旧无妨", "card": ""},
      "raw_message": "[CQ:face,id=368,raw=&#91;object Object&#93;,chainCount=0]", "font": 14, "sub_type": "friend",
      "message": [{"type": "face", "data": {"id": "368", "raw": {"faceIndex": 368, "faceText": "/奥特笑哭"}}}],
      "message_format": "array", "post_type": "message", "target_id": 111}, FriendMessageEvent, "/奥特笑哭")
])
def test_message_event_parser(data: dict, expected_class: Type[MessageEvent], expected_message: str) -> None:
    """
    测试消息事件解析
    :param data: 等待解析的数据
    :param expected_class: 期望被解析出来的类型
    :param expected_message: text属性的期望值
    """
    element = BasicEvent.parse_event(data)
    assert isinstance(element, expected_class)
    assert element.text == expected_message
