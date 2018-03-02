import io
import json
import time
import requests
import zipfile
import imghdr

from providers.logging_provider import LoggingProvider


class Browser:
    _user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36")
    _accept_language = 'ru,en-US;q=0.9,en;q=0.8,de;q=0.7'

    _proxy_service_url = 'https://api.getproxylist.com/proxy?apiKey=%s'

    _settings = None

    _proxy_api_key = None

    def __init__(self):
        self.logging_provider = LoggingProvider()
        try:
            self.session = requests.Session()
            self.session.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': self._accept_language,
                'Cash-Control': 'max-age=0',
                'User-Agent': self._user_agent,
            })
        except Exception as ex:
            self.logging_provider.critical('Error while init request session; Exception: %s' % ex)

    def get_html(self, url, use_proxy=False):
        try:
            if use_proxy and self._proxy_api_key:
                proxy_dict = self.get_proxy()
                response = self.session.get(url, proxies=proxy_dict)
            else:
                response = self.session.get(url)
            html_page = response.text
            return response.status_code, html_page
        except Exception as ex:
            self.logging_provider.critical('Error in method get_html: url - %s\nException: \n%s' % (url, ex))

    def get_proxy(self):
        proxy_dict = {}
        try:
            print(self._proxy_service_url)
            print(self._proxy_api_key)
            response = self.session.get(self._proxy_service_url % self._proxy_api_key)
            json_response = json.loads(response.text)
            ip = json_response['ip']
            port = json_response['port']
            protocol = json_response['protocol']
            proxy_dict = {
                protocol: '%s://%s:%s' % (protocol, ip, port)
            }
        except Exception as ex:
            self.logging_provider.warning('Can\'t get proxy. Exception: \n"%s"' % ex)
        finally:
            return proxy_dict

    def set_settings(self, settings):
        if not settings:
            return
        self._settings = settings
        self._proxy_api_key = self._settings.proxy_api

    def download_images(self, url_list1, csv_data=None):
        url_list = []
        for url in url_list1:
            if 'https:' not in url:
                url = 'https:' + url

            url_list.append(url)
        try:
            zip_bytes = io.BytesIO()
            images_zip = zipfile.ZipFile(zip_bytes, "w")

            i = 1
            for image_url in url_list:
                image_stream = io.BytesIO()
                r = self.session.get(image_url, stream=True)
                try:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            image_stream.write(chunk)
                    image_stream.seek(0)
                    image_format = imghdr.what(image_stream)
                    image_info = zipfile.ZipInfo('%s.%s' % (i, image_format), date_time=time.localtime(time.time()))
                    #image_info.compress_type = zipfile.ZIP_DEFLATED
                    image_info.create_system = 0
                    images_zip.writestr(zinfo_or_arcname=image_info, data=image_stream.getvalue())
                    image_stream.close()
                    i += 1
                except Exception as ex:
                    pass
            if csv_data:
                product_info = zipfile.ZipInfo('info.csv', date_time=time.localtime(time.time()))
                product_info.compress_type = zipfile.ZIP_DEFLATED
                product_info.create_system = 0
                images_zip.writestr(zinfo_or_arcname=product_info, data=csv_data.getvalue())
                csv_data.close()
            images_zip.close()
        except Exception as ex:
            pass
        finally:
            return zip_bytes



