from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Optional, Type, Union, overload

from .basic_event import Serializable
from .exception import ParameterError, ParseError, SendElementOnlyError, UnregisteredElementError


class ElementType(Enum):
    # 文本类消息
    TEXT = "text"
    AT = "at"
    REPLY = "reply"
    # 表情类消息
    FACE = "face"  # 内置表情
    MFACE = "mface"  # QQ商城表情
    DICE = "dice"  # 骰子
    RPS = "rps"  # 石头剪刀布
    POKE = "poke"  # 戳一戳
    # 多媒体类型
    IMAGE = "image"
    RECORD = "record"  # 语音
    VIDEO = "video"
    FILE = "file"
    # 富消息类
    JSON = "json"
    MUSIC = "music"  # 音乐分享
    FORWARD = "forward"  # 转发内容


class Element(Serializable, ABC):
    """
    消息元素基类\n
    在每条消息的Data类的属性注释中\n
    >表示仅发送的消息有此字段\n
    <表示仅接受的消息有此字段\n
    =表示接受发送均有此字段\n
    ?表示该参数是可选的
    """
    element_type: ElementType
    element_data: Serializable
    _element_registry: dict[ElementType, Type["Element"]] = {}

    def __init__(self, element_type: ElementType, element_data: Serializable) -> None:
        self.element_type = element_type
        self.element_data = element_data

    @property
    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_json(cls, json_dict: dict) -> "Element":
        raise NotImplementedError

    def to_json(self) -> dict:
        return {"type": self.element_type.value, "data": self.element_data.to_json()}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(type={self.element_type.value}, data={self.element_data})"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def register_element(cls, element_type: ElementType):
        def decorator(element_class: Type["Element"]):
            cls._element_registry[element_type] = element_class
            return element_class

        return decorator

    @classmethod
    def parse_element(cls, data: dict) -> "Element":
        try:
            element_type = ElementType(data["type"])
            element_data = data["data"]
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ParameterError(f"Unknown element type: {data["type"]}") from e
        if target_class := cls._element_registry.get(element_type):
            try:
                return target_class.from_json(element_data)
            except Exception as e:
                raise ParseError(f"Failed to parse {element_type.value} element") from e

        raise UnregisteredElementError(f"No parser registered for element type: {element_type.value}")


