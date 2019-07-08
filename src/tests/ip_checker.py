import pytest

from src.app.main import Config
from src.app.ip_checker import IPChecker
from src.tests.data_provider import TEST_PROXY_IPS

Config.APP_ENV = Config.AppEnvType.TEST
pytestmark = pytest.mark.asyncio


async def test_push_to_pool():
    count = await IPChecker.push_to_pool(TEST_PROXY_IPS)
    assert count == len(TEST_PROXY_IPS)


async def test_ip_check():
    await IPChecker().run()
    assert True
