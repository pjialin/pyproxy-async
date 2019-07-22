from src.app.main import Config, Logger
from src.lib.func import time_int
from src.lib.structs import IPData
from src.lib.redis_lib import Redis


class IPSaver:
    async def save_ip(self, ip: IPData):
        await self.update_score(ip)
        with await Redis.share() as redis:
            if ip.http is True:
                await redis.sadd(Config.REDIS_KEY_ABLE_HTTP, ip.to_str())
            else:
                await redis.srem(Config.REDIS_KEY_ABLE_HTTP, ip.to_str())

            if ip.https is True:
                await redis.sadd(Config.REDIS_KEY_ABLE_HTTPS, ip.to_str())
            else:
                await redis.srem(Config.REDIS_KEY_ABLE_HTTPS, ip.to_str())

            # Rules check
            for key, res in ip.rules.items():
                if res is True:
                    await redis.sadd(Config.REDIS_KEY_ABLE_RULES % key, ip.to_str())
                else:
                    await redis.srem(Config.REDIS_KEY_ABLE_RULES % key, ip.to_str())

            # Delay pool
            if ip.available():
                delay_key = self.get_delay_key(ip.delay)
                if delay_key:
                    await redis.sadd(delay_key, ip.to_str())

        if ip.available():
            await self.available_call(ip)
        else:
            await self.fail_call(ip)

    async def fail_call(self, ip: IPData):
        if ip.score <= Config.DEFAULT_MINI_SCORE:
            return
        with await Redis.share() as redis:
            await redis.zincrby(Config.REDIS_KEY_IP_POOL, -Config.DEFAULT_DEC_SCORE, ip.to_str())

    async def available_call(self, ip: IPData):
        if ip.score >= Config.DEFAULT_MAX_SCORE:
            return
        with await Redis.share() as redis:
            await redis.zincrby(Config.REDIS_KEY_IP_POOL, Config.DEFAULT_INC_SCORE, ip.to_str())

    async def remove_ip(self, ip_str):
        if not isinstance(ip_str, list):
            ip_str = [ip_str]
        with await Redis.share() as redis:
            await redis.srem(Config.REDIS_KEY_ABLE_HTTP, *ip_str)
            await redis.srem(Config.REDIS_KEY_ABLE_HTTPS, *ip_str)
            for i in [100, 500, 1000, 2000]:
                await redis.srem(Config.REDIS_KEY_NET_DELAY % i, *ip_str)
            for rule in Config.RULES:  # 从规则中删除
                await redis.srem(Config.REDIS_KEY_ABLE_RULES % rule.key, *ip_str)
            await redis.zrem(Config.REDIS_KEY_IP_POOL, *ip_str)
            # save to legacy pool
            members = []
            time = time_int()
            for ip in ip_str:
                members.append(time)
                members.append(ip)
            await redis.zadd(Config.REDIS_KEY_IP_LEGACY_POOL, *members)

    async def dump_to_file(self):
        from os import path, mkdir
        if not path.isdir(Config.DUMPED_DIR):
            mkdir(Config.DUMPED_DIR)
        with await Redis.share() as redis:
            members = await redis.zrangebyscore(Config.REDIS_KEY_IP_POOL, Config.DEFAULT_MINI_SCORE,
                                                Config.DEFAULT_MAX_SCORE + Config.DEFAULT_INC_SCORE)
            if members:
                members = [m.decode() for m in members]
                from datetime import datetime
                file_name = 'ip_pool_%s.ip.txt' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(Config.DUMPED_DIR + file_name, 'w') as f:
                    f.write('\n'.join(members))
                Logger.info('Dump %d ip to file %s' % (len(members, file_name)))
        return True

    def get_delay_key(self, delay: float) -> str:
        delay_key = None
        if delay <= 0.1:
            delay_key = Config.REDIS_KEY_NET_DELAY % 100
        elif delay <= 0.5:
            delay_key = Config.REDIS_KEY_NET_DELAY % 500
        elif delay <= 1:
            delay_key = Config.REDIS_KEY_NET_DELAY % 1000
        elif delay <= 2:
            delay_key = Config.REDIS_KEY_NET_DELAY % 2000
        return delay_key

    async def update_score(self, ip: IPData):
        with await Redis.share() as redis:
            score = await redis.zscore(Config.REDIS_KEY_IP_POOL, ip.to_str())
            ip.score = score if score is not None else 0
