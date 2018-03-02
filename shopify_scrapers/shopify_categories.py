import re

from lxml import html
from config.config import defaults
from providers.logging_provider import LoggingProvider
from bs4 import BeautifulSoup


class SCategories:

    _categories_title_xpath = '//meta[@property="og:title"]'
    _category_sitemap_url_tail = '/sitemap_collections_1.xml'

    _in_progress = False

    def __init__(self, browser):
        self.lp = LoggingProvider()
        self.browser = browser

    def get_categories(self, url):
        categories = list()
        try:
            self._in_progress = True
            categories_urls = self._get_categories_sitemap(url)
            categories = self._get_categories_info(categories_urls)
        except Exception as ex:
            self.lp.critical('Can\'t get categories. Url: %s; Exception: \n%s' % (url, ex))
        finally:
            self._in_progress = False
            return categories

    def _get_categories_sitemap(self, url):
        categories_urls = list()
        try:
            sitemap_url = url + self._category_sitemap_url_tail
            status_code, content = self.browser.get_html(sitemap_url)
            soup = BeautifulSoup(content)
            sitemap_tags = soup.find_all('url')
            for sitemap_tag in sitemap_tags:
                categories_urls.append(sitemap_tag.findNext("loc").text)
        except Exception as ex:
            self.lp.critical('Can\'t get categories from sitemap. Sitemap url: "%s". Exception: \n"%s"'
                             % (sitemap_url, ex))
        finally:
            return categories_urls

    def _get_categories_info(self, categories_urls):
        categories_info = list()
        for category_url in categories_urls:
            try:
                if not self._in_progress:
                    return categories_info
                status_code, content = self.browser.get_html(category_url)
                content_tree = html.fromstring(content)
                category_title_elements = content_tree.xpath(self._categories_title_xpath)
                category_title = category_title_elements[0].attrib['content'] \
                    if len(category_title_elements) and \
                       'content' in category_title_elements[0].attrib \
                    else None
                if category_title is None:
                    category_title_elements = content_tree.xpath('//title')[0]
                    category_title = category_title_elements.text


                category_info = {
                    'title': category_title,
                    'link': category_url
                }
                print(category_info)
                categories_info.append(category_info)
            except Exception as ex:
                self.lp.critical('Can\'t get categories info.'
                                 ' links: \n%s; Exception: \n%s'
                                 % (categories_urls, ex))
                continue

        return categories_info

    def stop(self):
        self._in_progress = False

