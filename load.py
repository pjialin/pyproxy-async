"""
从文件中加载 IP 列表
"""
import asyncio
import os
import sys

from src.app.ip_get import IPGet
from src.app.main import Logger


async def main():
    res = os.listdir('.')
    ip_file_lists = [name for name in res if name.find('.ip.txt') > 0]
    if len(sys.argv) > 1:
        custom_file = sys.argv[1]
        if custom_file not in ip_file_lists:
            Logger.error('file %s doesn\'t exists' % custom_file)
            return
        else:
            ip_file_lists = [custom_file]
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


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [main()]
    loop.run_until_complete(asyncio.wait(tasks))
