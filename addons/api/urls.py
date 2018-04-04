from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
                       path('', include('addons.api.auth_manage')),
                       ]
