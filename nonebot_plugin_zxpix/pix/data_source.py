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


class PixManage:
    @classmethod
    async def get_pix(
        cls,
        tags: tuple[str, ...],
        num: int,
        is_r18: bool,
        ai: bool | None,
        nsfw: tuple[int, ...],
        ratio_tuple: list[float] | None,
    ) -> PixResult[list[PixModel]]:
        """获取图片

        参数:
            tags: tags，包含uid和pid
            num: 数量

        返回:
            list[PixGallery]: 图片数据列表
        """
        api = f"{config.zxpix_api}/pix/get_pix"
        json_data = {
            "tags": tags,
            "num": num,
            "r18": is_r18,
            "ai": ai,
            "size": config.zxpix_image_size,
            "nsfw_tag": nsfw or None,
            "ratio": ratio_tuple,
        }
        logger.debug(f"尝试调用pix api: {api}, 参数: {json_data}")
        headers = None
        headers = {"Authorization": token.token} if token.token else None
        res = await AsyncHttpx.post(api, json=json_data, headers=headers)
        res.raise_for_status()
        res_data = res.json()
        res_data["data"] = [PixModel(**item) for item in res_data["data"]]
        return PixResult[list[PixModel]](**res_data)

    @classmethod
    async def get_image(cls, pix: PixModel, is_original: bool = False) -> Path | None:
        """获取图片

        参数:
            pix: PixGallery
            is_original: 是否下载原图

        返回:
            Path | None: 图片路径
        """
        url = pix.url
        if "limit_sanity_level" in url or (is_original and config.zxpix_nginx):
            image_type = url.split(".")[-1]
            if pix.is_multiple:
                url = f"https://{config.zxpix_nginx}/"
                f"{pix.pid}-{int(pix.img_p) + 1}.{image_type}"
            else:
                url = f"https://{config.zxpix_nginx}/{pix.pid}.{image_type}"
        elif config.zxpix_small_nginx:
            if "img-master" in url:
                url = "img-master" + url.split("img-master")[-1]
            elif "img-original" in url:
                url = "img-original" + url.split("img-original")[-1]
            url = f"https://{config.zxpix_small_nginx}/{url}"
        file = TEMP_PATH / f"pix_{pix.pid}_{random.randint(1, 1000)}.png"
        return (
            file
            if await AsyncHttpx.download_file(
                url, file, headers=headers, timeout=config.zxpix_timeout
            )
            else None
        )

    @classmethod
    async def get_pix_result(cls, pix: PixModel) -> tuple[list, PixModel]:
        """构建返回消息

        参数:
            pix: PixGallery

        返回:
            list: 返回消息
        """
        if not (image := await cls.get_image(pix)):
            return [f"获取图片 pid: {pix.pid} 失败..."], pix
        message_list = []
        if config.zxpix_show_info:
            message_list.append(
                f"title: {pix.title}\n"
                f"author: {pix.author}\n"
                f"pid: {pix.pid}\nuid: {pix.uid}\n",
            )
        message_list.append(image)
        return message_list, pix
