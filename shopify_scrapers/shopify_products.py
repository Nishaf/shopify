from lxml import html
from shopify_scrapers.shopify_product import SProduct
from providers.logging_provider import LoggingProvider
from shopsify_admin.models import ShopifyProductModel, ShopifySiteModel
from datetime import datetime

class SProducts:

    _page_url_tail = '?page=%s'
    _product_links_xpath = '//a[re:test(@href, "(\\/)(collections)(\\/)((?:[a-z][a-z0-9_-]*))' \
                           '(\\/)(products)(\\/)((?:[a-z][a-z0-9_-]*))$")]'
    _second_product_links_xpath = '//a[re:test(@href, "(\\/)(products)(\\/)((?:[a-z][a-z0-9_-]*))$")]'
    _next_page_xpath = '//a[contains(@href, "?page=")]'
    _base_url = None

    _in_progress = False

    def __init__(self, browser):
        self.browser = browser
        self.product_provider = SProduct(browser=browser)
        self.lp = LoggingProvider()

    def get_list_string(self, list):
        result = ''
        for item in list:
            try:
                result += '%s;' % item.replace('\n', '')
            except Exception as ex:
                continue
        return result

    def update_website_info(self, website_id, status):
        try:
            website = ShopifySiteModel.objects.get(id=website_id)
            website.total_products += 1
            website.last_update_date = datetime.now()
            website.last_status = status
            website.save()
        except Exception as ex:
            print(ex)
            pass

    def create_entry(self, website_id, product_info):
        site = ShopifySiteModel.objects.filter(id=website_id)[0]
        products = ShopifyProductModel.objects.filter(website=site, title=str(product_info['Title']).strip(),
                                              url=str(product_info['Url']).strip())
        if len(products) == 0:
            entry = ShopifyProductModel(
                website=site,
                title=str(product_info['Title']).strip() if product_info['Title'] else '',
                html=str(product_info['html']).strip() if product_info['html'] else '',
                category=str(product_info['Category']).strip() if product_info['Category'] else '',
                url=str(product_info['Url']).strip() if product_info['Url'] else '',
                description=str(product_info['Description']).strip() if product_info['Description'] else '',
                price=str(product_info['Price']).strip() if product_info['Price'] else '',
                sale_price=str(product_info['Sale price']).strip() if product_info['Sale price'] else '',
                currency=str(product_info['Currency']).strip() if product_info['Currency'] else '',
                images=self.get_list_string(product_info['Images']),
                options=self.get_list_string(product_info['Options']))
            entry.save()
            self.update_website_info(website_id, 'Success')

    def get_products(self, base_url, website_id, category):
        self._in_progress = True
        category_url = category['link']
        category_title = category['title']
        page_number = 1
        products_info_list = list({})
        has_next_page = True
        self._base_url = base_url
        while has_next_page:
            if not self._in_progress:
                return products_info_list
            print("Scraping....")
            full_category_url = category_url + self._page_url_tail % page_number
            print(full_category_url)
            status_code, content = self.browser.get_html(full_category_url)
            content_tree = html.fromstring(content)
            has_next_page = self._has_next_page(content_tree)
            product_urls = self._get_product_urls(content_tree)
            for product_url in product_urls:
                if not self._in_progress:
                    return products_info_list
                product_info = self.product_provider.get_product_info(product_url, category_title)
                if product_info:
                    self.create_entry(website_id, product_info)
                    products_info_list.append(product_info)
            page_number += 1
        self._in_progress = False
        return products_info_list

    def _has_next_page(self, content_tree):
        result = False
        try:
            next_page = content_tree.xpath(self._next_page_xpath)
            if next_page and len(next_page):
                if not next_page[-1].text or not next_page[-1].text.isdigit():
                    result = True
                else:
                    result = False
            else:
                result = False
        except Exception as ex:
            self.lp.warning('Can\'t get next page. Exception: "%s"' % ex)
        finally:
            return result

    def _get_product_urls(self, content_tree):
        product_urls = list()
        try:
            product_links = content_tree.xpath(self._product_links_xpath,
                                               namespaces={'re': "http://exslt.org/regular-expressions"})
            if not len(product_links):
                product_links = content_tree.xpath(self._second_product_links_xpath,
                                                   namespaces={'re': "http://exslt.org/regular-expressions"})
            if not product_links or not len(product_links):
                self.lp.info('Product links not found. ')
                return product_urls
            for product_link in product_links:
                if not self._in_progress:
                    return product_urls
                if 'href' in product_link.attrib:
                    product_url = self._base_url + product_link.attrib['href']
                    if product_url not in product_urls:
                        product_urls.append(product_url)
                else:
                    self.lp.warning('Product link: %s hasn\'t href attribute' % product_link)
        except Exception as ex:
            self.lp.critical('Exception occurred while getting product urls. Exception: \n%s' % ex)
        finally:
            return product_urls

    def stop(self):
        self._in_progress = False





