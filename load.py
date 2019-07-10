"""
从文件中加载 IP 列表
"""
import asyncio
import os
import sys

import aiohttp

from src.app.ip_get import IPGet
from src.app.main import Logger


async def main():
    argv = None
    if len(sys.argv) > 1:
        argv = sys.argv[1]
    if argv and argv.find('://') > 0:
        return await load_from_url(argv)
    res = os.listdir('.')
    ip_file_lists = [name for name in res if name.find('.ip.txt') > 0]
    if argv:
        if argv not in ip_file_lists:
            Logger.error('file %s doesn\'t exists' % argv)
            return
        else:
            ip_file_lists = [argv]
    for fn in ip_file_lists:
        await load_file(fn)


async def load_file(f_path):
    with open(f_path) as f:
        ips = []
        for ip in f.readlines():
            if ip and ip.find(':') and ip.find('#') < 0:
                ip = ip.strip()
                ips.append(ip)
        if ips:
            Logger.info('Find ip count %d' % len(ips))
            await IPGet.push_to_pool(ips)


async def load_from_url(url: str):
    import re
    headers = {
        'User-Agent': get_user_agent()
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            text = await resp.text()
            matched = re.findall(r'(?:\d{1,3}\.){3}\d{1,3}:\d+', text)
            ips = []
            for ip in matched:
                if ip and ip.find(':') and ip.find('#') < 0:
                    ip = ip.strip()
                    ips.append(ip)
            if ips:
                Logger.info('Find ip count %d' % len(ips))
                await IPGet.push_to_pool(ips)


def get_user_agent() -> str:
    import random
    return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%d.0.3770.80 Safari/537.36' % random.randint(
        70, 76)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [main()]
    loop.run_until_complete(asyncio.wait(tasks))
