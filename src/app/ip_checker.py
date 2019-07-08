import asyncio
import datetime

import aiohttp

from src.app.main import Config, Logger
from src.app.ip_saver import IPSaver
from src.lib.exceptions import ValidationFailException
from src.lib.redis_lib import Redis
from src.lib.structs import IPData


class IPChecker:
    NORMAL_CHECK_URL = 'http://httpbin.org/get'

    async def run(self):
        runner = self.check_task
        # tasks = [runner()]
        # tasks = []
        tasks = [runner() for _ in range(Config.COROUTINE_COUNT_IP_CHECK)]
        tasks.append(self.check_low_score_task())
        tasks.append(self.recheck_ip_task())
        await asyncio.ensure_future(asyncio.wait(tasks))

    async def check_task(self):
        while True:
            Logger.debug('[check] check task loop')
            await self.start_check()
            if Config.APP_ENV == Config.AppEnvType.TEST:
                break

    async def check_low_score_task(self):
        while True:
            Logger.debug('[check] check low score task loop')
            await self.remove_low_score_ip()
            if Config.APP_ENV == Config.AppEnvType.TEST:
                break
            await asyncio.sleep(Config.DEFAULT_CHECK_CLEAN_IP_INTERVAL)

    async def recheck_ip_task(self):
        while True:
            Logger.debug('[check] recheck ip task loop')
            await self.resend_check_ip()
            if Config.APP_ENV == Config.AppEnvType.TEST:
                break
            await asyncio.sleep(Config.DEFAULT_CHECK_INTERVAL)

    async def start_check(self):
        with await Redis.share() as redis:
            ip_str = await redis.blpop(Config.REDIS_KEY_CHECK_POOL)
        ip_str = ip_str[1].decode()
        Logger.info('[check] got ip %s' % ip_str)
        ip = IPData.with_str(ip_str)
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(Config.DEFAULT_REQUEST_CHECK_TIME_OUT)) as session:
            ip = await self.http_check(ip, session)
            ip = await self.https_check(ip, session)
            Logger.info('[check] Check result %s http %s https %s', ip.to_str(), ip.http, ip.https)
        await IPSaver().save_ip(ip)
        # await self.push_to_checked_pool(ip.to_str())

    async def http_check(self, ip: IPData, session) -> IPData:
        """
        可用与匿名检测 毫秒
        :param ip:
        :return:
        """
        time_spend = datetime.datetime.now()
        try:
            async with session.get(self.NORMAL_CHECK_URL, proxy=ip.to_http()) as resp:
                result = await resp.json()
                if not result.get('origin'):
                    raise ValidationFailException()
                time_spend = datetime.datetime.now() - time_spend
                ip.delay = time_spend.total_seconds()
                ip.http = True
        except Exception as e:
            ip.http = False

        return ip

    async def https_check(self, ip: IPData, session) -> IPData:
        """
        HTTPS 可用性检测
        :return:
        """
        try:
            async with session.get(self.NORMAL_CHECK_URL.replace('http', 'https', 1), proxy=ip.to_http()) as resp:
                result = await resp.json()
                if not result.get('origin'):
                    raise ValidationFailException()
                ip.https = True
        except Exception as e:
            ip.https = False

        return ip

    async def remove_low_score_ip(self):
        saver = IPSaver()
        needs_remove = []
        with await Redis.share() as redis:
            ips = await redis.zrangebyscore(Config.REDIS_KEY_IP_POOL, -100, 0)
            if len(ips) > 0:
                ips = [ip_str.decode() for ip_str in ips]
                needs_remove = ips
        if needs_remove:
            await saver.remove_ip(ips)
            Logger.info('[check] remove ip %s', ','.join(ips))

    async def resend_check_ip(self):
        """
        从 ip_pool 中将需要检测的 ip 推到 ip_check_pool 中
        :return:
        """
        with await Redis.share() as redis:
            check_pool_len = await redis.llen(Config.REDIS_KEY_CHECK_POOL)
            ip_pool_len = await redis.zcount(Config.REDIS_KEY_IP_POOL)
            if check_pool_len >= ip_pool_len:  # 如果待检测的数量大于 ip 池中的数量，就不推了
                return
            for i in range(Config.DEFAULT_MINI_SCORE + 1, Config.DEFAULT_MAX_SCORE + Config.DEFAULT_INC_SCORE,
                           Config.DEFAULT_INC_SCORE):
                end_score = i + Config.DEFAULT_INC_SCORE - 1
                ips = await redis.zrangebyscore(Config.REDIS_KEY_IP_POOL, i, end_score)
                ips = [ip.decode() for ip in ips]
                needs_check = []
                for ip in ips:
                    # is_checked = await redis.sismember(Config.REDIS_KEY_CHECKED_POOL, ip)
                    # if is_checked:
                    #     continue
                    needs_check.append(ip)
                if needs_check:
                    await self.push_to_pool(needs_check)
            # remove checked pool
            # await redis.delete(Config.REDIS_KEY_CHECKED_POOL)

    @classmethod
    async def push_to_pool(cls, ips) -> int:
        if not isinstance(ips, list):
            ips = [ips]
        with await Redis.share() as redis:
            await redis.rpush(Config.REDIS_KEY_CHECK_POOL, *ips)
            Logger.info('[check] send %d ip to check pools' % len(ips))
        return len(ips)

    @classmethod
    async def push_to_checked_pool(cls, ips) -> int:
        if not isinstance(ips, list):
            ips = [ips]
        with await Redis.share() as redis:
            await redis.sadd(Config.REDIS_KEY_CHECKED_POOL, *ips)
            Logger.info('[check] send %d ip to checked pools' % len(ips))
        return len(ips)


if __name__ == '__main__':
    from src.lib.func import run_until_complete

    run_until_complete(IPChecker().run())
