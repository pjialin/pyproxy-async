import os
from src.app.main import Config

# Set env before import client
os.environ['prometheus_multiproc_dir'] = Config.PROMETHEUS_DIR

from prometheus_client import Summary, Counter, Gauge, CollectorRegistry, multiprocess, generate_latest

name_prefix = Config.APP_NAME + '_'

# register Collector
registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)


class Prometheus:
    # Create metrics.
    IP_CHECK_TOTAL = Counter(name_prefix + 'ip_check_total', 'Total checked counts')
    IP_STATUS = Gauge(name_prefix + 'ip_status', 'Current status', multiprocess_mode='max', labelnames=['key', 'group'])
    WEB_API_COUNTER = Counter(name_prefix + 'web_api', 'Web api counter', labelnames=['uri', 'method', 'code'])
    WEB_REQUESTS_DURATION = Gauge(name_prefix + 'web_requests_duration_seconds', 'Web requests duration',
                                  multiprocess_mode='max', labelnames=['uri', 'method', 'code'])

    @staticmethod
    def get_data() -> str:
        return generate_latest(registry).decode()

    @classmethod
    def up_status(cls, key: str, val: int, group=''):
        label = ''
        if key.find(':'):
            label = key[key.rfind(':') + 1:]
        cls.IP_STATUS.labels(key=label, group=group).set(val)

    @classmethod
    def up_web_api_counter(cls, uri: str, method: str = 'GET', code=200, delay=0, inc=1):
        cls.WEB_API_COUNTER.labels(uri=uri, method=method, code=code).inc(inc)
        cls.WEB_REQUESTS_DURATION.labels(uri=uri, method=method, code=code).set(delay)


if __name__ == '__main__':
    import time

    while True:
        res = Prometheus.get_data()
        print(res)
        Prometheus.IP_POOL.inc(1)
        time.sleep(1)
