#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/10/10
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : main
# @Software: PyCharm

import click
import uvicorn

from constants.constants import Constants
from launch.we0_index_mcp import we0_index_mcp
from setting.setting import get_we0_index_settings

@click.command()
@click.option('--mode', default='mcp', show_default=True, type=click.Choice(['mcp', 'fastapi']), required=True, help='Choose run mode: "mcp" or "fastapi".')
@click.option('--transport', default='streamable-http', show_default=True, type=click.Choice(['streamable-http', 'stdio', 'sse']), help='Transport protocol for MCP mode')
def main(mode, transport):
    sider_settings = get_we0_index_settings()

    if mode == 'mcp':
        we0_index_mcp.run(transport)
    elif mode == 'fastapi':
        uvicorn.run(
            'launch.launch:app',
            host=sider_settings.server.host,
            port=sider_settings.server.port,
            reload=sider_settings.server.reload,
            env_file=Constants.Path.ENV_FILE_PATH
        )
    else:
        raise ValueError(f"Unknown mode: {mode}")

if __name__ == '__main__':
    main()
