from src.app.ip_get import IPGet, SiteResponse
from src.lib.structs import SiteData, SiteResponseData, SiteRequestData

key = 'ihuan'


@IPGet.config(key)
def config():
    site = SiteData()
    site.name = '小幻HTTP代理'
    site.use_proxy = True
    site.pages = ['https://ip.ihuan.me/']
    site.base_url = 'https://ip.ihuan.me/'
    site.page_limit = 20
    site.current_page = 1
    return site


@IPGet.parse(key)
def parse(resp: SiteResponse):
    items = resp.xpath('//tr')[1:]
    for item in items:
        try:
            res = SiteResponseData()
            res.ip = item.xpath('.//td[1]//text()')[0]
            res.port = item.xpath('.//td[2]//text()')[0]
            yield res
        except Exception:
            continue
    try:
        if resp.site.current_page < resp.site.page_limit:
            n = resp.xpath('//ul[@class="pagination"]//li//a[@aria-label="Next"]//@href')[0]
            request = SiteRequestData()
            request.url = resp.site.base_url + n
            request.use_proxy = True
            resp.site.current_page += 1
            yield request
    except Exception:
        pass


if __name__ == '__main__':
    from src.lib.func import run_until_complete

    runner = IPGet.test_crawl(key)
    run_until_complete(runner)
