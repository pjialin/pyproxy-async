import aioredis
from aioredis.commands import ContextRedis

from src.app.main import Config
from src.lib.helper import ShareInstance
from src.lib.func import time_int


class Redis(ShareInstance):
    _pool = None

    async def init_pool(self, *args, **kwargs):
        size = 5
        if not self._pool:
            if not kwargs:
                kwargs = Config.REDIS
                size = Config.COROUTINE_COUNT_IP_CHECK

            self._pool = await aioredis.create_redis_pool(minsize=size + size // 2, maxsize=size * 2, *args, **kwargs)

    @classmethod
    async def share(cls, **kwargs) -> "ContextRedis":
        self = super().share()
        await self.init_pool()
        return await self._pool

    @classmethod
    async def last_time_check(cls, key: str, interval: float) -> bool:
        with await cls.share() as redis:
            score = await redis.zscore(Config.REDIS_KEY_TASK_POOL, key)
            if score and score > (time_int() - interval):
                return True
        return False

    @classmethod
    async def save_last_time(cls, key: str) -> bool:
        from src.lib.func import time_int
        with await cls.share() as redis:
            await redis.zadd(Config.REDIS_KEY_TASK_POOL, time_int(), key)
        return True


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()


    async def run():
        with await Redis.share() as redis:
            result = await redis.keys('*')
        print(result)


    res = loop.run_until_complete(run())
