from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = [
    url(r'^$', views.index_view, name='index_view'),
    url(r'^explorer$', views.explorer, name='explorer')
]
