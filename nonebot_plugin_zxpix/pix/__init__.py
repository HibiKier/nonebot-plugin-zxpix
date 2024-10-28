from nonebot import logger
from nonebot.adapters import Bot
from httpx import HTTPStatusError
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_alconna import (
    Args,
    Query,
    Option,
    Alconna,
    Arparma,
    MultiVar,
    on_alconna,
    store_true,
)

from ..utils import MessageUtils
from .data_source import PixManage, config

_matcher = on_alconna(
    Alconna(
        "pix",
        Args["tags?", MultiVar(str)],
        Option("-n|--num", Args["num", int]),
        Option("-r|--r18", action=store_true, help_text="是否是r18"),
        Option("-noai", action=store_true, help_text="是否是过滤ai"),
    ),
    aliases={"PIX"},
    priority=5,
    block=True,
)


@_matcher.handle()
async def _(
    bot: Bot,
    session: Uninfo,
    arparma: Arparma,
    tags: Query[tuple[str, ...]] = Query("tags", ()),
    num: Query[int] = Query("num", 1),
):
    allow_group_r18 = config.zxpix_allow_group_r18
    is_r18 = arparma.find("r18")
    if (
        not allow_group_r18
        and session.group
        and is_r18
        and session.user.id not in bot.config.superusers
    ):
        await MessageUtils.build_message("给我滚出克私聊啊变态！").finish()
    is_ai = arparma.find("noai") or None
    try:
        result = await PixManage.get_pix(tags.result, num.result, is_r18, is_ai)
        if not result.suc:
            await MessageUtils.build_message(result.info).send()
    except HTTPStatusError as e:
        logger.error(f"pix图库API出错... {type(e)}: {e}")
        await MessageUtils.build_message("pix图库API出错啦！").finish()
    if not result.data:
        await MessageUtils.build_message("没有找到相关tag/pix/uid的图片...").finish()
    max_once_num2forward = config.zxpix_max_once_num2forward
    if (
        max_once_num2forward
        and max_once_num2forward <= len(result.data)
        and session.group
    ):
        message_list = []
        for r in result.data:
            message_list.append(await PixManage.get_pix_result(r))
        await MessageUtils.alc_forward_msg(
            message_list, session.user.id, next(iter(bot.config.nickname))
        ).send()
    else:
        for r in result.data:
            message = await PixManage.get_pix_result(r)
            await MessageUtils.build_message(message).send()
    logger.info(f"pix调用 tags: {tags.result}")
