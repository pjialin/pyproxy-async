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
    ip = await IPFactory.get_random_ip(bool(request.raw_args.get('https', False)))
    return json({
        'ip': ip.ip,
        'port': ip.port,
        # 'https': ip.https,
        'http': ip.to_http(),
    })
