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
    PROMETHEUS_DIR = PROJECT_DIR + 'data/prometheus/'
    CONFIG_FILE = PROJECT_DIR + 'config.toml'

    # Basic
    AUTO_DUMP = True
    PROMETHEUS_ABLE = False

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
    RULES = []

    # Redis keys
    REDIS_KEY_IP_POOL = APP_NAME + ':ip_pool'  # sort set
    REDIS_KEY_IP_LEGACY_POOL = APP_NAME + ':ip_legacy_pool'  # sort set
    REDIS_KEY_TASK_POOL = APP_NAME + ':task_pool'  # sort set
    REDIS_KEY_CHECK_POOL = APP_NAME + ':ip_check_pool'  # list
    REDIS_KEY_CHECKED_POOL = APP_NAME + ':ip_checked_pool'
    REDIS_KEY_NET_DELAY = APP_NAME + ':ip_net_%d'  # set   100 500 1000 2000
    # REDIS_KEY_ABLE_POOL = APP_NAME + ':able_pool'
    REDIS_KEY_ABLE_HTTP = APP_NAME + ':able_http'  # set
    REDIS_KEY_ABLE_HTTPS = APP_NAME + ':able_https'  # set
    REDIS_KEY_ABLE_RULES = APP_NAME + ':able_rules_%s'  # rules

    # default
    DEFAULT_SCORE = 30
    DEFAULT_INC_SCORE = 10
    DEFAULT_DEC_SCORE = 10
    DEFAULT_MAX_SCORE = 100
    DEFAULT_MINI_SCORE = 0

    DEFAULT_LEGACY_IP_RETAINED_TIME = 60 * 60 * 12  # 无效 ip 保留时间 | 秒

    DEFAULT_LOOP_INTERVAL = 5  # 任务 Loop 间隔 | 秒
    DEFAULT_CHECK_INTERVAL = 60 * 10  # ip 检查间隔 | 秒
    DEFAULT_CHECK_CLEAN_IP_INTERVAL = 10  # ip 清理间隔 | 秒
    DEFAULT_CRAWL_SITES_INTERVAL = 60 * 60  # ip 抓取间隔 | 秒
    DEFAULT_LEGACY_IP_CHECK_INTERVAL = 10  # 无效 ip 检测时间 | 秒
    DEFAULT_DUMP_IP_INTERVAL = 60 * 60 * 12  # 保存 IP 间隔 | 秒
    DEFAULT_STATS_CHECK_INTERVAL = 10  # IP 数据统计间隔

    DEFAULT_REQUEST_TIME_OUT = 5
    DEFAULT_REQUEST_CHECK_TIME_OUT = 3

    # Rate
    RE_PUSH_TO_CHECK_POOL_RATE = 0.6  # 如果 总 IP 数量 > IP 池数量 * Rate  则跳过本次推送任务

    @classmethod
    def load(cls):
        """
        Load configs from toml file
        :return:
        """
        import toml
        configs = toml.load(cls.CONFIG_FILE)

        redis = configs.get('redis', {})
        cls.REDIS.update(redis)

        web = configs.get('web', {})
        cls.WEB.update(web)

        app = configs.get('app', {})
        cls.load_app(app)

        rules = configs.get('rule', {})
        cls.load_rules(rules)

        if cls.PROMETHEUS_ABLE:
            cls.clean_prometheus_dir()

    @classmethod
    def load_app(cls, app):
        cls.APP_ENV = app.get('env', cls.APP_ENV)
        for key, val in app.items():
            if key in ['env']:
                continue
            upper_key = key.upper()
            if getattr(cls, upper_key, None) is not None:
                setattr(cls, upper_key, val)

    @classmethod
    def load_rules(cls, rules):
        from src.lib.structs import RuleData
        for _, rule in rules.items():
            r_data = RuleData(**rule)
            if r_data.verify():
                cls.RULES.append(r_data)

    @classmethod
    def clean_prometheus_dir(cls):
        path = cls.PROMETHEUS_DIR
        if not os.path.isdir(path):
            os.mkdir(path)
            return
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                pass


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
