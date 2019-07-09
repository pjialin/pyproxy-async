import pytest

from src.app.ip_saver import IPSaver
from src.app.main import Config
from src.app.ip_get import IPGet
from src.lib.func import time_int
from src.lib.redis_lib import Redis
from src.tests.data_provider import TEST_PROXY_IPS

Config.APP_ENV = Config.AppEnvType.TEST
pytestmark = pytest.mark.asyncio


async def test_push_to_pool():
    count = await IPGet.push_to_pool(TEST_PROXY_IPS)
    assert count == len(TEST_PROXY_IPS)


async def test_remove_legacy_ip():
    with await Redis.share() as redis:
        await redis.zadd(Config.REDIS_KEY_IP_LEGACY_POOL,
                         *(time_int() - Config.DEFAULT_LEGACY_IP_RETAINED_TIME, '127.0.0.1:8080'))
    count = await IPGet().remove_legacy_ip()
    assert count > 0


async def test_dump_to_file():
    res = await IPSaver().dump_to_file()
    assert res == True
