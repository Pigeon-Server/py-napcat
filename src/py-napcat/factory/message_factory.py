from ..model import Element, ElementType, TextElement, ImageElement, AtElement, FaceElement, ReplyElement


class MessageFactory:
    @staticmethod
    def parse_element(data: dict) -> Element:
        element_type = data["type"]
        element_data = data["data"]
        match ElementType(element_type):
            case ElementType.TEXT:
                return TextElement(element_type, element_data)
            case ElementType.IMAGE:
                return ImageElement(element_type, element_data)
            case ElementType.AT:
                return AtElement(element_type, element_data)
            case ElementType.FACE:
                return FaceElement(element_type, element_data)
            case ElementType.REPLY:
                return ReplyElement(element_type, element_data)
            case _:
                raise ValueError(f"Unknown element type: {element_type}")