@Element.register_element(ElementType.TEXT)
class TextElement(Element):
    """
    纯文本消息
    """

    @dataclass
    class TextElementData(Serializable):
        """
        Attributes:
            text(str): 文本内容(=)
        """
        text: str

        def __post_init__(self) -> None:
            assert isinstance(self.text, str)

        def to_json(self) -> dict:
            return {"text": self.text}

        @classmethod
        def from_json(cls, json_dict: dict) -> "TextElement.TextElementData":
            try:
                return cls(text=json_dict["text"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(text={self.text})"

    element_data: TextElementData

    def __init__(self, data: Union[str, TextElementData]) -> None:
        """
        构建一条纯文本消息
        :param data: 消息内容,可以直接传入消息字符串,也可以传入TextElementData对象
        """
        if isinstance(data, str):
            super().__init__(ElementType.TEXT, self.TextElementData(text=data))
        elif isinstance(data, self.TextElementData):
            super().__init__(ElementType.TEXT, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or TextElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "TextElement":
        return cls(cls.TextElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return self.element_data.text


@Element.register_element(ElementType.AT)
class AtElement(Element):
    """
    At消息
    """

    @dataclass
    class AtElementData(Serializable):
        """
        Attributes:
            target_user_id(int): 要@的QQ号,"all"表示@全体成员(=)
        """
        target_user_id: str

        def __post_init__(self) -> None:
            assert isinstance(self.target_user_id, str)

        def to_json(self) -> dict:
            return {"qq": self.target_user_id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "AtElement.AtElementData":
            try:
                return cls(target_user_id=json_dict["qq"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(qq={self.target_user_id})"

    element_data: AtElementData

    def __init__(self, data: Union[str, AtElementData]) -> None:
        """
        构建一条At消息
        :param data: At的目标,可以直接传入字符串,表示目标QQ号,也可以传入AtElementData对象
        """
        if isinstance(data, str):
            super().__init__(ElementType.AT, self.AtElementData(target_user_id=data))
        elif isinstance(data, self.AtElementData):
            super().__init__(ElementType.AT, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or AtElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "AtElement":
        return cls(cls.AtElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"@{self.element_data.target_user_id}"


@Element.register_element(ElementType.REPLY)
class ReplyElement(Element):
    """
    回复消息
    """

    @dataclass
    class ReplyElementData(Serializable):
        """
        Attributes:
            target_message_id(int): 被回复消息的唯一ID(=)
        """
        target_message_id: str

        def __post_init__(self) -> None:
            assert isinstance(self.target_message_id, str)

        def to_json(self) -> dict:
            return {"id": self.target_message_id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "ReplyElement.ReplyElementData":
            try:
                return cls(target_message_id=json_dict["id"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(id={self.target_message_id})"

    element_data: ReplyElementData

    def __init__(self, data: Union[str, ReplyElementData]) -> None:
        """
        构建一条回复消息
        :param data: 目标消息的消息ID或者ReplyElementData对象
        """
        if isinstance(data, str):
            super().__init__(ElementType.REPLY, self.ReplyElementData(target_message_id=data))
        elif isinstance(data, self.ReplyElementData):
            super().__init__(ElementType.REPLY, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or ReplyElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "ReplyElement":
        return cls(cls.ReplyElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[回复]({self.element_data.target_message_id})"


@Element.register_element(ElementType.FACE)
class FaceElement(Element):
    """
    QQ内置表情消息
    """

    @dataclass
    class FaceElementData(Serializable):
        """
        Attributes:
            id(str): 表情ID(=)
            raw(Optional[Any]): 表情原始数据(<?)
            result_id(Optional[str]): 骰子或石头剪刀布结果ID(<?)
            chain_count(Optional[int]): 连续发送次数(<?)
        """
        id: str
        raw: Optional[Any] = None
        result_id: Optional[str] = None
        chain_count: Optional[int] = None

        def __post_init__(self) -> None:
            assert isinstance(self.id, str)

        def to_json(self) -> dict:
            return {"id": self.id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "FaceElement.FaceElementData":
            try:
                return cls(id=json_dict["id"],
                           raw=json_dict.get("raw"),
                           result_id=json_dict.get("resultId"),
                           chain_count=json_dict.get("chainCount"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return (f"{self.__class__.__name__}(id={self.id}, raw={self.raw}, result_id={self.result_id}, "
                    f"chain_count={self.chain_count})")

    element_data: FaceElementData

    def __init__(self, data: Union[str, FaceElementData]) -> None:
        """
        构建一条QQ内置表情消息
        :param data: 表情ID或者FaceElementData对象
        """
        if isinstance(data, str):
            super().__init__(ElementType.FACE, self.FaceElementData(id=data))
        elif isinstance(data, self.FaceElementData):
            super().__init__(ElementType.FACE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or FaceElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "FaceElement":
        return cls(cls.FaceElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        if self.element_data.raw is not None and isinstance(self.element_data.raw, dict) and \
                (text := self.element_data.raw.get("faceText")) is not None and len(text) > 0:
            return text
        return f"[表情]({self.element_data.id})"


@Element.register_element(ElementType.MFACE)
class MFaceElement(Element):
    """
    QQ商城表情消息
    """

    @dataclass
    class MFaceElementData(Serializable):
        """
        Attributes:
            emoji_id(str): 表情ID(=)
            emoji_package_id(str): 表情包ID(=)
            key(Optional[str]): 表情key(=?)
            summary(Optional[str]): 表情名称(>?)
        """
        emoji_id: str
        emoji_package_id: str
        key: Optional[str] = None
        summary: Optional[str] = None

        def __post_init__(self) -> None:
            assert isinstance(self.emoji_id, str)
            assert isinstance(self.emoji_package_id, str)

        def to_json(self) -> dict:
            return {k: v for k, v in asdict(self).items() if v is not None}

        @classmethod
        def from_json(cls, json_dict: dict) -> "MFaceElement.MFaceElementData":
            try:
                return cls(emoji_id=json_dict["emojiId"],
                           emoji_package_id=json_dict["emojiPackageId"],
                           key=json_dict.get("key"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return (f"{self.__class__.__name__}(emoji_id={self.emoji_id}, emoji_package_id={self.emoji_package_id}, "
                    f"key={self.key}, summary={self.summary})")

    element_data: MFaceElementData

    @overload
    def __init__(self, data: MFaceElementData) -> None:
        ...

    @overload
    def __init__(self, emoji_id: str, emoji_package_id: str, key: Optional[str] = None,
                 summary: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, MFaceElementData], emoji_package_id: Optional[str] = None,
                 key: Optional[str] = None, summary: Optional[str] = None) -> None:
        """
        构造一条QQ商城表情消息
        :param data: 表情ID或者MFaceElementData对象
        :param emoji_package_id: 表情包ID,当data参数是字符串类型的时候此参数必须被提供
        :param key: 表情key
        :param summary: 表情名称
        """
        if isinstance(data, str):
            if emoji_package_id is not None:
                super().__init__(ElementType.MFACE,
                                 self.MFaceElementData(emoji_id=data,
                                                       emoji_package_id=emoji_package_id,
                                                       key=key,
                                                       summary=summary))
            else:
                raise ParameterError(f"Argument 'emoji_package_id' should be provided when data is string type")
        elif isinstance(data, self.MFaceElementData):
            super().__init__(ElementType.MFACE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or MFaceElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "MFaceElement":
        return cls(cls.MFaceElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        if self.element_data.summary is not None:
            return self.element_data.summary
        return f"[表情]({self.element_data.emoji_id})"


@Element.register_element(ElementType.DICE)
class DiceElement(Element):
    """
    骰子表情
    """

    @dataclass
    class DiceElementData(Serializable):
        """
        Attributes:
            result(Optional[str]): 骰子点数(<)
        """
        result: Optional[str] = None

        def to_json(self) -> dict:
            return {}

        @classmethod
        def from_json(cls, json_dict: dict) -> "DiceElement.DiceElementData":
            try:
                return cls(result=json_dict["result"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(result={self.result})"

    element_data: DiceElementData

    def __init__(self, data: Optional[DiceElementData] = None) -> None:
        """
        构建一条骰子消息
        :param data: 发送时请不要传递参数
        """
        if data is None:
            super().__init__(ElementType.DICE, self.DiceElementData())
        elif isinstance(data, self.DiceElementData):
            super().__init__(ElementType.DICE, data)
        else:
            raise ParameterError(f"Argument 'data' expected DiceElementData or None, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "DiceElement":
        return cls(cls.DiceElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[骰子]({self.element_data.result})"


@Element.register_element(ElementType.RPS)
class RPSElement(Element):
    """
    石头剪刀布表情
    """

    class RPSResult(Enum):
        CLOTH = "1"  # 布
        SHEARS = "2"  # 剪刀
        STONE = "3"  # 石头

    @dataclass
    class RPSElementData(Serializable):
        """
        Attributes:
            result(Optional[RPSElement.RPSResult]): 石头剪刀布结果(<)
        """
        result: Optional["RPSElement.RPSResult"] = None

        def to_json(self) -> dict:
            return {}

        @classmethod
        def from_json(cls, json_dict: dict) -> "RPSElement.RPSElementData":
            try:
                return cls(result=RPSElement.RPSResult(json_dict["result"]))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e
            except ValueError as e:
                raise ValueError(f"Result not in dict: {json_dict['result']}, {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(result={self.result})"

    element_data: RPSElementData

    def __init__(self, data: Optional[RPSElementData] = None) -> None:
        """
        构建一条石头剪刀布消息
        :param data: 发送时请不要传递参数
        """
        if data is None:
            super().__init__(ElementType.RPS, self.RPSElementData())
        elif isinstance(data, self.RPSElementData):
            super().__init__(ElementType.RPS, data)
        else:
            raise ParameterError(f"Argument 'data' expected RPSElementData or None, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "RPSElement":
        return cls(cls.RPSElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[石头剪刀布]({self.element_data.result.name})"


@Element.register_element(ElementType.POKE)
class PokeElement(Element):
    """
    戳一戳消息
    """

    @dataclass
    class PokeElementData(Serializable):
        """
        Attributes:
            type(str): 戳一戳类型(=)
            type(str): 戳一戳ID(=)
        """

        type: str
        id: str

        def __post_init__(self) -> None:
            assert isinstance(self.type, str)
            assert isinstance(self.id, str)

        def to_json(self) -> dict:
            return {"type": self.type, "id": self.id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "PokeElement.PokeElementData":
            try:
                return cls(type=json_dict["type"],
                           id=json_dict["id"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(type={self.type}, id={self.id})"

    element_data: PokeElementData

    @overload
    def __init__(self, data: PokeElementData) -> None:
        ...

    @overload
    def __init__(self, poke_type: str, poke_id: str) -> None:
        ...

    def __init__(self, data: Union[str, PokeElementData], poke_id: Optional[str] = None) -> None:
        """
        构建一条戳一戳消息
        :param data: 戳一戳类型或者PokeElementData对象
        :param poke_id: 戳一戳ID
        """
        if isinstance(data, str):
            if poke_id is not None:
                super().__init__(ElementType.POKE, self.PokeElementData(type=data, id=poke_id))
            else:
                raise ParameterError(f"Argument 'poke_id' should be provided when data is str")
        elif isinstance(data, self.PokeElementData):
            super().__init__(ElementType.POKE, data)
        else:
            raise ParameterError(f"Argument 'data' expected str or PokeElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "PokeElement":
        return cls(cls.PokeElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[戳一戳]"


@Element.register_element(ElementType.IMAGE)
class ImageElement(Element):
    """
    图片消息
    """

    @dataclass
    class ImageElementData(Serializable):
        """
        Attributes:
            file(str): 接受时: 图片文件名; 发送时: 图片文件路径、URL或Base64编码(=)
            url(Optional[str]): 图片URL(=?)
            summary(Optional[str]): 图片描述(=?)
            sub_type(Optional[str]): 图片子类型(=?)
            file_size(Optional[int]): 文件大小(<?)
            key(Optional[str]): 表情key(<?)
            emoji_id(Optional[str]): 表情ID(<?)
            emoji_package_id(Optional[str]): 表情包ID(<?)
        """
        file: str
        url: Optional[str] = None
        summary: Optional[str] = None
        sub_type: Optional[str] = None
        file_size: Optional[int] = None
        key: Optional[str] = None
        emoji_id: Optional[str] = None
        emoji_package_id: Optional[str] = None

        def __post_init__(self) -> None:
            assert isinstance(self.file, str)

        def to_json(self) -> dict:
            data = {"file": self.file}
            if self.url is not None:
                data["url"] = self.url
            if self.summary is not None:
                data["summary"] = self.summary
            if self.sub_type is not None:
                data["sub_type"] = self.sub_type
            return data

        @classmethod
        def from_json(cls, json_dict: dict) -> "ImageElement.ImageElementData":
            try:
                return cls(file=json_dict["file"],
                           url=json_dict.get("url"),
                           summary=json_dict.get("summary"),
                           sub_type=json_dict.get("sub_type"),
                           file_size=json_dict.get("file_size"),
                           key=json_dict.get("key"),
                           emoji_id=json_dict.get("emoji_id"),
                           emoji_package_id=json_dict.get("emoji_package_id"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return (f"{self.__class__.__name__}(file={self.file}, url={self.url}, summary={self.summary}, "
                    f"sub_type={self.sub_type}, file_size={self.file_size}, key={self.key}, "
                    f"emoji_id={self.emoji_id}, emoji_package_id={self.emoji_package_id})")

    element_data: ImageElementData

    @overload
    def __init__(self, data: ImageElementData) -> None:
        ...

    @overload
    def __init__(self, file: str, url: Optional[str] = None, summary: Optional[str] = None,
                 sub_type: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, ImageElementData], url: Optional[str] = None, summary: Optional[str] = None,
                 sub_type: Optional[str] = None) -> None:
        """
        构建一条图片消息
        :param data: 图片文件路径、URL或Base64编码或者ImageElementData对象
        :param url: 图片URL
        :param summary: 图片描述
        :param sub_type: 图片子类型
        """
        if isinstance(data, str):
            super().__init__(ElementType.IMAGE,
                             self.ImageElementData(file=data, url=url, summary=summary, sub_type=sub_type))
        elif isinstance(data, self.ImageElementData):
            super().__init__(ElementType.IMAGE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or ImageElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "ImageElement":
        return cls(cls.ImageElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        if self.element_data.summary is not None and self.element_data.summary != "":
            return self.element_data.summary
        return f"[图片]"


@Element.register_element(ElementType.RECORD)
class RecordElement(Element):
    """
    语音消息
    """

    @dataclass
    class RecordElementData(Serializable):
        """
        Attributes:
            file(str): 接受时: 语音文件标识; 发送时: 语音文件路径、URL或Base64编码(=)
            file_size(Optional[int]): 文件大小(字节)(<?)
            path(Optional[str]): 文件路径(<?)
        """
        file: str
        file_size: Optional[int] = None
        path: Optional[str] = None

        def __post_init__(self) -> None:
            assert isinstance(self.file, str)

        def to_json(self) -> dict:
            return {"file": self.file}

        @classmethod
        def from_json(cls, json_dict: dict) -> "RecordElement.RecordElementData":
            try:
                return cls(file=json_dict["file"],
                           file_size=json_dict.get("file_size"),
                           path=json_dict.get("path"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(file={self.file}, file_size={self.file_size}, path={self.path})"

    element_data: RecordElementData

    def __init__(self, data: Union[str, RecordElementData]) -> None:
        """
        构造一条语音消息
        :param data: 语音文件路径、URL或Base64编码或RecordElementData对象
        """
        if isinstance(data, str):
            super().__init__(ElementType.RECORD, self.RecordElementData(file=data))
        elif isinstance(data, self.RecordElementData):
            super().__init__(ElementType.RECORD, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or RecordElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "RecordElement":
        return cls(cls.RecordElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[语音]"


@Element.register_element(ElementType.VIDEO)
class VideoElement(Element):
    """
    视频消息
    """

    @dataclass
    class VideoElementData(Serializable):
        """
        Attributes:
            file(str): 接受时: 视频文件标识; 发送时: 视频文件路径、URL或Base64编码(=)
            url(Optional[str]): 视频在线URL(<?)
            file_size(Optional[int]): 文件大小(字节)(<?)
            thumb(Optional[str]): 视频缩略图(>?)
        """
        file: str
        url: Optional[str] = None
        file_size: Optional[int] = None
        thumb: Optional[str] = None

        def __post_init__(self) -> None:
            assert isinstance(self.file, str)

        def to_json(self) -> dict:
            data = {"file": self.file}
            if self.thumb:
                data["thumb"] = self.thumb
            return data

        @classmethod
        def from_json(cls, json_dict: dict) -> "VideoElement.VideoElementData":
            try:
                return cls(file=json_dict["file"],
                           url=json_dict.get("url"),
                           file_size=json_dict.get("file_size"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return (f"{self.__class__.__name__}(file={self.file}, url={self.url}, file_size={self.file_size}, "
                    f"thumb={self.thumb})")

    element_data: VideoElementData

    @overload
    def __init__(self, data: VideoElementData) -> None:
        ...

    @overload
    def __init__(self, file: str, thumb: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, VideoElementData], thumb: Optional[str] = None) -> None:
        """
        构造一条视频消息
        :param data: 视频文件路径、URL或Base64编码或VideoElementData对象
        :param thumb: 视频缩略图
        """
        if isinstance(data, str):
            super().__init__(ElementType.VIDEO, self.VideoElementData(file=data, thumb=thumb))
        elif isinstance(data, self.VideoElementData):
            super().__init__(ElementType.VIDEO, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or VideoElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "VideoElement":
        return cls(cls.VideoElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[视频]"


@Element.register_element(ElementType.FILE)
class FileElement(Element):
    """
    文件消息
    """

    @dataclass
    class FileElementData(Serializable):
        """
        Attributes:
            file(str): 接受时: 文件名; 发送时: 文件路径、URL或Base64编码(=)
            file_id(Optional[str]): 文件ID(<?)
            file_size(Optional[int]): 文件大小(字节)(<?)
            name(Optional[str]): 文件名(可选)(>?)
        """
        file: str
        file_id: Optional[str] = None
        file_size: Optional[int] = None
        name: Optional[str] = None

        def __post_init__(self) -> None:
            assert isinstance(self.file, str)

        def to_json(self) -> dict:
            data = {"file": self.file}
            if self.name is not None:
                data["name"] = self.name
            return data

        @classmethod
        def from_json(cls, json_dict: dict) -> "FileElement.FileElementData":
            try:
                return cls(file=json_dict["file"],
                           file_id=json_dict.get("file_id"),
                           file_size=json_dict.get("file_size"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return (f"{self.__class__.__name__}(file={self.file}, file_id={self.file_id}, file_size={self.file_size}, "
                    f"name={self.name})")

    element_data: FileElementData

    @overload
    def __init__(self, data: FileElementData) -> None:
        ...

    @overload
    def __init__(self, file: str, name: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, FileElementData], name: Optional[str] = None) -> None:
        """
        构建一条文件消息
        :param data: 文件路径、URL或Base64编码或FileElementData对象
        :param name: 文件名
        """
        if isinstance(data, str):
            super().__init__(ElementType.FILE, self.FileElementData(file=data, name=name))
        elif isinstance(data, self.FileElementData):
            super().__init__(ElementType.FILE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or FileElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "FileElement":
        return cls(cls.FileElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[文件]"


@Element.register_element(ElementType.JSON)
class JsonElement(Element):
    """
    JSON格式的卡片消息
    """

    @dataclass
    class JsonElementData(Serializable):
        """
        Attributes:
            data(str): JSON字符串(=)
        """
        data: str

        def __post_init__(self):
            assert isinstance(self.data, str)

        def to_json(self) -> dict:
            return {"data": self.data}

        @classmethod
        def from_json(cls, json_dict: dict) -> "JsonElement.JsonElementData":
            try:
                return cls(data=json_dict["data"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(data={self.data})"

    element_data: JsonElementData

    def __init__(self, data: Union[str, JsonElementData]) -> None:
        """
        构建一条Json消息
        :param data: JSON字符串或JsonElementData对象
        """
        if isinstance(data, str):
            super().__init__(ElementType.JSON, self.JsonElementData(data=data))
        elif isinstance(data, self.JsonElementData):
            super().__init__(ElementType.JSON, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or JsonElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "JsonElement":
        return cls(cls.JsonElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[JSON]"


@Element.register_element(ElementType.MUSIC)
class MusicElement(Element):
    """
    音乐分享(仅能发送)
    """

    class MusicPlatform(Enum):
        QQ = "qq"
        WANG_YI = "163"
        KU_GOU = "kugou"
        KU_WO = "kuwo"
        MI_GU = "migu"
        CUSTOM = "custom"

    @dataclass
    class MusicElementData(Serializable):
        """
        仅能发送
        Attributes:
            platform_type("MusicElement.MusicPlatform"): 音乐平台
            id(Optional[str]): 音乐ID(平台非CUSTOM必填)
            url(Optional[str]): 音乐链接(CUSTOM必填)
            image(Optional[str]): 封面图片(CUSTOM必填)
            singer(Optional[str]): 歌手
            title(Optional[str]): 标题
            content(Optional[str]): 内容描述
        """

        platform_type: "MusicElement.MusicPlatform"
        id: Optional[str] = None
        url: Optional[str] = None
        image: Optional[str] = None
        singer: Optional[str] = None
        title: Optional[str] = None
        content: Optional[str] = None

        def __post_init__(self):
            if self.platform_type == MusicElement.MusicPlatform.CUSTOM:
                assert isinstance(self.url, str) and isinstance(self.image, str)
            else:
                assert isinstance(self.id, str)

        def to_json(self) -> dict:
            data = {"type": self.platform_type.value}
            if self.platform_type == MusicElement.MusicPlatform.CUSTOM:
                data["url"] = self.url
                data["image"] = self.image
                if self.singer is not None:
                    data["singer"] = self.singer
                if self.title is not None:
                    data["title"] = self.title
                if self.content is not None:
                    data["content"] = self.content
            else:
                data["id"] = self.id
            return data

        @classmethod
        def from_json(cls, json_dict: dict) -> "MusicElement":
            raise SendElementOnlyError(f"This element can not be received")

        def __str__(self) -> str:
            return (f"{self.__class__.__name__}(platform_type={self.platform_type.value}, id={self.id}, "
                    f"url={self.url}, image={self.image}, singer={self.singer}, "
                    f"title={self.title}, content={self.content})")

    element_data: MusicElementData

    @overload
    def __init__(self, data: MusicElementData) -> None:
        ...

    @overload
    def __init__(self, platform_type: MusicPlatform, music_id: Optional[str] = None,
                 url: Optional[str] = None,
                 image: Optional[str] = None, singer: Optional[str] = None, title: Optional[str] = None,
                 content: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[MusicPlatform, MusicElementData], music_id: Optional[str] = None,
                 url: Optional[str] = None,
                 image: Optional[str] = None, singer: Optional[str] = None, title: Optional[str] = None,
                 content: Optional[str] = None) -> None:
        """
        构建一条音乐分享消息
        :param data: 音乐平台MusicPlatform或者MusicElementData对象
        :param music_id: 音乐ID(平台非CUSTOM必填)
        :param url: 音乐链接(CUSTOM必填)
        :param image: 封面图片(CUSTOM必填)
        :param singer: 歌手
        :param title: 标题
        :param content: 内容描述
        """
        if isinstance(data, self.MusicElementData):
            super().__init__(ElementType.MUSIC, data)
        elif isinstance(data, self.MusicPlatform):
            if data == self.MusicPlatform.CUSTOM:
                if url is None:
                    raise ParameterError(f"Argument 'url' should be provided when data is CUSTOM")
                if image is None:
                    raise ParameterError(f"Argument 'image' should be provided when data is CUSTOM")
                super().__init__(ElementType.MUSIC,
                                 self.MusicElementData(platform_type=data, url=url, image=image,
                                                       singer=singer, title=title, content=content))
            else:
                if music_id is None:
                    raise ParameterError(f"Argument 'music_id' should be provided when data is not CUSTOM")
                super().__init__(ElementType.MUSIC,
                                 self.MusicElementData(platform_type=data, id=music_id))
        else:
            raise ParameterError(f"Argument 'data' expected MusicPlatform or MusicElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "MusicElement":
        raise SendElementOnlyError(f"This element can not be received")

    @property
    def text(self) -> str:
        return f"音乐分享"


@Element.register_element(ElementType.FORWARD)
class ForwardElement(Element):
    """
    合并消息
    """

    @dataclass
    class ForwardElementData(Serializable):
        """
        Attributes:
            id(str): 转发消息ID(=)
            content(Optional[list[Element]]): 转发的消息内容列表(仅当解析转发内容时)(<?)
        """
        id: str
        content: Optional[list[Element]] = None

        def __post_init__(self) -> None:
            assert isinstance(self.id, str)

        def to_json(self) -> dict:
            return {"id": self.id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "ForwardElement.ForwardElementData":
            raw_content = json_dict.get("content")
            if raw_content is not None:
                raw_content = [Element.parse_element(data) for data in raw_content]
            try:
                return cls(json_dict["id"], raw_content)
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        def __str__(self) -> str:
            return f"{self.__class__.__name__}(id={self.id}, content={self.content})"

    element_data: ForwardElementData

    def __init__(self, data: Union[str, ForwardElementData]) -> None:
        """
        构造一条合并消息
        :param data: 转发消息ID或者ForwardElementData对象
        """
        if isinstance(data, str):
            super().__init__(ElementType.FORWARD, self.ForwardElementData(id=data))
        elif isinstance(data, self.ForwardElementData):
            super().__init__(ElementType.FORWARD, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or ForwardElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "ForwardElement":
        return cls(cls.ForwardElementData.from_json(json_dict))

    @property
    def text(self) -> str:
        return f"[合并消息]"
