from typing import Generic, Literal, TypeVar

import nonebot
from pydantic import BaseModel
import nonebot_plugin_localstore as store


class PluginConfig(BaseModel):
    zxpix_api: str = "http://pix.zhenxun.org"
    """PIX api"""
    zxpix_image_size: Literal["large", "medium", "original", "square_medium"] = "large"
    """获取图像大小"""
    zxpix_timeout: int = 10
    """请求超时时间"""
    zxpix_show_info: bool = True
    """是否显示图片相关信息"""
    zxpix_allow_group_r18: bool = False
    """是否允许群聊使用r18"""
    zxpix_system_proxy: str | None = None
    """系统代理"""
    zxpix_max_once_num2forward: int = 0
    """多于该数量的图片时使用转发消息，0为不使用"""
    zxpix_nginx: str | None = "pixiv.re"
    """反代"""
    zxpix_image_to_bytes: bool = False
    """是否将图片转换为bytes"""


config = nonebot.get_plugin_config(PluginConfig)

RT = TypeVar("RT")


class Token:
    def __init__(self) -> None:
        self.file = store.get_plugin_data_dir() / "token.txt"
        self.token = ""
        if self.file.exists():
            self.token = self.file.read_text(encoding="utf-8").strip()

    def save(self, token: str):
        self.token = token
        self.file.open("w", encoding="utf-8").write(self.token)


token = Token()


class PixResult(Generic[RT], BaseModel):
    """
    总体返回
    """

    suc: bool
    code: int
    info: str
    warning: str | None
    data: RT
