from strenum import StrEnum


class KwType(StrEnum):
    """关键词类型"""

    KEYWORD = "KEYWORD"
    """关键词"""
    UID = "UID"
    """用户uid"""
    PID = "PID"
    """图片pid"""
    BLACK = "BLACK"
    """黑名单"""
