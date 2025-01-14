import asyncio

from httpx import HTTPStatusError
from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot.rule import Rule
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    Arparma,
    MultiVar,
    Option,
    Query,
    Reply,
    on_alconna,
    store_true,
)
from nonebot_plugin_alconna.uniseg import Receipt
from nonebot_plugin_alconna.uniseg.tools import reply_fetch
from nonebot_plugin_uninfo import Uninfo

from .._config import InfoManage
from ..utils import MessageUtils
from .data_source import PixManage, config


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


_matcher = on_alconna(
    Alconna(
        "pix",
        Args["tags?", MultiVar(str)],
        Option("-n|--num", Args["num", int]),
        Option("-r|--r18", action=store_true, help_text="是否是r18"),
        Option("-noai", action=store_true, help_text="是否是过滤ai"),
        Option(
            "--nsfw",
            Args["nsfw_tag", MultiVar(int)],
            help_text="nsfw_tag，[0, 1, 2]",
        ),
        Option("--ratio", Args["ratio", str], help_text="图片比例，例如: 0.5,1.2"),
    ),
    aliases={"PIX"},
    priority=5,
    block=True,
)

_original_matcher = on_alconna(
    Alconna(["/"], "original"),
    priority=5,
    block=True,
    use_cmd_start=False,
    rule=reply_check(),
)


@_matcher.handle()
async def _(
    bot: Bot,
    session: Uninfo,
    arparma: Arparma,
    tags: Query[tuple[str, ...]] = Query("tags", ()),
    num: Query[int] = Query("num", 1),
    nsfw: Query[tuple[int, ...]] = Query("nsfw_tag", ()),
    ratio: Query[str] = Query("ratio", ""),
):
    if num.result > 10:
        await MessageUtils.build_message("最多一次10张哦...").finish()
    allow_group_r18 = config.zxpix_allow_group_r18
    is_r18 = arparma.find("r18")
    if (
        not allow_group_r18
        and session.group
        and (is_r18 or 2 in nsfw.result)
        and session.user.id not in bot.config.superusers
    ):
        await MessageUtils.build_message("给我滚出克私聊啊变态！").finish()
    is_ai = False if arparma.find("noai") else None
    ratio_tuple = None
    ratio_tuple_split = []
    if "," in ratio.result:
        ratio_tuple_split = ratio.result.split(",")
    elif "，" in ratio.result:
        ratio_tuple_split = ratio.result.split("，")
    if ratio_tuple_split and len(ratio_tuple_split) < 2:
        return await MessageUtils.build_message("比例格式错误，请输入x,y").finish()
    if ratio_tuple:
        ratio_tuple = [float(ratio_tuple_split[0]), float(ratio_tuple_split[1])]
    if nsfw.result:
        for n in nsfw.result:
            if n not in [0, 1, 2]:
                return await MessageUtils.build_message(
                    "nsfw_tag格式错误，请输入0,1,2"
                ).finish()
    try:
        result = await PixManage.get_pix(
            tags.result,
            num.result,
            is_r18,
            is_ai,
            nsfw.result,
            ratio_tuple,
        )
        if not result.suc:
            await MessageUtils.build_message(result.info).send()
    except HTTPStatusError as e:
        logger.error(f"pix图库API出错... {type(e)}: {e}")
        await MessageUtils.build_message("pix图库API出错啦！").finish()
    if not result.data:
        await MessageUtils.build_message("没有找到相关tag/pix/uid的图片...").finish()
    task_list = [asyncio.create_task(PixManage.get_pix_result(r)) for r in result.data]
    result_list = await asyncio.gather(*task_list)
    max_once_num2forward = config.zxpix_max_once_num2forward
    if (
        max_once_num2forward
        and max_once_num2forward <= len(result.data)
        and session.group
    ):
        await MessageUtils.alc_forward_msg(
            [r[0] for r in result_list],
            session.user.id,
            next(iter(bot.config.nickname)),
        ).send()
    else:
        for r, pix in result_list:
            receipt: Receipt = await MessageUtils.build_message(r).send()
            msg_id = receipt.msg_ids[0]["message_id"]
            InfoManage.add(str(msg_id), pix)
    logger.info(f"pix调用 tags: {tags.result}")
    logger.info(f"pix调用 tags: {tags.result}")


@_original_matcher.handle()
async def _(bot: Bot, event: Event):
    reply: Reply | None = await reply_fetch(event, bot)
    if reply and (pix_model := InfoManage.get(str(reply.id))):
        try:
            result = await PixManage.get_image(pix_model, True)
            if not result:
                await MessageUtils.build_message("下载图片数据失败...").finish()
        except HTTPStatusError as e:
            logger.error(f"pix图库API出错... {type(e)}: {e}")
            await MessageUtils.build_message(
                f"pix图库API出错啦！ code: {e.response.status_code}"
            ).finish()
        receipt: Receipt = await MessageUtils.build_message(result).send(reply_to=True)
        msg_id = receipt.msg_ids[0]["message_id"]
        InfoManage.add(str(msg_id), pix_model)
    else:
        await MessageUtils.build_message(
            "没有找到该图片相关信息或数据已过期..."
        ).finish(reply_to=True)
