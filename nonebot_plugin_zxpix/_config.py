import time
from typing import Generic, Literal, TypeVar

import nonebot
import nonebot_plugin_localstore as store
from pydantic import BaseModel


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
    zxpix_small_nginx: str | None = "i.suimoe.com"
    """缩略图反代"""
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


class PixModel(BaseModel):
    pid: str
    """pid"""
    uid: str
    """uid"""
    author: str
    """作者"""
    title: str
    """标题"""
    sanity_level: int
    """sanity_level"""
    x_restrict: int
    """x_restrict"""
    total_view: int
    """总浏览数"""
    total_bookmarks: int
    """总收藏数"""
    nsfw_tag: int
    """nsfw等级"""
    is_ai: bool
    """是否ai图"""
    url: str
    """图片url"""
    is_multiple: bool
    """是否多图"""
    img_p: str
    """多图第n张"""
    tags: str
    """tags"""


class InfoModel(BaseModel):
    msg_id: str
    """消息id"""
    time: int
    """时间戳"""
    info: PixModel
    """PixModel"""


class InfoManage:
    data: dict[str, InfoModel] = {}  # noqa: RUF012

    @classmethod
    def add(cls, msg_id: str, pix: PixModel):
        """添加图片信息

        参数:
            msg_id: 消息id
            pix: PixGallery
        """
        cls.data[msg_id] = InfoModel(msg_id=msg_id, time=int(time.time()), info=pix)

    @classmethod
    def get(cls, msg_id: str) -> PixModel | None:
        """获取图片信息

        参数:
            msg_id: 消息id

        返回:
            InfoModel | None: 图片信息
        """
        return info.info if (info := cls.data.get(msg_id)) else None

    @classmethod
    def remove(cls):
        """移除超时五分钟的图片数据"""
        now = time.time()
        key_list = list(cls.data.keys())
        for key in key_list:
            if now - cls.data[key].time > 60 * 5:
                cls.data.pop(key)
