from datetime import datetime

from sanic import Sanic
from sanic.response import json, text
from multiprocessing import Process

from src.app.ip_factory import IPFactory
from src.app.main import Config
from src.app.prometheus import Prometheus

app = Sanic()


class Web(Process):

    def run(self):
        app.run(**Config.WEB)


@app.route('/get_ip')
async def get_ip(request):
    is_https = bool(request.raw_args.get('https', False))
    rule = request.raw_args.get('rule')
    ip = await IPFactory.get_random_ip(https=is_https, rule=rule)
    if ip:
        return json({'ip': ip.ip, 'port': ip.port,
                     # 'https': ip.https,
                     'http': ip.to_http(),
                     })
    else:
        return json({'msg': 'The ip pool is empty. '})


@app.route('/metrics')
async def metrics(request):
    from src.app.prometheus import Prometheus
    data = Prometheus.get_data()
    return text(data)


@app.middleware('request')
async def print_on_request(request):
    request['start_time'] = datetime.now()


@app.middleware('response')
async def print_on_response(request, response):
    spend_time = datetime.now() - request['start_time']
    Prometheus.up_web_api_counter(request.path, request.method, code=response.status,
                                  delay=spend_time.total_seconds())


if __name__ == '__main__':
    web = Web()
    web.start()
    web.join()
