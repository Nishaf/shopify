import json
import time
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.shortcuts import render

from shopsify_admin.models import ShopifyProductModel,ShopifySiteModel,ShopifySettingsModel,User


#from providers.logging_provider import LoggingProvider
from shopify_scrapers.shopify_scraper import ShopifyScraper
from datetime import datetime


try:
    scraper_settings = ShopifySettingsModel.objects.order_by('-name')
    scraper = ShopifyScraper(scraper_settings[0])
except:
    scraper = ''
#lp = LoggingProvider()
in_progress = False


@login_required(login_url='login')
def index(request):
    if request.method == 'POST':
        request_paths = {
            '/status/': status,
            '/start/': start,
            '/stop/': stop,
            '/add/': add,
            '/settings/': settings,
            '/delete/': delete
        }
        return request_paths[request.path](request)

    websites_list = ShopifySiteModel.objects.order_by('-name')
    settings_list = ShopifySettingsModel.objects.order_by('-name')

    context = {
        'sites': websites_list,
        'settings_list': settings_list
    }
    return render(request, 'scraping_tool.html', context)


def add(request):
    websites_list = ShopifySiteModel.objects.order_by('-name')
    result = {}
    response = HttpResponse(content_type='application/json')
    try:
        website_name = request.POST['website_name']
        website_url = request.POST['website_url']
        print(website_name, website_url)
        is_exist = False
        for website in websites_list:
            if website.name.lower() == website_name.lower()\
                    or website.url.lower() == website_url.lower():
                is_exist = True
                break
        if not is_exist:
            is_shopify_site = scraper.is_shopify_site(website_url)
            if is_shopify_site:
                new_website = ShopifySiteModel(name=website_name, url=website_url)
                new_website.save()
                result['success'] = True
            else:
                result['success'] = False
                result['message'] = 'Website isn\'t SHOPIFY!'
        else:
            result['success'] = False
            result['message'] = 'Website with this URL or name already exist!'
    except Exception as ex:
        result['success'] = False
        result['message'] = 'Exception was thrown: "%s"' % ex
    finally:
        json_result = json.dumps(result)
        response.write(json_result)
        return response


def delete(request):
    response = HttpResponse(content_type='application/json')
    result = {}
    try:
        ids_to_delete = request.POST.getlist('ids_to_delete[]')
        for id_to_delete in ids_to_delete:
            website = ShopifySiteModel.objects.get(id=id_to_delete)
            website.delete()
        result['success'] = True
    except Exception as ex:
        result['success'] = False
    finally:
        json_result = json.dumps(result)
        response.write(json_result)
        return response


def settings(request):
    response = HttpResponse(content_type='application/json')
    result = {}
    try:
        settings_list = ShopifySettingsModel.objects.order_by('-name')
        proxy_api_key = request.POST['proxy_api_key']
        update_period = request.POST['update_period']
        for settings_entry in settings_list:
            settings_entry.proxy_api = proxy_api_key
            settings_entry.update_period = int(update_period)
            settings_entry.save()
            scraper.set_settings(settings_entry)
        result['success'] = True
        print('Successfully Updated settings.')
    except Exception as ex:
        result['success'] = False
        result['message'] = 'Exception was thrown: "%s"' % ex
    finally:
        json_result = json.dumps(result)
        response.write(json_result)
        return response


def start(request):
    global in_progress
    result = {}
    response = HttpResponse(content_type='application/json')
    try:
        print('Trying')
        print(in_progress)
        in_progress = True
        scraper_products()
        result['success'] = True
    except Exception as ex:
        result['success'] = False
        result['message'] = 'Exception was thrown: "%s"' % ex
    finally:

        print('finally')
        json_result = json.dumps(result)
        response.write(json_result)
        in_progress = False
        return response


def stop(request):
    global in_progress
    response = HttpResponse(content_type='application/json')
    scraper.stop()
    in_progress = False
    return response


def status(request):
    global in_progress
    print(in_progress)
    scraper_status = scraper.get_status()
    scraper_status['in_progress'] = in_progress
    json_status = json.dumps(scraper_status)
    response = HttpResponse(content_type='application/json')
    response.write(json_status)
    return response


def create_entries(all_products_info, website_id, website_name):
    for product_info in all_products_info:
        products = ShopifyProductModel.objects.filter(url=product_info['Url'])
        products_count = products.count()
        if products_count:
            is_product_changed = product_changed(products[0], product_info)
            if is_product_changed:
                update_product(products[0], product_info)
            else:
                continue
        try:
            site = ShopifySiteModel.objects.filter(id=website_id)[0]
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
                images=get_list_string(product_info['Images']),
                options=get_list_string(product_info['Options']))
            entry.save()
        except Exception as ex:
            #lp.warning('Some problem while creating entry.\n Exception: "%s"' % ex)
            pass


def product_changed(product, product_info):
    if product.title == product_info['Title'] and \
        product.category == product_info['Category'] and \
        product.description == product_info['Description'] and \
        product.price == product_info['Price'] and \
        product.sale_price == product_info['Sale price']:
        return False
    return True


def update_product(product, product_info):
    product.title = product_info['Title']
    product.category = product_info['Category']
    product.description = product_info['Description']
    product.price = product_info['Price']
    product.sale_price = product_info['Sale price']
    product.save()


def update_website_info(website_id, scraper_status):
    try:
        website = ShopifySiteModel.objects.get(id=website_id)
        website.total_products = scraper_status['total_products']
        website.last_update_date = datetime.now()
        website.last_status = 'Success' if scraper_status['success'] else 'Failed'
        website.save()
    except Exception as ex:
        pass


def get_list_string(list):
    result = ''
    for item in list:
        try:
            result += '%s;' % item.replace('\n', '')
        except Exception as ex:
            continue
    return result


def scraper_products():
    global in_progress

    while True:
        if not in_progress:
            return
        websites_list = ShopifySiteModel.objects.order_by('-name')
        settings_list = ShopifySettingsModel.objects.order_by('-name')

        update_period = 0

        for settings_item in settings_list:
            update_period = settings_item.update_period

        for website in websites_list:
            if in_progress:
                all_products_info = scraper.scrape(website.url, website.id)
                #scraper_status = scraper.get_status()
                #reate_entries(all_products_info, website_id=website.id, website_name=website.name)
                #update_website_info(website_id=website.id, scraper_status=scraper_status)
        time.sleep(update_period)



