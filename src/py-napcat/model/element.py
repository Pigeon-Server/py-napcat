from abc import ABC
from enum import Enum
from typing import Optional, Type

from .basic_event import Serializable


class ElementType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AT = "at"
    FACE = "face"
    REPLY = "reply"


class Element(Serializable, ABC):
    data_type: Type[Serializable] = Serializable
    element_type: ElementType
    element_data: Serializable

    def __init__(self, element_type: ElementType, element_data: dict) -> None:
        self.element_type = element_type
        self.element_data = self.data_type.from_json(element_data)

    def to_json(self) -> dict:
        return {
            "type": self.element_type.value,
            "data": self.element_data.to_json(),
        }

    @classmethod
    def from_json(cls, json_dict: dict) -> "Element":
        return cls(ElementType(json_dict["type"]), json_dict["data"])

    def __str__(self) -> str:
        return f"{self.__name__}(type={self.element_type.value}, data={self.element_data})"

    def __repr__(self) -> str:
        return str(self)


class TextElement(Element):
    class TextElementData(Serializable):
        text: str

        def __init__(self, text: str) -> None:
            self.text = text

        def to_json(self) -> dict:
            return {
                "text": self.text
            }

        @classmethod
        def from_json(cls, json_dict: dict) -> "TextElement.TextElementData":
            return cls(json_dict["text"])

        def __str__(self) -> str:
            return f"TextMessageData(text={self.text})"

        def __repr__(self) -> str:
            return str(self)

    element_data: TextElementData

    def __init__(self, element_type: ElementType, element_data: dict) -> None:
        self.data_type = self.TextElementData
        super().__init__(element_type, element_data)


class ImageElement(Element):
    class ImageElementData(Serializable):
        image_name: str
        image_url: Optional[str]

        def __init__(self, image_name: str, image_url: Optional[str] = None) -> None:
            self.image_name = image_name
            self.image_url = image_url

        def to_json(self) -> dict:
            data = {
                "file": self.image_name
            }
            if self.image_url is not None:
                data["url"] = self.image_url
            return data

        @classmethod
        def from_json(cls, json_dict: dict) -> "Serializable":
            return cls(json_dict["file"], json_dict.get("url"))

    element_data: ImageElementData

    def __init__(self, element_type: ElementType, element_data: dict) -> None:
        self.data_type = self.ImageElementData
        super().__init__(element_type, element_data)


class AtElement(Element):
    class AtElementData(Serializable):
        target_user_id: int

        def __init__(self, target_user_id: int) -> None:
            self.target_user_id = target_user_id

        def to_json(self) -> dict:
            return {
                "qq": self.target_user_id
            }

        @classmethod
        def from_json(cls, json_dict: dict) -> "AtElement.AtElementData":
            return cls(json_dict["qq"])

    element_data: AtElementData

    def __init__(self, element_type: ElementType, element_data: dict) -> None:
        self.data_type = self.AtElementData
        super().__init__(element_type, element_data)


class FaceElement(Element):
    class FaceElementData(Serializable):
        id: int

        def __init__(self, id: int) -> None:
            self.id = id

        def to_json(self) -> dict:
            return {
                "id": self.id
            }

        @classmethod
        def from_json(cls, json_dict: dict) -> "FaceElement.FaceElementData":
            return cls(json_dict["id"])

    element_data: FaceElementData

    def __init__(self, element_type: ElementType, element_data: dict) -> None:
        self.data_type = self.FaceElementData
        super().__init__(element_type, element_data)


class ReplyElement(Element):
    class ReplyElementData(Serializable):
        id: int

        def __init__(self, id: int) -> None:
            self.id = id

        def to_json(self) -> dict:
            return {
                "id": self.id
            }

        @classmethod
        def from_json(cls, json_dict: dict) -> "ReplyElement.ReplyElementData":
            return cls(json_dict["id"])

    element_data: ReplyElementData

    def __init__(self, element_type: ElementType, element_data: dict) -> None:
        self.data_type = self.ReplyElementData
        super().__init__(element_type, element_data)
