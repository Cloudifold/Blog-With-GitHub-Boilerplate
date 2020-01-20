# -*- coding: utf-8 -*-
"""博客构建配置文件
"""

# For Maverick
site_prefix = "/MyBlog/"
source_dir = "../src/"
build_dir = "../dist/"
index_page_size = 10
archives_page_size = 20
enable_jsdelivr = {
    "enabled": True,
    "repo": "Cloudifold/MyBlog@gh-pages"
}

# 站点设置
site_name = "CLD's BLOG"
site_logo = "${static_prefix}logo.png"
site_build_date = "2019-12-18T16:51+08:00"
author = "CLD"
email = "hi@imalan.cn"
author_homepage = "MyBlog"
description = "test des"
key_words = [ 'Galileo', 'blog']
language = 'zh-CN'
external_links = [
    {
        "name": "Maverick",
        "url": "https://github.com/AlanDecode/Maverick",
        "brief": "🏄‍ Go My Own Way."
    },
    {
        "name": "朋友们",
        "url": "${site_prefix}friends/",
        "brief": "cldfd的朋友们"
    }
]
nav = [
    {
        "name": "首页",
        "url": "${site_prefix}",
        "target": "_self"
    },
    {
        "name": "归档",
        "url": "${site_prefix}archives/",
        "target": "_self"
    },
    {
        "name": "关于",
        "url": "${site_prefix}about/",
        "target": "_self"
    },
    {
        "name": "友链",
        "url": "${site_prefix}friends/",
        "target": "_self"
    }
]

social_links = [
    {
        "name": "Twitter",
        "url": "",
        "icon": "gi gi-twitter"
    },
    {
        "name": "GitHub",
        "url": "https://github.com/Cloudifold",
        "icon": "gi gi-github"
    },
    {
        "name": "Weibo",
        "url": "",
        "icon": "gi gi-weibo"
    }
]

head_addon = r'''
<meta http-equiv="x-dns-prefetch-control" content="on">
<link rel="dns-prefetch" href="//cdn.jsdelivr.net" />
'''

footer_addon = ''

body_addon = ''
