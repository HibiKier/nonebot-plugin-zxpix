from httpx import HTTPStatusError
from nonebot import logger
from nonebot_plugin_alconna import Alconna, Args, Arparma, on_alconna
from nonebot_plugin_uninfo import Uninfo

from .._enum import KwType
from ..utils import MessageUtils
from .data_source import KeywordManage

_add_matcher = on_alconna(
    Alconna(
        "pix添加",
        Args["add_type", ["u", "p"]]["content", str],
    ),
    priority=5,
    block=True,
)


@_add_matcher.handle()
async def _(
    session: Uninfo,
    arparma: Arparma,
    add_type: str,
    content: str,
):
    try:
        if add_type == "u":
            result = await KeywordManage.add_content(content, KwType.UID)
        elif add_type == "p":
            result = await KeywordManage.add_content(content, KwType.PID)
        else:
            result = await KeywordManage.add_content(content, KwType.KEYWORD)
        await MessageUtils.build_message(result).send()
    except HTTPStatusError as e:
        logger.error(f"pix图库API出错... {type(e)}: {e}")
        await MessageUtils.build_message("pix图库API出错啦！").finish()
    logger.info(f"PIX 添加结果: {result}", arparma.header_result, session=session)
