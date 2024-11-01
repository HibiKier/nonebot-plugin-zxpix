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
from nonebot_plugin_uninfo import Uninfo

from .._config import InfoManage
from ..utils import MessageUtils, get_platform
from .data_source import StarManage


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


_star_matcher = on_alconna(
    Alconna(["/"], "star"),
    priority=5,
    block=True,
    use_cmd_start=False,
    rule=reply_check(),
)

_unstar_matcher = on_alconna(
    Alconna(["/"], "unstar"),
    priority=5,
    block=True,
    use_cmd_start=False,
    rule=reply_check(),
)

_my_matcher = on_alconna(
    Alconna("pix收藏"),
    priority=5,
    block=True,
)

_rank_matcher = on_alconna(
    Alconna(
        "pix排行",
        Args["num?", int],
        Option("-r|--r18", action=store_true, help_text="是否包含r18"),
    ),
    priority=5,
    block=True,
)


@_star_matcher.handle()
async def _(bot: Bot, event: Event, session: Uninfo, arparma: Arparma):
    reply: Reply | None = await reply_fetch(event, bot)
    if reply and (pix_model := InfoManage.get(str(reply.id))):
        platform = get_platform(session)
        try:
            result = await StarManage.star_set(
                pix_model, f"{platform}-{session.user.id}", True
            )
        except HTTPStatusError as e:
            logger.error(f"pix图库API出错... {type(e)}: {e}")
            await MessageUtils.build_message(
                f"pix图库API出错啦！ code: {e.response.status_code}"
            ).finish()
        logger.info(
            f"pix收藏图片: {pix_model.pid}", arparma.header_result, session=session
        )
        await MessageUtils.build_message(result).finish(reply_to=True)
    await MessageUtils.build_message("没有找到该图片相关信息或数据已过期...").finish(
        reply_to=True
    )


@_unstar_matcher.handle()
async def _(bot: Bot, event: Event, session: Uninfo, arparma: Arparma):
    reply: Reply | None = await reply_fetch(event, bot)
    if reply and (pix_model := InfoManage.get(str(reply.id))):
        platform = get_platform(session)
        try:
            result = await StarManage.star_set(
                pix_model, f"{platform}-{session.user.id}", False
            )
        except HTTPStatusError as e:
            logger.error(f"pix图库API出错... {type(e)}: {e}")
            await MessageUtils.build_message(
                f"pix图库API出错啦！ code: {e.response.status_code}"
            ).finish()
        logger.info(
            f"pix取消收藏图片: {pix_model.pid}", arparma.header_result, session=session
        )
        await MessageUtils.build_message(result).finish(reply_to=True)
    await MessageUtils.build_message("没有找到该图片相关信息或数据已过期...").finish(
        reply_to=True
    )


@_my_matcher.handle()
async def _(session: Uninfo, arparma: Arparma):
    platform = get_platform(session)
    try:
        result = await StarManage.my_star(f"{platform}-{session.user.id}")
    except HTTPStatusError as e:
        logger.error(f"pix图库API出错... {type(e)}: {e}")
        await MessageUtils.build_message(
            f"pix图库API出错啦！ code: {e.response.status_code}"
        ).finish()
    logger.info("pix查看收藏", arparma.header_result, session=session)
    await MessageUtils.build_message(result).finish(reply_to=True)


@_rank_matcher.handle()
async def _(
    bot: Bot, session: Uninfo, arparma: Arparma, num: Query[int] = Query("num", 10)
):
    try:
        result_list = await StarManage.star_rank(num.result, arparma.find("r18"))
    except HTTPStatusError as e:
        logger.error(f"pix图库API出错... {type(e)}: {e}")
        await MessageUtils.build_message(
            f"pix图库API出错啦！ code: {e.response.status_code}"
        ).finish()
    if isinstance(result_list, str):
        await MessageUtils.build_message(result_list).finish(reply_to=True)
    if session.group:
        await MessageUtils.alc_forward_msg(
            result_list,
            session.user.id,
            next(iter(bot.config.nickname)),
        ).send()
    else:
        for r in result_list:
            await MessageUtils.build_message(r).send()
    logger.info("pix查看收藏排行", arparma.header_result, session=session)
