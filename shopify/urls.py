"""shopsify URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^scraping_tool/status/$', views.status, name='status'),
    url(r'^scraping_tool/start/$', views.start, name='start'),
    url(r'^scraping_tool/stop/$', views.stop, name='stop'),
    url(r'^scraping_tool/add/$', views.add, name='add'),
    url(r'^scraping_tool/delete/$', views.delete, name='delete'),
    url(r'^scraping_tool/settings/$', views.settings, name='settings'),
    url(r'^scraping_tool/$', views.index, name='index'),
    url(r'^panel/', include('shopsify_admin.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

