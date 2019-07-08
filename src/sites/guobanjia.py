from src.app.ip_get import IPGet, SiteResponse
from src.lib.structs import SiteData, SiteResponseData

key = 'goubanjia'


@IPGet.config(key)
def config():
    site = SiteData()
    site.name = '全网代理IP'
    site.pages = ['http://www.goubanjia.com/']
    return site


@IPGet.parse(key)
def parse(resp: SiteResponse):
    items = resp.xpath('//tr')[1:]
    for item in items:
        try:
            data = item.xpath('.//td[1]//*[name(.)!="p"]/text()')
            res = SiteResponseData()
            res.ip = "".join(data[:-1])
            res.port = data[-1]
            yield res
        except Exception:
            continue

if __name__ == '__main__':
    from src.lib.func import run_until_complete

    runner = IPGet.test_crawl(key)
    run_until_complete(runner)
