from app.ip_get import IPGet, SiteResponse
from lib.structs import SiteData, SiteResponseData

key = 'xicidaili'


@IPGet.config(key)
def config():
    site = SiteData()
    site.name = '西刺代理'
    site.enabled = True
    site.pages = ['http://www.xicidaili.com/{}/{}'.format(i, ii) for i in ['nn', 'nt', 'wn', 'wt'] for ii in
                  range(1, 5)]
    return site


@IPGet.parse(key)
def parse(resp: SiteResponse):
    items = resp.xpath('//tr')[1:]
    for item in items:
        try:
            res = SiteResponseData()
            res.ip = item.xpath('.//td[2]//text()')[0]
            res.port = item.xpath('.//td[3]//text()')[0]
            yield res
        except Exception:
            continue


if __name__ == '__main__':
    from lib.func import run_until_complete

    runner = IPGet.test_crawl(key)
    run_until_complete(runner)
