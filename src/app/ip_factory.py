import random

from src.app.main import Config, Logger
from src.lib.redis_lib import Redis
from src.lib.structs import IPData


class IPFactory:
    @classmethod
    async def get_random_ip(cls, https: bool = False) -> IPData:
        ips = await cls.get_ips(https=https)
        ip = random.choice(ips)
        if not ip:
            return None
        assert isinstance(ip, IPData), 'Error format'
        Logger.info('[factory] get ip %s', ip.to_str())
        return ip

    @classmethod
    async def get_ips(cls, http: bool = True, https: bool = False, delay: int = None):
        keys = []
        if http:
            keys.append(Config.REDIS_KEY_ABLE_HTTP)
        if https:
            keys.append(Config.REDIS_KEY_ABLE_HTTPS)
        if delay:
            keys.append(Config.REDIS_KEY_NET_DELAY % delay)
        with await Redis.share() as redis:
            ips = await redis.sinter(*keys)
            ips = [IPData.with_str(ip.decode()) for ip in ips]
        return ips


if __name__ == '__main__':
    from src.lib.func import run_until_complete

    run_until_complete(IPFactory.get_random_ip())
