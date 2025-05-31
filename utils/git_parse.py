#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/4/27
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : git_parse
# @Software: PyCharm


import re


def parse_git_url(git_url):
    # 支持的平台域名
    platforms = [
        'github.com',
        'gitlab.com',
        'gitee.com',
        'bitbucket.org',
        'codeberg.org'
    ]

    # 支持的URL模式
    patterns = [
        # SSH格式: git@github.com:owner/repo
        r'^git@([^:]+):([^/]+)/([^/.]+)(?:\.git)?$',

        # HTTP/HTTPS格式: http(s)://github.com/owner/repo
        r'^https?://([^/]+)/([^/]+)/([^/.]+)(?:\.git)?$'
    ]

    # 去除可能的空白
    url = git_url.strip() if git_url else ''

    # 遍历匹配模式
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            domain, owner, repo = match.groups()
            if domain.lower() in platforms:
                return domain, owner, repo

    return None, None, None


if __name__ == '__main__':

    # 测试用例
    test_urls = [
        # SSH协议
        'git@github.com:we0-dev/we0',
        'git@github.com:we0-dev/we0.git',

        # HTTP协议
        'http://github.com/we0-dev/we0',
        'http://github.com/we0-dev/we0.git',

        # HTTPS协议
        'https://github.com/we0-dev/we0',
        'https://github.com/we0-dev/we0.git',

        # 其他平台
        'git@gitlab.com:group/project',
        'http://gitlab.com/group/project',
        'https://gitee.com/username/repo',

        # 无效的URL
        'we0-dev/we0',  # 不完整
        'github.com/we0-dev/we0',  # 缺少协议
        'https://example.com/we0-dev/we0'  # 非支持的平台
    ]

    for test_url in test_urls:
        result = parse_git_url(test_url)
        print(f"URL: {test_url}")
        print(f"Parsed: {result}\n")
