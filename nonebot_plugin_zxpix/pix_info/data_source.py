from nonebot import logger

from .._config import config, token
from ..utils import AsyncHttpx
from .config import ImageCount


class InfoManage:
    @classmethod
    async def get_pix_gallery(cls, tags: tuple[str, ...]) -> str:
        """查看pix图库

        参数:
            tags: tags列表

        返回:
            BuildImage: 图片
        """
        api = f"{config.zxpix_api}/pix/pix_gallery_count"
        json_data = {"tags": tags}
        logger.debug(f"尝试调用pix api: {api}, 参数: {json_data}")
        headers = {"Authorization": token.token} if token.token else None
        res = await AsyncHttpx.post(api, json=json_data, headers=headers)
        res.raise_for_status()
        data = ImageCount(**res.json()["data"])
        return f"""
总数: {data.count}
普通: {data.normal}
涩图: {data.setu}
R18: {data.r18}
AI: {data.ai}
    """.strip()
