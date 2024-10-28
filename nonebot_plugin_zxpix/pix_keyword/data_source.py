from nonebot import logger

from .._config import PixResult, config, token
from .._enum import KwType
from ..utils import AsyncHttpx


class KeywordManage:
    @classmethod
    async def add_content(cls, content: str, kw_type: KwType) -> str:
        """添加pix

        参数:
            content: 关键词
            kw_type: 类型

        返回:
            str: 返回信息
        """
        api = f"{config.zxpix_api}/pix/pix_add"
        json_data = {"content": content, "add_type": kw_type}
        logger.debug(f"尝试调用pix api: {api}, 参数: {json_data}")
        headers = None
        headers = {"Authorization": token.token} if token.token else None
        res = await AsyncHttpx.post(api, json=json_data, headers=headers)
        res.raise_for_status()
        return PixResult(**res.json()).info
