# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request
from xpc.items import PostItem, CommentItem, ComposerItem, CopyrightItem

# 评论网址
comment_api = 'http://www.xinpianchang.com/article/filmplay/ts-getCommentApi/id-%s/page-1'
vip_map = {
        'yellow-v':1,
        'bule-v':2
    }

# 去除数字中的符号(逗号)
def ci(s):
    if isinstance(s,int):
        return s
    return int(s.replace(',','')) if s else 0



class DiscoverySpider(scrapy.Spider):
    name = 'discovery'
    root_url = 'http://www.xinpianchang.com'
    allowed_domains = ['www.xinpianchang.com']
    # start_urls = ['http://www.xinpianchang.com/channel/index/id-0/sort-like/type-0']
    start_urls = ['http://www.xinpianchang.com/channel/index/id-0/sort-like/type-0?from=articleListPage']

    def parse(self, response):
        # 每个网页的请求网址
        post_url = 'http://www.xinpianchang.com/a%s?from=ArticleList'
        # 每页作品的列表
        post_list = response.xpath('//ul[@class="video-list"]/li')
        for post in post_list:
            post_id = post.xpath('./@data-articleid').extract_first()
            thumbnail = post.xpath('./a/img/@_src').get()
            # post_title = post.xpath('./div[@class="video-con"]/a/p/text()').get()
            # print(post_title,post_url % post_id)
            # 每个网址拼接id作为request对象 回调函数是self.parse_post
            request = Request(post_url % post_id,callback=self.parse_post)
            # request中meta参数的作用是传递信息给下一个函数，即把需要传递的信息赋值给这个叫meta的变量，meta只接收字典类型的赋值
            request.meta['pid'] = post_id
            request.meta['thumbnail'] = thumbnail
            # yield迭代器  相当于多次返回一个list  如果返回包含成千上百个元素的list，会占用很多计算机的资源和时间，用yield很好的缓解了这种情况
            yield request

        # 下一页的xpath
        next_page = response.xpath('//div[@class="page"]/a[last()]/@href').get()
        # 如果下一页不为空
        if next_page:
            # 一直执行
            yield response.follow(next_page,callback=self.parse)

    def parse_post(self,response):
        post = PostItem()
        # 将所有数据爬取
        post['pid'] = response.meta['pid']
        post['thumbnail'] = response.meta['thumbnail']
        post['title'] = response.xpath('//div[@class="title-wrap"]/h3/text()').get()
        post['video'] = response.xpath('//video[@id="xpc_video"]/@src').get()
        post['video_format'] = ''
        #预览图
        post['preview'] =response.xpath('//div[@class="filmplay"]//img/@src').get()
        # 类别
        post['category'] = response.xpath('//span[@class="cate v-center"]/text()').get()
        post['created_at'] = response.xpath('//span[contains(@class,"update-time")]/i/text()').get()
        post['play_counts'] = ci(response.xpath('//i[contains(@class,"play-counts")]/@data-curplaycounts').get())
        post['like_counts'] = ci(response.xpath('//span[contains(@class,like-counts)]/@data-counts').get())
        post['description'] = response.xpath('//p[contains(@class,"desc")]/text()').get()

        yield post

        creator_list = response.xpath('//div[contains(@class,"filmplay-creator")]/ul[@class="creator-list"]/li')
        for creator  in creator_list:
            user_page = creator.xpath('./a/@href').get()
            user_id = creator.xpath('./a/@data-userid').get()
            request = Request('%s%s' % (self.root_url, user_page),callback=self.parse_composer)
            request.meta['cid'] = user_id
            yield request

            cr = CopyrightItem()
            cr['pid'] = response.meta['pid']
            cr['cid'] = user_id
            cr['pcid'] = '%s_%s' % (cr['pid'], cr['cid'])
            cr['roles'] = creator.xpath('.//span[contains(@class,"roles")]/text()').get()
            yield cr

        # 将post['pid']作为参数传入comment_api中 指定page参数为1，回调函数为self.parse_comment
        request = Request(comment_api %post['pid'], callback=self.parse_comment)
        request.meta['pid'] = post['pid']
        # request.meta['cur_page'] = 1
        yield request

    def parse_comment(self,response):
        if response.text:
            pid = response.meta['pid']
            # 下载页面的json数据
            result = json.loads(response.text)
            # 提取下一页的网址
            next_page = result['data']['next_page_url']
            if next_page:
                request = Request(next_page, callback=self.parse_comment)
                request.meta['pid'] = pid
                yield request

            comments = result['data']['list']
            for c in comments:
                comment = CommentItem()
                comment['commentid'] = c['commentid']
                comment['pid'] = pid
                comment['cid'] = c['userInfo']['userid']
                comment['uname'] = c['userInfo']['username']
                comment['avatar'] = c['userInfo']['face']
                comment['created_at'] = int(c['addtime_int'])
                comment['content'] = c['content']
                comment['like_counts'] = ci(c['count_approve'])
                if c['reply']:
                    comment['reply'] = c['reply']['commentid'] or 0
                yield comment

                request = Request('%s/u%s' % (self.root_url,comment['cid']),callback=self.parse_composer)
                request.meta['cid'] = comment['cid']
                yield request



    def parse_composer(self,response):
        composer = ComposerItem()
        composer['cid'] = response.meta['cid']
        composer['name'] = response.xpath('//p[contains(@class,"creator-name")]/text()').get()
        # 简介
        composer['intro'] = response.xpath('//p[contains(@class,"creator-desc")]/text()').get()
        # 背景
        composer['banner'] = response.xpath('//div[@class="banner-wrap"]/@style').get()
        if composer['banner']:
            # 提取样式中的图片链接
            composer['banner'] = composer['banner'][21:-1]
        elem = response.xpath('//span[@class="avator-wrap-s"]')
        # 头像
        composer['avatar'] = elem.xpath('./img/@src').get()
        auth_style = elem.xpath('./span/@class').get()
        if auth_style:
            #认证
            composer['verified'] = vip_map.get(auth_style.split(" ")[-1])
        # 人气
        composer['like_counts'] = ci(response.xpath('//span[contains(@class,"like-counts")]/text()').get())
        # 粉丝
        composer['fans_counts'] = ci(response.xpath('//span[contains(@class,"fans-counts")]/@data-counts').get())
        # 关注
        composer['follow_counts'] = ci(response.xpath('//span[@class="follow-wrap"]/span[last()]/text()').get())

        yield composer