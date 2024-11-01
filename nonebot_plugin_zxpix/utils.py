from io import BytesIO
from pathlib import Path
from typing import Any, ClassVar

import aiofiles
import httpx
from httpx import ConnectTimeout, HTTPStatusError, Response
from nonebot import logger
from nonebot.adapters import Bot
from nonebot_plugin_alconna import (
    At,
    AtAll,
    CustomNode,
    Image,
    Reference,
    Text,
    UniMessage,
    Video,
    Voice,
)
from nonebot_plugin_uninfo import Uninfo, get_interface

from ._config import config


def get_platform(t: Bot | Uninfo) -> str:
    """获取平台

    参数:
        bot: Bot

    返回:
        str | None: 平台
    """
    if isinstance(t, Bot):
        if interface := get_interface(t):
            info = interface.basic_info()
            platform = info["scope"].lower()
            return "qq" if platform.startswith("qq") else platform
    else:
        platform = t.basic["scope"].lower()
        return "qq" if platform.startswith("qq") else platform
    return "unknown"


class AsyncHttpx:
    proxy: ClassVar[dict[str, str | None]] = {
        "http://": config.zxpix_system_proxy,
        "https://": config.zxpix_system_proxy,
    }

    @classmethod
    async def get(
        cls,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        timeout: int = 30,
        **kwargs,
    ) -> Response:
        """
        说明:
            Post

        参数:
            url: url
            params: params
            headers: 请求头
            cookies: cookies
            verify: verify
            use_proxy: 使用默认代理
            proxy: 指定代理
            timeout: 超时时间
        """
        _proxy = proxy or (cls.proxy if use_proxy else None)
        async with httpx.AsyncClient(proxies=_proxy, verify=verify) as client:  # type: ignore
            return await client.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )

    @classmethod
    async def post(
        cls,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        content: Any = None,
        files: Any = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        timeout: int = 30,
        **kwargs,
    ) -> Response:
        """
        说明:
            Post
        参数:
            url: url
            data: data
            content: content
            files: files
            use_proxy: 是否默认代理
            proxy: 指定代理
            json: json
            params: params
            headers: 请求头
            cookies: cookies
            timeout: 超时时间
        """
        _proxy = proxy or (cls.proxy if use_proxy else None)
        async with httpx.AsyncClient(proxies=_proxy, verify=verify) as client:  # type: ignore
            return await client.post(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )

    @classmethod
    async def download_file(
        cls,
        url: str | list[str],
        path: str | Path,
        *,
        params: dict[str, str] | None = None,
        verify: bool = True,
        use_proxy: bool = True,
        proxy: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        timeout: int = 30,
        follow_redirects: bool = True,
        **kwargs,
    ) -> bool:
        """下载文件

        参数:
            url: url
            path: 存储路径
            params: params
            verify: verify
            use_proxy: 使用代理
            proxy: 指定代理
            headers: 请求头
            cookies: cookies
            timeout: 超时时间
        """

        if isinstance(path, str):
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if not isinstance(url, list):
                url = [url]
            cur_proxy = proxy or (cls.proxy if use_proxy else None)
            async with httpx.AsyncClient(proxies=cur_proxy, verify=verify) as client:  # type: ignore
                for u in url:
                    try:
                        response = await client.get(
                            u,
                            params=params,
                            headers=headers,
                            cookies=cookies,
                            timeout=timeout,
                            follow_redirects=follow_redirects,
                            **kwargs,
                        )
                        response.raise_for_status()
                        content = response.content
                        async with aiofiles.open(path, "wb") as wf:
                            await wf.write(content)
                            logger.info(f"下载 {u} 成功.. Path：{path.absolute()}")
                        return True
                    except (TimeoutError, ConnectTimeout, HTTPStatusError) as e:
                        logger.warning(
                            f"下载 {u} 失败.. 尝试下一个地址.. {type(e)}: {e}"
                        )
            logger.error(f"下载 {url} 下载超时.. Path：{path.absolute()}")
        except Exception as e:
            logger.error(f"下载 {url} 错误 Path：{path.absolute()} & {type(e)}: {e}")
        return False


MESSAGE_TYPE = (
    str
    | int
    | float
    | Path
    | bytes
    | BytesIO
    | At
    | AtAll
    | Image
    | Text
    | Voice
    | Video
)


class MessageUtils:
    @classmethod
    def __build_message(cls, msg_list: list[MESSAGE_TYPE]) -> list[Text | Image]:
        """构造消息

        参数:
            msg_list: 消息列表

        返回:
            list[Text | Text]: 构造完成的消息列表
        """
        message_list = []
        for msg in msg_list:
            if isinstance(msg, Image | Text | At | AtAll | Video | Voice):
                message_list.append(msg)
            elif isinstance(msg, str | int | float):
                message_list.append(Text(str(msg)))
            elif isinstance(msg, Path):
                if msg.exists():
                    if config.zxpix_image_to_bytes:
                        with open(msg, "rb") as f:
                            message_list.append(Image(raw=f.read()))
                    else:
                        message_list.append(Image(path=msg))
                else:
                    logger.warning(f"图片路径不存在: {msg}")
            elif isinstance(msg, bytes):
                message_list.append(Image(raw=msg))
            elif isinstance(msg, BytesIO):
                message_list.append(Image(raw=msg))
        return message_list

    @classmethod
    def build_message(
        cls, msg_list: MESSAGE_TYPE | list[MESSAGE_TYPE | list[MESSAGE_TYPE]]
    ) -> UniMessage:
        """构造消息

        参数:
            msg_list: 消息列表

        返回:
            UniMessage: 构造完成的消息列表
        """
        message_list = []
        if not isinstance(msg_list, list):
            msg_list = [msg_list]
        for m in msg_list:
            _data = m if isinstance(m, list) else [m]
            message_list += cls.__build_message(_data)  # type: ignore
        return UniMessage(message_list)

    @classmethod
    def alc_forward_msg(
        cls,
        msg_list: list,
        uin: str,
        name: str,
    ) -> UniMessage:
        """生成自定义合并消息

        参数:
            msg_list: 消息列表
            uin: 发送者 QQ
            name: 自定义名称

        返回:
            list[dict]: 转发消息
        """
        node_list = []
        for _message in msg_list:
            if isinstance(_message, list):
                for i in range(len(_message.copy())):
                    if isinstance(_message[i], Path):
                        with open(_message[i], "rb") as f:
                            _message[i] = Image(raw=f.read())
            node_list.append(
                CustomNode(uid=uin, name=name, content=UniMessage(_message))
            )
        return UniMessage(Reference(nodes=node_list))
