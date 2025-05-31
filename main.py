#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/10/10
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : main
# @Software: PyCharm

import uvicorn

from constants.constants import Constants
from setting.setting import get_we0_index_settings

if __name__ == '__main__':
    sider_settings = get_we0_index_settings()
    uvicorn.run(
        'launch.launch:app',
        host=sider_settings.server.host,
        port=sider_settings.server.port,
        reload=sider_settings.server.reload,
        env_file=Constants.Path.ENV_FILE_PATH
    )
