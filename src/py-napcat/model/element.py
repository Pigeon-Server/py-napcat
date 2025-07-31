from abc import ABC
from dataclasses import asdict, dataclass
from enum import Enum
from platform import platform
from typing import Any, Optional, Union, overload

from .basic_event import Serializable
from .exception import ParameterError, SendElementOnlyError


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

    def __init__(self, element_type: ElementType, element_data: Serializable) -> None:
        self.element_type = element_type
        self.element_data = element_data

    def to_json(self) -> dict:
        return {
            "type": self.element_type.value,
            "data": self.element_data.to_json(),
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(type={self.element_type.value}, data={self.element_data})"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def parse_element(data: dict) -> "Element":
        try:
            element_type = ElementType(data["type"])
        except KeyError as e:
            raise ParameterError(f"Missing required field: {e}") from e
        except TypeError as e:
            raise ParameterError(f"Unknown element type: {data["type"]}") from e
        element_data = data["data"]
        match element_type:
            case ElementType.TEXT:
                return TextElement.from_json(element_data)
            case ElementType.AT:
                return AtElement.from_json(element_data)
            case ElementType.REPLY:
                return ReplyElement.from_json(element_data)
            case ElementType.FACE:
                return FaceElement.from_json(element_data)
            case ElementType.MFACE:
                return MFaceElement.from_json(element_data)
            case ElementType.DICE:
                return DiceElement.from_json(element_data)
            case ElementType.RPS:
                return RPSElement.from_json(element_data)
            case ElementType.POKE:
                return PokeElement.from_json(element_data)
            case ElementType.IMAGE:
                return ImageElement.from_json(element_data)
            case ElementType.RECORD:
                return RecordElement.from_json(element_data)
            case ElementType.VIDEO:
                return VideoElement.from_json(element_data)
            case ElementType.FILE:
                return FileElement.from_json(element_data)
            case ElementType.JSON:
                return JsonElement.from_json(element_data)
            case ElementType.MUSIC:
                return MusicElement.from_json(element_data)
            case ElementType.FORWARD:
                return ForwardElement.from_json(element_data)
            case _:
                raise ValueError(f"Unknown element type: {element_type}")


class TextElement(Element):
    """
    纯文本
    """

    @dataclass
    class TextElementData(Serializable):
        """
        Attributes:
            text(str): 文本内容(=)
        """
        text: str

        def to_json(self) -> dict:
            return {"text": self.text}

        @classmethod
        def from_json(cls, json_dict: dict) -> "TextElement.TextElementData":
            try:
                return cls(json_dict["text"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    element_data: TextElementData

    def __init__(self, data: Union[str, TextElementData]) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.TEXT, self.TextElementData(data))
        elif isinstance(data, self.TextElementData):
            super().__init__(ElementType.TEXT, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or TextElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "TextElement":
        return cls(cls.TextElementData.from_json(json_dict))


class AtElement(Element):
    """
    At消息
    """

    @dataclass
    class AtElementData(Serializable):
        """
        Attributes:
            target_user_id(int): 要@的QQ号，"all"表示@全体成员(=)
        """
        target_user_id: str

        def to_json(self) -> dict:
            return {"qq": self.target_user_id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "AtElement.AtElementData":
            try:
                return cls(json_dict["qq"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    element_data: AtElementData

    def __init__(self, data: Union[str, AtElementData]) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.AT, self.AtElementData(data))
        elif isinstance(data, self.AtElementData):
            super().__init__(ElementType.AT, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or AtElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "AtElement":
        return cls(cls.AtElementData.from_json(json_dict))


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

        def to_json(self) -> dict:
            return {"id": self.target_message_id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "ReplyElement.ReplyElementData":
            try:
                return cls(json_dict["id"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    element_data: ReplyElementData

    def __init__(self, data: Union[str, ReplyElementData]) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.REPLY, self.ReplyElementData(data))
        elif isinstance(data, self.ReplyElementData):
            super().__init__(ElementType.REPLY, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or ReplyElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "ReplyElement":
        return cls(cls.ReplyElementData.from_json(json_dict))


class FaceElement(Element):
    """
    QQ内置表情
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

        def to_json(self) -> dict:
            return {"id": self.id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "FaceElement.FaceElementData":
            try:
                return cls(json_dict["id"], json_dict.get("raw"), json_dict.get("result_id"),
                           json_dict.get("chain_count"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    element_data: FaceElementData

    def __init__(self, data: Union[str, FaceElementData]) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.FACE, self.FaceElementData(data))
        elif isinstance(data, self.FaceElementData):
            super().__init__(ElementType.FACE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or FaceElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "FaceElement":
        return cls(cls.FaceElementData.from_json(json_dict))


class MFaceElement(Element):
    """
    QQ商城表情
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

        def to_json(self) -> dict:
            return {k: v for k, v in asdict(self).items() if v is not None}

        @classmethod
        def from_json(cls, json_dict: dict) -> "MFaceElement.MFaceElementData":
            try:
                return cls(json_dict["emoji_id"], json_dict["emoji_package_id"], json_dict.get("key"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    @overload
    def __init__(self, data: MFaceElementData) -> None:
        ...

    @overload
    def __init__(self, emoji_id: str, emoji_package_id: str, key: Optional[str] = None,
                 summary: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, MFaceElementData], emoji_package_id: Optional[str] = None,
                 key: Optional[str] = None, summary: Optional[str] = None) -> None:
        if isinstance(data, str):
            if emoji_package_id is not None:
                super().__init__(ElementType.MFACE, self.MFaceElementData(data, emoji_package_id, key, summary))
            else:
                raise ParameterError(f"Argument 'emoji_package_id' should be provided when data is string type")
        elif isinstance(data, self.MFaceElementData):
            super().__init__(ElementType.MFACE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or MFaceElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "MFaceElement":
        return cls(cls.MFaceElementData.from_json(json_dict))


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
                return cls(json_dict["result"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    def __init__(self, data: Optional[DiceElementData] = None) -> None:
        if data is None:
            super().__init__(ElementType.DICE, self.DiceElementData())
        elif isinstance(data, self.DiceElementData):
            super().__init__(ElementType.DICE, data)
        else:
            raise ParameterError(f"Argument 'data' expected DiceElementData or None, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "DiceElement":
        return cls(cls.DiceElementData.from_json(json_dict))


class RPSElement(Element):
    """
    石头剪刀布表情
    """

    class RPSResult(Enum):
        STONE = "1"  # 石头
        SHEARS = "2"  # 剪刀
        CLOTH = "3"  # 布

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
                return cls(RPSElement.RPSResult(json_dict["result"]))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e
            except ValueError as e:
                raise ValueError(f"Result not in dict: {json_dict['result']}, {e}") from e

    def __init__(self, data: Optional[RPSElementData] = None) -> None:
        if data is None:
            super().__init__(ElementType.RPS, self.RPSElementData())
        elif isinstance(data, self.RPSElementData):
            super().__init__(ElementType.RPS, data)
        else:
            raise ParameterError(f"Argument 'data' expected RPSElementData or None, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "RPSElement":
        return cls(cls.RPSElementData.from_json(json_dict))


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

        def to_json(self) -> dict:
            return {"type": self.type, "id": self.id}

        @classmethod
        def from_json(cls, json_dict: dict) -> "PokeElement.PokeElementData":
            try:
                return cls(json_dict["type"], json_dict["id"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    @overload
    def __init__(self, data: PokeElementData) -> None:
        ...

    @overload
    def __init__(self, poke_type: str, poke_id: str) -> None:
        ...

    def __init__(self, data: Union[str, PokeElementData], poke_id: Optional[str] = None) -> None:
        if isinstance(data, str):
            if poke_id is not None:
                super().__init__(ElementType.POKE, self.PokeElementData(data, poke_id))
            else:
                raise ParameterError(f"Argument 'poke_id' should be provided when data is str")
        elif isinstance(data, self.PokeElementData):
            super().__init__(ElementType.POKE, data)
        else:
            raise ParameterError(f"Argument 'data' expected str or PokeElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "PokeElement":
        return cls(cls.PokeElementData.from_json(json_dict))


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
                return cls(json_dict["file"], json_dict.get("url"), json_dict.get("summary"), json_dict.get("sub_type"),
                           json_dict.get("file_size"), json_dict.get("key"), json_dict.get("emoji_id"),
                           json_dict.get("emoji_package_id"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    element_data: ImageElementData

    @overload
    def __init__(self, data: ImageElementData) -> None:
        ...

    @overload
    def __init__(self, file: str, url: Optional[str] = None, summary: Optional[str] = None,
                 sub_type: Optional[str] = None, file_size: Optional[int] = None, key: Optional[str] = None,
                 emoji_id: Optional[str] = None, emoji_package_id: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, ImageElementData], url: Optional[str] = None, summary: Optional[str] = None,
                 sub_type: Optional[str] = None, file_size: Optional[int] = None, key: Optional[str] = None,
                 emoji_id: Optional[str] = None, emoji_package_id: Optional[str] = None) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.IMAGE,
                             self.ImageElementData(data, url, summary, sub_type, file_size,
                                                   key, emoji_id, emoji_package_id))
        elif isinstance(data, self.ImageElementData):
            super().__init__(ElementType.IMAGE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or ImageElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "ImageElement":
        return cls(cls.ImageElementData.from_json(json_dict))


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

        def to_json(self) -> dict:
            return {"file": self.file}

        @classmethod
        def from_json(cls, json_dict: dict) -> "RecordElement.RecordElementData":
            try:
                return cls(json_dict["file"], json_dict.get("file_size"), json_dict.get("path"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    def __init__(self, data: Union[str, RecordElementData]) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.RECORD, self.RecordElementData(data))
        elif isinstance(data, self.RecordElementData):
            super().__init__(ElementType.RECORD, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or RecordElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "RecordElement":
        return cls(cls.RecordElementData.from_json(json_dict))


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

        def to_json(self) -> dict:
            data = {"file": self.file}
            if self.thumb:
                data["thumb"] = self.thumb
            return data

        @classmethod
        def from_json(cls, json_dict: dict) -> "VideoElement.VideoElementData":
            try:
                return cls(json_dict["file"], json_dict.get("url"), json_dict.get("file_size"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    @overload
    def __init__(self, data: VideoElementData) -> None:
        ...

    @overload
    def __init__(self, file: str, thumb: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, VideoElementData], thumb: Optional[str] = None) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.VIDEO, self.VideoElementData(file=data, thumb=thumb))
        elif isinstance(data, self.VideoElementData):
            super().__init__(ElementType.VIDEO, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or VideoElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "VideoElement":
        return cls(cls.VideoElementData.from_json(json_dict))


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

        def to_json(self) -> dict:
            data = {"file": self.file}
            if self.name is not None:
                data["name"] = self.name
            return data

        @classmethod
        def from_json(cls, json_dict: dict) -> "FileElement.FileElementData":
            try:
                return cls(json_dict["file"], json_dict.get("file_id"), json_dict.get("file_size"))
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    @overload
    def __init__(self, data: FileElementData) -> None:
        ...

    @overload
    def __init__(self, file: str, name: Optional[str] = None) -> None:
        ...

    def __init__(self, data: Union[str, FileElementData], name: Optional[str] = None) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.FILE, self.FileElementData(file=data, name=name))
        elif isinstance(data, self.FileElementData):
            super().__init__(ElementType.FILE, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or FileElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "FileElement":
        return cls(cls.FileElementData.from_json(json_dict))


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

        def to_json(self) -> dict:
            return {"data": self.data}

        @classmethod
        def from_json(cls, json_dict: dict) -> "JsonElement.JsonElementData":
            try:
                return cls(json_dict["data"])
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

    def __init__(self, data: Union[str, JsonElementData]) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.JSON, self.JsonElementData(data=data))
        elif isinstance(data, self.JsonElementData):
            super().__init__(ElementType.JSON, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or JsonElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "JsonElement":
        return cls(cls.JsonElementData.from_json(json_dict))


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
                assert self.url is not None and self.image is not None
            else:
                assert self.id is not None

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
        if isinstance(data, self.MusicElementData):
            super().__init__(ElementType.MUSIC, data)
        elif isinstance(data, self.MusicPlatform):
            if data == self.MusicPlatform.CUSTOM:
                if url is None:
                    raise ParameterError(f"Argument 'url' should be provided when data is CUSTOM")
                if image is None:
                    raise ParameterError(f"Argument 'image' should be provided when data is CUSTOM")
                super().__init__(ElementType.MUSIC,
                                 self.MusicElementData(platform_type=data, url=url, image=image, singer=singer,
                                                       title=title, content=content))
            else:
                if music_id is None:
                    raise ParameterError(f"Argument 'music_id' should be provided when data is not CUSTOM")
                super().__init__(ElementType.MUSIC, self.MusicElementData(platform_type=data, id=music_id))
        else:
            raise ParameterError(f"Argument 'data' expected MusicPlatform or MusicElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "MusicElement":
        raise SendElementOnlyError(f"This element can not be received")


class ForwardElement(Element):
    @dataclass
    class ForwardElementData(Serializable):
        """
        Attributes:
            id(str): 转发消息ID(=)
            content(Optional[list[Element]]): 转发的消息内容列表(仅当解析转发内容时)(<?)
        """
        id: str
        content: Optional[list[Element]] = None

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

    def __init__(self, data: Union[str, ForwardElementData]) -> None:
        if isinstance(data, str):
            super().__init__(ElementType.FORWARD, self.ForwardElementData(id=data))
        elif isinstance(data, self.ForwardElementData):
            super().__init__(ElementType.FORWARD, data)
        else:
            raise ParameterError(f"Argument 'data' expected string or ForwardElementData, but got {type(data)}")

    @classmethod
    def from_json(cls, json_dict: dict) -> "ForwardElement":
        return cls(cls.ForwardElementData.from_json(json_dict))
