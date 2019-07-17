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
    IP_POOL = Gauge(name_prefix + 'ip_pool', 'Ip pools count', multiprocess_mode='livesum')
    IP_CHECK_POOL = Gauge(name_prefix + 'ip_check_pool', 'Ip check pools count', multiprocess_mode='livesum')

    @staticmethod
    def get_data()-> str:
        return generate_latest(registry).decode()

if __name__ == '__main__':
    import time

    while True:
        res = Prometheus.get_data()
        print(res)
        Prometheus.IP_POOL.inc(1)
        time.sleep(1)
