from typing import Type

from py_napcat import DiceElement, Element, FaceElement, ForwardElement, ImageElement, MFaceElement, PokeElement, \
    RPSElement, \
    ReplyElement, \
    TextElement


def test_element_parser():
    messages: list[tuple[dict, Type[Element], str]] = [
        (
            {
                "type": "image",
                "data": {"summary": "[饿了]", "file": "123.jpg", "sub_type": 7, "url": "123", "file_size": "17552"}
            },
            ImageElement,
            "[饿了]"
        ),
        ({"type": "reply", "data": {"id": "576826342"}}, ReplyElement, "[回复](576826342)"),
        ({"type": "text", "data": {"text": "好看"}}, TextElement, "好看"),
        (
            {"type": "face", "data": {"id": "298", "raw": {"faceIndex": 298, "faceText": "[元宝]", "faceType": 2}}},
            FaceElement,
            "[元宝]"
        ),
        (
            {
                "type": "image",
                "data": {"summary": "[动画表情]", "file": "123.jpg", "sub_type": 1, "url": "123", "file_size": "76620"}
            },
            ImageElement,
            "[动画表情]"
        ),
        ({"type": "poke", "data": {"type": "1", "id": "1"}}, PokeElement, "[戳一戳]"),
        ({"type": "forward", "data": {"id": "7533614539788225271"}}, ForwardElement, "[合并消息]"),
        ({"type": "rps", "data": {"result": "1"}}, RPSElement, "[石头剪刀布](CLOTH)"),
        ({"type": "dice", "data": {"result": "1"}}, DiceElement, "[骰子](1)"),
    ]

    for message in messages:
        element = Element.parse_element(message[0])
        assert isinstance(element, message[1])
        assert element.text == message[2]
