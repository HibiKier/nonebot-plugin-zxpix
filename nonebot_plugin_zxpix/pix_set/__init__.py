from httpx import HTTPStatusError
from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot.rule import Rule
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    Arparma,
    Option,
    Query,
    Reply,
    on_alconna,
    store_true,
)
from nonebot_plugin_alconna.uniseg.tools import reply_fetch
from nonebot_plugin_apscheduler import scheduler

from .._config import InfoManage
from ..utils import MessageUtils
from .data_source import PixManage


def reply_check() -> Rule:
    """
    检查是否存在回复消息

    返回:
        Rule: Rule
    """

    async def _rule(bot: Bot, event: Event):
        if event.get_type() == "message":
            return bool(await reply_fetch(event, bot))
        return False

    return Rule(_rule)


_info_matcher = on_alconna(
    Alconna(["/"], "info"),
    priority=5,
    block=True,
    use_cmd_start=False,
    rule=reply_check(),
)

_block_matcher = on_alconna(
    Alconna(
        ["/"],
        "block",
        Args["level?", [1, 2]],
        Option("-u|--uid", action=store_true, help_text="是否是uid"),
        Option("--all", action=store_true, help_text="全部"),
    ),
    priority=5,
    block=True,
    use_cmd_start=False,
    rule=reply_check(),
)

_nsfw_matcher = on_alconna(
    Alconna(["/"], "nsfw", Args["n", int]),
    priority=5,
    block=True,
    use_cmd_start=False,
    rule=reply_check(),
)


@_info_matcher.handle()
async def _(bot: Bot, event: Event):
    reply: Reply | None = await reply_fetch(event, bot)
    if reply and (pix_model := InfoManage.get(str(reply.id))):
        result = f"""title: {pix_model.title}
author: {pix_model.author}
pid: {pix_model.pid}-{pix_model.img_p}
uid: {pix_model.uid}
收藏数:{pix_model.total_bookmarks}
nsfw: {pix_model.nsfw_tag}
tags: {pix_model.tags}
url: {pix_model.url}""".strip()
        await MessageUtils.build_message(result).finish(reply_to=True)
    await MessageUtils.build_message("没有找到该图片相关信息或数据已过期...").finish(
        reply_to=True
    )


@_block_matcher.handle()
async def _(
    bot: Bot, event: Event, arparma: Arparma, level: Query[int] = Query("level", 2)
):
    reply: Reply | None = await reply_fetch(event, bot)
    if reply and (pix_model := InfoManage.get(str(reply.id))):
        try:
            result = await PixManage.block_pix(
                pix_model, level.result, arparma.find("uid"), arparma.find("all")
            )
        except HTTPStatusError as e:
            logger.error(f"pix图库API出错 code: {e.response.status_code}...")
            await MessageUtils.build_message(
                f"pix图库API出错啦！ code: {e.response.status_code}"
            ).finish()
        await MessageUtils.build_message(result).finish(reply_to=True)
    await MessageUtils.build_message("没有找到该图片相关信息或数据已过期...").finish(
        reply_to=True
    )


@_nsfw_matcher.handle()
async def _(bot: Bot, event: Event, n: int):
    reply: Reply | None = await reply_fetch(event, bot)
    if reply and (pix_model := InfoManage.get(str(reply.id))):
        if n not in [0, 1, 2]:
            await MessageUtils.build_message(
                "nsfw参数错误，必须在 [0, 1, 2] 之间..."
            ).finish(reply_to=True)
        try:
            result = await PixManage.set_nsfw(pix_model, n)
        except HTTPStatusError as e:
            logger.error(f"pix图库API出错 code: {e.response.status_code}...")
            await MessageUtils.build_message(
                f"pix图库API出错啦！ code: {e.response.status_code}"
            ).finish()
        await MessageUtils.build_message(result).finish(reply_to=True)
    await MessageUtils.build_message("没有找到该图片相关信息或数据已过期...").finish(
        reply_to=True
    )


@scheduler.scheduled_job(
    "interval",
    hours=6,
)
async def _():
    InfoManage.remove()
    logger.debug("自动移除过期图片数据...")
