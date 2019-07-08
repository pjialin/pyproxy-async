import pytest

from app.main import Config
from app.ip_get import IPGet
from tests.data_provider import TEST_PROXY_IPS

Config.APP_ENV = Config.AppEnvType.TEST
pytestmark = pytest.mark.asyncio


async def test_push_to_pool():
    count = await IPGet.push_to_pool(TEST_PROXY_IPS)
    assert count == len(TEST_PROXY_IPS)
