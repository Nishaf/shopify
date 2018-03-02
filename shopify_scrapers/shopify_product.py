import json
from bs4 import BeautifulSoup

#from providers.logging_provider import LoggingProvider
from providers.request_browser import Browser
from lxml import html


class SProduct:

    _in_stock_schema = 'http://schema.org/InStock'

    _product_title_xpath = '//meta[@property="og:title"]'
    _product_url_xpath = '//meta[@property="og:url"]'
    _product_description_xpath = '//meta[@property="og:description"]'
    _product_images_xpath = '//meta[@property="og:image"]'
    _product_images_xpath1 = '//meta[@property="og:image:secure_url"]'
    _additional_images_xpath = '//div[@class=carousel]'
    _product_price_xpath = '//meta[@property="og:price:amount"]'
    _product_currency_xpath = '//meta[@property="og:price:currency"]'

    _product_info_title_xpath = '//h1[@itemprop="name"]'
    _product_info_old_price_xpath = '//span[@id="ComparePrice"]'
    _product_info_price_xpath = '//span[@itemprop="price"]'
    _product_info_description_xpath = '//div[@itemprop="description"]'
    _product_info_options_xpath = "//option"

    _product_additional_meta_xpath = '//script[contains(text(),"var meta = ")]'

    _product_additional_images_xpath = ''

    def __init__(self, browser=None):
        self.browser = browser if browser else Browser()
        #self.lp = LoggingProvider()

    def get_product_info(self, product_url, category_title=None):
        status_code, content = self.browser.get_html(product_url, use_proxy=True)
        if status_code != 200:
            return None
        print("Getting Details")
        print(product_url)
        content_tree = html.fromstring(content)
        product_meta_info = self._get_product_meta_info(content_tree, category_title, product_url)
        product_additional_meta_info = self._get_product_additional_meta_info(content_tree)
        product_info = self._get_product_info(content_tree)

        if product_info['Title'] or not product_meta_info['Title']:
            product_meta_info['Title'] = product_info['Title']

        if product_info['Description']:
            product_meta_info['Description'] = product_info['Description']

        if not product_meta_info['Price']:
            product_meta_info['Price'] = product_info['Price']

        if product_info['Old price']:
            product_meta_info['Sale price'] = product_meta_info['Price']
            product_meta_info['Price'] = product_info['Old price']
        else:
            product_meta_info['Sale price'] = product_meta_info['Price']

        product_meta_info['Description'] = product_meta_info['Description'] if product_meta_info['Description'] else \
            self.get_additional_description(content)

        product_meta_info['Title'] = product_meta_info['Title'] if product_meta_info['Title'] is not None \
            else product_additional_meta_info['Title']
        product_meta_info['Price'] = product_meta_info['Price'] if product_meta_info['Price'] is not None \
            else product_additional_meta_info['Price']
        product_meta_info['Sale price'] = product_meta_info['Sale price'] if product_meta_info['Sale price'] is not None \
            else product_additional_meta_info['Price']
        product_meta_info['Options'] = product_info['Options'] if product_info['Options'] is not None \
                else product_additional_meta_info['Options']
        product_meta_info['Currency'] = product_meta_info['Currency'] if product_meta_info['Currency'] is not None \
                else product_additional_meta_info['Currency']
        product_meta_info['html'] = content
        #product_info['Url'] = (product_meta_info['Url'].split("product('")[1]) if 'product' in \
         #                                                                                  product_meta_info['Url'] else \
        #product_meta_info['Url']
        if len(product_meta_info['Images']) == 0:
            product_meta_info['Images'] = self.get_additional_images(content)

        return product_meta_info

    def _get_product_info(self, content_tree):
        product_title_elements = content_tree.xpath(self._product_info_title_xpath)
        product_price_elements = content_tree.xpath(self._product_info_price_xpath)
        product_description_elements = content_tree.xpath(self._product_info_description_xpath)
        product_options_elements = content_tree.xpath(self._product_info_options_xpath)
        product_old_price_elements = content_tree.xpath(self._product_info_old_price_xpath)

        product_title = product_title_elements[0].text if len(product_title_elements) else None
        product_price = product_price_elements[0].attrib['content']\
            if len(product_price_elements) and \
               'content' in product_price_elements[0].attrib\
            else None

        product_description = product_description_elements[0].text_content() if len(product_description_elements) else None

        product_options = self._get_product_options(product_options_elements)

        product_old_price = product_old_price_elements[0].text_content() \
            if len(product_old_price_elements) else None

        product_info = {
            'Title': product_title,
            'Description': product_description,
            'Price': product_price,
            'Old price': self.get_digits_from_line(product_old_price),
            'Options': product_options,
        }

        return product_info

    def get_digits_from_line(self, value_string):
        if not value_string:
            return None
        result = value_string.replace('\n', '').replace(' ', '').replace('$', '')
        return result

    def _get_product_meta_info(self, content_tree, category_title, product_url):
        product_title_elements = content_tree.xpath(self._product_title_xpath)
        product_description_elements = content_tree.xpath(self._product_description_xpath)
        product_price_elements = content_tree.xpath(self._product_price_xpath)
        product_currency_elements = content_tree.xpath(self._product_currency_xpath)
        product_image_elements = content_tree.xpath(self._product_images_xpath)
        product_image_elements1 = content_tree.xpath(self._product_images_xpath1)

        product_title = product_title_elements[0].attrib['content']\
            if len(product_title_elements) and \
               'content' in product_title_elements[0].attrib\
            else None

        product_description = product_description_elements[0].attrib['content'] \
            if len(product_description_elements) and \
               'content' in product_description_elements[0].attrib \
            else None

        product_price = product_price_elements[0].attrib['content'] \
            if len(product_price_elements) and \
               'content' in product_price_elements[0].attrib \
            else None

        product_currency = product_currency_elements[0].attrib['content'] \
            if len(product_currency_elements) and\
               'content' in product_currency_elements[0].attrib \
            else None

        product_images = self._get_product_images(product_image_elements + product_image_elements1)

        product_meta_info = {
            'Title': product_title,
            'Category': category_title,
            'Url': product_url,
            'Description': product_description,
            'Price': product_price,
            'Currency': product_currency,
            'Images': product_images
        }

        return product_meta_info

    def _get_product_additional_meta_info(self, content_tree):
       try:
            additional_meta_elements = content_tree.xpath(self._product_additional_meta_xpath)
            meta_script = additional_meta_elements[0].text if len(additional_meta_elements) else None
            if not meta_script:
                return None
            script_lines = meta_script.split(';')
            data_variable = None
            currency = None
            for script_line in script_lines:
                if 'var meta =' in script_line:
                    data_variable = script_line
                if '.meta.currency' in script_line:
                    currency = script_line
            if not data_variable:
                return None
            data_position = data_variable.find('{"product')
            if data_position < 0:
                return None
            json_data = data_variable[data_position:]
            additional_meta_dict = json.loads(json_data)
            position = currency.find('currency = ')
            currency = currency[position:]
            currency = currency.replace('currency = ', '')
            product_info = {
                'Title': additional_meta_dict['product']['variants'][0]['name'],
                'Price': additional_meta_dict['product']['variants'][0]['price'],
                'Options': [i['public_title'] for i in additional_meta_dict['product']['variants']],
                'Currency': (str(currency).replace(';','')).replace("'", "")
            }
            return product_info
       except:
            return {
                'Title': '',
                'Price': '',
                'Options': '',
                'Currency': ''
            }

    def get_additional_images(self, content):
        images = self._get_additional_product_images(content)
        if len(images) == 0:
            images = self._get_additional_product_images2(content)
        return images

    def _get_product_images(self, product_image_elements):
        try:
            image_urls = list()
            for product_image_element in product_image_elements:
                image_url = product_image_element.attrib['content'] \
                    if 'content' in product_image_element.attrib \
                    else None
                image_urls.append(image_url)
        except Exception as ex:
            self.lp.warning('Can\'t get product images. Exception: \n%s' % ex)
        finally:
            return image_urls

    def _get_additional_product_images(self, content):
        try:
            image_urls = list()
            soup = BeautifulSoup(content)
            images_list = soup.find('div', attrs={'class': 'carousel'})
            for image in images_list.find_all('img'):
                image_urls.append(image.get('src'))
        except Exception as ex:
            self.lp.warning('Can\'t get product images. Exception: \n%s' % ex)
        finally:
            return image_urls

    def _get_additional_product_images2(self, content):
        try:
            image_urls = list()
            soup = BeautifulSoup(content)
            for image in soup.find_all('div', attrs={'class': 'gallery-cell'}):
                image_urls.append((image.find('img')).get('src'))
        except Exception as ex:
            self.lp.warning('Can\'t get product images. Exception: \n%s' % ex)
        finally:
            return image_urls

    def _get_product_options(self, product_options_elements):
        try:
            options = list()
            for product_option_element in product_options_elements:
                option = product_option_element.text
                options.append(option)
        except Exception as ex:
            self.lp.warning('Can\'t get product images. Exception: \n%s' % ex)
        finally:
            return options

    def get_additional_description(self, content):
        soup = BeautifulSoup(content)
        description = (soup.find('div', attrs={'id': 'tattoo'}).text).strip()
        return description