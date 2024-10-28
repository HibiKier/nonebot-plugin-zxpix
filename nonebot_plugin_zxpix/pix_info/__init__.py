from nonebot import logger
from httpx import HTTPStatusError
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_alconna import Args, Query, Alconna, Arparma, MultiVar, on_alconna

from ..utils import MessageUtils
from .data_source import InfoManage

_matcher = on_alconna(
    Alconna(
        "pix图库",
        Args["tags?", MultiVar(str)],
    ),
    priority=5,
    block=True,
)


@_matcher.handle()
async def _(
    session: Uninfo,
    arparma: Arparma,
    tags: Query[tuple[str, ...]] = Query("tags", ()),
):
    try:
        result = await InfoManage.get_pix_gallery(tags.result)
    except HTTPStatusError as e:
        logger.error(f"pix图库API出错... {type(e)}: {e}")
        await MessageUtils.build_message("pix图库API出错啦！").finish()
    await MessageUtils.build_message(result).send(reply_to=True)
    logger.info(
        f"PIX 查看PIX图库 tags: {tags.result}", arparma.header_result, session=session
    )
