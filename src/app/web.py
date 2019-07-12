from sanic import Sanic
from sanic.response import json
from multiprocessing import Process

from src.app.ip_factory import IPFactory
from src.app.main import Config

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


if __name__ == '__main__':
    Web().start()
