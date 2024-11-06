<div align=center>

<img width="250" height="312" src="https://github.com/HibiKier/nonebot-plugin-zxreport/blob/main/docs_image/tt.jpg"/>

</div>

<div align="center">

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>


# nonebot-plugin-zxpix

_✨ 基于 [NoneBot2](https://github.com/nonebot/nonebot2) 的一个插件 ✨_

![python](https://img.shields.io/badge/python-v3.9%2B-blue)
![nonebot](https://img.shields.io/badge/nonebot-v2.1.3-yellow)
![onebot](https://img.shields.io/badge/onebot-v11-black)
[![license](https://img.shields.io/badge/license-AGPL3.0-FE7D37)](https://github.com/HibiKier/zhenxun_bot/blob/main/LICENSE)

</div>

## 📖 介绍

<div align="center">

🎉 __这是一个公开的图库API，希望大家共同维护，看看你的xp(bushi__ 🎉

</div>

[小真寻](https://github.com/HibiKier/zhenxun_bot)会将你的xp分享给其他人！  
通过提交的 __PID__， __UID__， ~~__关键词__~~ 来收录图片  
为保证质量， __UID__ 收录只会保存收藏数大于 __450__ 的图片


> [!NOTE]
>
> <div align="center"><b>小真寻也很可爱呀，也会很喜欢你！</b></div>
>
> <div align="center"><img width="250" height="250" src="https://github.com/HibiKier/nonebot-plugin-zxpm/blob/main/docs_image/tt3.png"/><img width="250" height="250" src="https://github.com/HibiKier/nonebot-plugin-zxpm/blob/main/docs_image/tt1.png"/><img width="250" height="250" src="https://github.com/HibiKier/nonebot-plugin-zxpm/blob/main/docs_image/tt2.png"/></div>

## 📈 统计

<div align="center">

![stat](http://pix.zhenxun.org/pix/stat?t=9)

</div>

## 💿 安装

```python
pip install nonebot-plugin-zxpix
```

```python
nb plugin install nonebot-plugin-zxpix
```

## 💿 配置
| 配置                       | 类型  |          默认值          | 说明                                                                              |
| :------------------------- | :---: | :----------------------: | --------------------------------------------------------------------------------- |
| zxpix_api                  |  str  | http://pix.zhenxun.org | zhenxun-pix-api地址                                                               |
| zxpix_image_size           |  str  |         large          | ["large", "medium", "original", "square_medium"]图片大小，当使用zxpix_nginx时无效 |
| zxpix_timeout              |  int  |            10            | 请求时长                                                                          |
| zxpix_show_info            | bool  |           true           | 显示图片的uid，pid，标题                                                          |
| zxpix_allow_group_r18      | bool  |          false           | 允许群组中使用-r参数                                                              |
| zxpix_system_proxy         |  str  |           None           | 系统代理                                                                          |
| zxpix_max_once_num2forward |  int  |            0             | 多于该数量的图片时使用转发消息，0为不使用                                         |
| zxpix_nginx                |  str  |         pixiv.re         | 反代地址                                                                     |
| zxpix_small_nginx                |  str  |         i.suimoe.com         | 缩略图反代地址                                                                        |
| zxpix_image_to_bytes       | bool  |          false           | 是否将图片转换为bytes发送                                                         |

## 🎁 使用


```python

pix ?*[tags] ?[-n 1]: 通过 tag 获取相似图片，不含tag时随机抽取, tag也可以是uid和pid
            -n表示数量, -r表示查看r18, -noai表示过滤ai
    示例：pix 萝莉 白丝
    示例：pix 萝莉 白丝 -n 10  （10为数量）
    示例：pix 13929393-1   查看pid为13929393的第1张的图片（多图时）
    示例：pix 121323322    查看uid或pid为121323322的图片

pix图库 ?[tags](使用空格分隔): 查看pix图库数量

pix添加 ['u', 'p'] [content]
        u: uid
        p: pid

    示例:
        pix添加 u 123456789
        pix添加 p 123456789

以下block与nsfw设置仅仅提交一个请求，需要图库管理员审核

引用 /original : 下载原图
引用 /info : 引用图片查看图片信息
引用 /block ?[-u]: 提交图片block请求，存在-u时将block该uid下所有图片
引用 /nsfw n: 设置图片nsfw，n在[0, 1, 2]之间
    0: 普通
    1: 色图
    2: r18

引用消息 /star     : 收藏图片
引用消息 /unatar   : 取消收藏图片
pix收藏           : 查看个人收藏
pix排行 ?[10] -r: 查看收藏排行, 默认获取前10，包含-r时会获取包括r18在内的排行
```

## ❤ 感谢

- 可爱的小真寻 Bot [`zhenxun_bot`](https://github.com/HibiKier/zhenxun_bot): 我谢我自己，桀桀桀
