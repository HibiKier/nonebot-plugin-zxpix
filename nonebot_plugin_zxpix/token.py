import nonebot
from nonebot import logger

from ._config import config, token
from .utils import AsyncHttpx

driver = nonebot.get_driver()


@driver.on_startup
async def _():
    if not token.token:
        base_api = f"{config.zxpix_api}/pix/token"
        res = await AsyncHttpx.post(base_api)
        if res.status_code != 200:
            logger.warning(f"获取PIX token失败, code: {res.status_code}")
            return
        res_data = res.json()
        token.save(f"{res_data['token_type']} {res_data['access_token']}")
        logger.info(f"成功生成PIX token: {res_data['access_token']}")
