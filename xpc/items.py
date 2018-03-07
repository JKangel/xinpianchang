# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class PostItem(scrapy.Item):
    """保存视频信息的item"""
    table_name = 'posts'
    pid = Field()
    title = Field()
    thumbnail = Field()
    preview = Field()
    video = Field()
    # 类别
    category = Field()
    created_at = Field()
    play_counts = Field()
    like_counts = Field()
    description = Field()
    video_format = Field()

class CommentItem(scrapy.Item):
    table_name = 'comments'
    commentid = Field()
    pid = Field()
    cid = Field()
    avatar = Field()
    uname = Field()
    created_at = Field()
    content = Field()
    like_counts = Field()
    reply = Field()


class ComposerItem(scrapy.Item):
    table_name = 'composers'
    cid = Field()
    # 背景
    banner = Field()
    # 头像
    avatar = Field()
    # 认证
    verified = Field()
    # 名字
    name = Field()
    # 简介
    intro = Field()
    # 人气
    like_counts = Field()
    # 粉丝
    fans_counts = Field()
    # 关注
    follow_counts = Field()

class CopyrightItem(scrapy.Item):
    table_name = 'copyrights'
    pcid = Field()
    pid = Field()
    cid = Field()
    roles = Field()
