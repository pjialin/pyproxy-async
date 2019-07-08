from src.app.ip_get import IPGet, SiteResponse
from src.lib.structs import SiteData, SiteResponseData

key = 'kuaidaili'


@IPGet.config(key)
def config():
    site = SiteData()
    site.name = '云代理 ip3366'
    site.enabled = True
    site.pages = ['http://www.ip3366.net/free/?stype=%s&page=%s' % (i, ii) for i in range(1, 3) for ii in range(1, 5)]
    return site


@IPGet.parse(key)
def parse(resp: SiteResponse):
    items = resp.xpath('//tr')[1:]
    for item in items:
        try:
            data = item.xpath('.//td//text()')
            res = SiteResponseData()
            res.ip = data[0]
            res.port = data[1]
            yield res
        except Exception:
            continue


if __name__ == '__main__':
    from src.lib.func import run_until_complete

    runner = IPGet.test_crawl(key)
    run_until_complete(runner)
