import asyncio
from src.app.ip_checker import IPChecker
from src.sites import *
from src.app.ip_get import IPGet


def main():
    loop = asyncio.get_event_loop()
    tasks = []
    tasks.append(IPGet.share().run())
    tasks.append(IPChecker().run())
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    main()
