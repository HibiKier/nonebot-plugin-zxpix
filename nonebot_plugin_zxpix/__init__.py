from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_localstore")
require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from ._config import PluginConfig

__plugin_meta__ = PluginMetadata(
    name="Pix图库",
    description="小真寻的pix图库",
    usage="""
    pix ?*[tags] ?[-n 1]: 通过 tag 获取相似图片，不含tag时随机抽取,
                -n表示数量, -r表示查看r18, -noai表示过滤ai
        示例：pix 萝莉 白丝
        示例：pix 萝莉 白丝 -n 10  （10为数量）

    pix图库 ?[tags](使用空格分隔): 查看pix图库数量

    pix添加 ['u', 'p'] [content]
            u: uid
            p: pid
            k: 关键词
        示例:
            pix添加 u 123456789
            pix添加 p 123456789

    引用 /info : 引用图片查看图片信息
    引用 /block ?[-u]: 提交图片block请求，存在-u时将block该uid下所有图片
    引用 /nsfw n: 设置图片nsfw，n在[0, 1, 2]之间
        0: 普通
        1: 色图
        2: r18
    """,
    type="application",
    config=PluginConfig,
    homepage="https://github.com/HibiKier/nonebot-plugin-zxpix",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna",
    ),
    extra={"author": "HibiKier", "version": "0.1"},
)

from .pix import *  # noqa: F403
from .pix_info import *  # noqa: F403
from .pix_keyword import *  # noqa: F403
from .pix_set import *  # noqa: F403
from .token import *  # noqa: F403
