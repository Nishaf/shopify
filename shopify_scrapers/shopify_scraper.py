import re

from datetime import datetime
from urllib.parse import urlparse

from shopify_scrapers.shopify_categories import SCategories
from shopify_scrapers.shopify_products import SProducts
from shopify_scrapers.shopify_product import SProduct

#from providers.logging_provider import LoggingProvider
from providers.request_browser import Browser


class ShopifyScraper:

    _robots_url_tile = '/robots.txt'
    _is_shopify_regex = '(\\/)(\\d+)(\\/)(checkouts)'

    _categories_provider = None
    _products_provider = None
    _product_provider = None
    _browser = None
    _lp = None

    _in_progress = False
    _is_job_finished = True
    _is_success = True
    _url = None
    _last_update_date = None
    _total_products = 0

    def __init__(self, settings=None):
        self._browser = Browser()
        self._lp = LoggingProvider()
        self.set_settings(settings)

    def scrape(self, url, website_id):
        all_products_list = list()
        try:
            self.set_init_states()
            self._in_progress = True
            self._is_job_finished = False
            self._is_success = False
            self._url = url
            print('in here')
            domain_url = ShopifyScraper._get_url_domain(url)
            self._categories_provider = SCategories(browser=self._browser)
            print("getting all categories...")
            self._products_provider = SProducts(browser=self._browser)
            print("getting all_products...")
            self._product_provider = SProduct(browser=self._browser)
            all_products_list = self.scrape_categories(domain_url, website_id)
            self._in_progress = False
            self._is_job_finished = True
            self._is_success = True
        except Exception as ex:
            print(ex)
            self._lp.warning('Exception was thrown while scraping URL: "%s", Exception: \n"%s"' % (url, ex))
            self._is_job_finished = True
            self._in_progress = False
            self._is_success = False
        finally:
            self._last_update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._total_products = len(all_products_list)
            return all_products_list

    def set_init_states(self):
        self._in_progress = False
        self._is_job_finished = True
        self._is_success = True
        self._url = None
        self._last_update_date = None
        self._total_products = 0

    def scrape_categories(self, url, website_id):
        all_products_list = list()
        is_shopify = self.is_shopify_site(url)
        print("scraping cat")
        print(is_shopify)
        if not is_shopify:
            self._lp.critical('Site: "%s" is not shopify_scrapers based. Skipped.' % url)
            return all_products_list
        categories = self._categories_provider.get_categories(url=url)
        print("Categories: " + str(len(categories)))
        for category in categories:
            if not self._in_progress:
                return all_products_list
            self._lp.info('Scraper category: %s' % category['title'])
            products = self._products_provider.get_products(url, website_id, category)
            all_products_list.extend(products)
        return all_products_list

    def is_shopify_site(self, url):
        robots_url = url + self._robots_url_tile
        status_code, content = self._browser.get_html(robots_url, use_proxy=True)
        if len(re.findall(pattern=self._is_shopify_regex, string=str(content))):
            return True
        return False

    def stop(self):
        self._in_progress = False
        if self._categories_provider:
            self._categories_provider.stop()
        if self._products_provider:
            self._products_provider.stop()

    def get_status(self):
        status = {
            'is_job_finished': self._is_job_finished,
            'url': self._url,
            'success': self._is_success,
            'last_update_date': self._last_update_date,
            'total_products': self._total_products
        }
        return status

    def set_settings(self, settings):
        self._browser.set_settings(settings)

    @staticmethod
    def _get_url_domain(url):
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        return domain




