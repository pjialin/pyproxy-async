import logging
import os


class Config:
    class AppEnvType:
        DEV = 'dev'
        PRODUCTION = 'production'
        TEST = 'test'

    APP_NAME = 'pyproxy'
    APP_ENV = AppEnvType.PRODUCTION
    LOADED = False

    PROJECT_DIR = os.path.abspath(__file__ + '/../../../') + '/'
    DUMPED_DIR = PROJECT_DIR + 'data/dumped/'
    CONFIG_FILE = PROJECT_DIR + 'config.toml'

    # Basic
    AUTO_DUMP = True

    # Coroutine count
    COROUTINE_COUNT_IP_CHECK = 20

    WEB = {
        'host': '0.0.0.0',
        'port': 8008
    }
    # Config
    REDIS = {
        'address': '127.0.0.1:6379',
        'db': 0,
        'password': None,
    }

    # Redis keys
    REDIS_KEY_IP_POOL = APP_NAME + ':ip_pool'  # sort set
    REDIS_KEY_IP_LEGACY_POOL = APP_NAME + ':ip_legacy_pool'  # sort set
    REDIS_KEY_TASK_POOL = APP_NAME + ':task_pool'  # sort set
    REDIS_KEY_CHECK_POOL = APP_NAME + ':ip_check_pool'  # list
    REDIS_KEY_CHECKED_POOL = APP_NAME + ':ip_checked_pool'
    REDIS_KEY_NET_DELAY = APP_NAME + ':ip_net_%d'  # set
    # REDIS_KEY_ABLE_POOL = APP_NAME + ':able_pool'
    REDIS_KEY_ABLE_HTTP = APP_NAME + ':able_http'  # set
    REDIS_KEY_ABLE_HTTPS = APP_NAME + ':able_https'  # set

    # default
    DEFAULT_SCORE = 30
    DEFAULT_INC_SCORE = 10
    DEFAULT_DEC_SCORE = 10
    DEFAULT_MAX_SCORE = 100
    DEFAULT_MINI_SCORE = 0

    DEFAULT_LEGACY_IP_RETAINED_TIME = 60 * 60 * 12  # 无效 ip 保留时间 | 秒

    DEFAULT_CHECK_INTERVAL = 60 * 10  # ip 检查间隔 | 秒
    DEFAULT_CHECK_CLEAN_IP_INTERVAL = 10  # ip 清理间隔 | 秒
    DEFAULT_CRAWL_SITES_INTERVAL = 60 * 60  # ip 抓取间隔 | 秒
    DEFAULT_LEGACY_IP_CHECK_INTERVAL = 10  # 无效 ip 检测时间 | 秒
    DEFAULT_DUMP_IP_INTERVAL = 60 * 60 * 12  # 保存 IP 间隔 | 秒

    DEFAULT_REQUEST_TIME_OUT = 5
    DEFAULT_REQUEST_CHECK_TIME_OUT = 3

    @classmethod
    def load(cls):
        """
        Load configs from toml file
        :return:
        """
        import toml
        configs = toml.load(cls.CONFIG_FILE)

        redis = configs.get('redis')
        if redis:
            cls.REDIS.update(redis)

        web = configs.get('web')
        if redis:
            cls.WEB.update(web)

        app = configs.get('app')
        if app:
            cls.APP_ENV = app.get('env', cls.APP_ENV)


if not Config.LOADED:
    Config.load()


# Logger
def set_up_logger():
    logger = logging.getLogger(Config.APP_NAME)

    logger.setLevel(logging.DEBUG if Config.APP_ENV == Config.AppEnvType.DEV else logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


Logger = set_up_logger()
