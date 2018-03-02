from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser,Group
from django.utils.encoding import smart_str
from datetime import datetime

class UserGroups(Group):
    number_of_sites = models.IntegerField()
    def __unicode__(self):
        return self.number_of_sites


class User(AbstractUser):
    customer = models.BooleanField(blank=True, default=False)
    image = models.ImageField(default='default-avatar.jpg')


class ShopifySiteCategoryModel(models.Model):
    name = models.CharField(max_length=200, default='', unique=True, verbose_name='Name')
    description = models.TextField(max_length=1000, default='', verbose_name='Description')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return smart_str('%s' % self.name)

    def __unicode__(self):
        return '%s' % self.name


class ShopifySiteModel(models.Model):
    site_category = models.ForeignKey(ShopifySiteCategoryModel, null=True, verbose_name='Category')
    name = models.CharField(max_length=100, verbose_name='Name')
    url = models.CharField(max_length=100, default='http://example.com', verbose_name='Url')
    total_products = models.IntegerField(default=0, verbose_name='Total products')
    last_update_date = models.DateTimeField(default=datetime.now(), verbose_name='Date Updated')
    status = models.CharField(max_length=20, default='None')

    class Meta:
        verbose_name = "Site"

    def __str__(self):
        return smart_str(self.name)


class ShopifySettingsModel(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')
    proxy_api = models.CharField(max_length=100, default='', verbose_name='Proxy api key')
    update_period = models.IntegerField(default=60, verbose_name='Update after (sec)')

    class Meta:
        verbose_name = "Setting"

    def __str__(self):
        return smart_str(self.name)


class ShopifyProductModel(models.Model):
    website = models.ForeignKey(ShopifySiteModel, null=True, verbose_name='Parent website')
    html = models.TextField(default='')
    title = models.CharField(max_length=200, default='', verbose_name='Title')
    category = models.CharField(max_length=200, default='', verbose_name='Category', null=True)
    url = models.URLField(max_length=200, default='', verbose_name='Url')
    description = models.TextField(default='', verbose_name='Short description')
    price = models.CharField(max_length=200, default='', verbose_name='Price', null=True)
    sale_price = models.CharField(max_length=200, default='', verbose_name='Sale price', null=True)
    currency = models.CharField(max_length=200, default='', verbose_name='Currency', null=True)
    images = models.CharField(max_length=2000, default='', verbose_name='Image URLs')
    date_added = models.DateTimeField(default=datetime.now(), verbose_name='Time Extracted')
    options = models.CharField(max_length=2000, default='', verbose_name='Options')
    tags = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = "Product"

    def __str__(self):
        return smart_str(self.title)

    def get_first_image(self):
        return self.images.split(';')[0]


