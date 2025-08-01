from typing import Type

import pytest

from py_napcat.model.meta_event import HeartbeatEvent, LifeCycleEvent, MetaEvent


@pytest.mark.parametrize("data, expected_class", [
    ({"time": 111, "self_id": 111, "post_type": "meta_event", "meta_event_type": "heartbeat",
      "status": {"online": True, "good": True}, "interval": 300000}, HeartbeatEvent),
    ({"time": 111, "self_id": 111, "post_type": "meta_event", "meta_event_type": "lifecycle", "sub_type": "connect"},
     LifeCycleEvent)
])
def test_meta_event_parser(data: dict, expected_class: Type[MetaEvent]) -> None:
    """
    测试对元数据事件的解析
    :param data: 等待解析的数据
    :param expected_class: 期望被解析出来的类型
    """
    meta_event = MetaEvent.parse_event(data)
    assert isinstance(meta_event, expected_class)
