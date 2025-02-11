import asyncio
import random
from pathlib import Path

import nonebot_plugin_localstore as store
from nonebot import logger

from .._config import PixModel, PixResult, config, token
from ..utils import AsyncHttpx

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6;"
    " rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Referer": "https://www.pixiv.net/",
}
TEMP_PATH = store.get_plugin_cache_dir()


class StarManage:
    @classmethod
    async def star_set(cls, pix: PixModel, user_id: str, is_star: bool) -> str:
        """block pix

        参数:
            pix: pixModel
            is_uid: 是否为uid

        返回:
            str: 返回信息
        """
        if is_star:
            api = f"{config.zxpix_api}/pix/star"
        else:
            api = f"{config.zxpix_api}/pix/unstar"
        json_data = {"pid": f"{pix.pid}-{pix.img_p}", "user_id": user_id}
        logger.debug(f"尝试调用pix api: {api}, 参数: {json_data}")
        headers = {"Authorization": token.token} if token.token else None
        res = await AsyncHttpx.post(api, json=json_data, headers=headers)
        res.raise_for_status()
        return f"⭐{PixResult(**res.json()).info}"

    @classmethod
    async def my_star(cls, user_id: str) -> str:
        """block pix

        参数:
            pix: pixModel
            is_uid: 是否为uid

        返回:
            str: 返回信息
        """
        api = f"{config.zxpix_api}/pix/get_user_star_list"
        json_data = {"user_id": user_id}
        logger.debug(f"尝试调用pix api: {api}, 参数: {json_data}")
        headers = {"Authorization": token.token} if token.token else None
        res = await AsyncHttpx.get(api, params=json_data, headers=headers)
        res.raise_for_status()
        data = PixResult(**res.json())
        return ("当前收藏:\n" + "，".join(data.data))[:-1] if data.suc else data.info

    @classmethod
    async def star_rank(cls, num: int, contain_r18: bool) -> list | str:
        """获取rank列表

        参数:
            num: 数量
            contain_r18: 是否包含r18

        返回:
            list | str: 返回信息
        """
        nsfw_tag = [0, 1, 2] if contain_r18 else [0, 1]
        api = f"{config.zxpix_api}/pix/star_rank"
        json_data = {"nsfw": nsfw_tag, "num": num}
        logger.debug(f"尝试调用pix api: {api}, 参数: {json_data}")
        headers = {"Authorization": token.token} if token.token else None
        res = await AsyncHttpx.post(api, json=json_data, headers=headers)
        res.raise_for_status()
        data: PixResult = PixResult(**res.json())
        if not data.suc:
            return data.info
        data.data = [PixModel(**pix) for pix in data.data]
        task_list = [asyncio.create_task(cls.get_image(pix)) for pix in data.data]
        result = await asyncio.gather(*task_list)
        message_list = []
        for i in range(len(data.data)):
            pix: PixModel = data.data[i]
            img = result[i] or "这张图片下载失败了..."
            message_list.append(
                [
                    f"rank: {i+1}\npid: {pix.pid}\nuid: {pix.title}\nstar: {pix.star}",
                    img,
                ]
            )
        return message_list

    @classmethod
    async def get_image(cls, pix: PixModel) -> Path | None:
        """获取图片

        参数:
            pix: PixGallery
            is_original: 是否下载原图

        返回:
            Path | None: 图片路径
        """
        url = pix.url
        if small_url := config.zxpix_small_nginx:
            if "img-master" in url:
                url = "img-master" + url.split("img-master")[-1]
            elif "img-original" in url:
                url = "img-original" + url.split("img-original")[-1]
            url = f"https://{small_url}/{url}"
        file = TEMP_PATH / f"pix_{pix.pid}_{random.randint(1, 1000)}.png"
        try:
            return (
                file
                if await AsyncHttpx.download_file(
                    url, file, headers=headers, timeout=config.zxpix_timeout
                )
                else None
            )
        except Exception as e:
            logger.error(f"pix下载图片失败 {type(e)}: {e}")
        return None
