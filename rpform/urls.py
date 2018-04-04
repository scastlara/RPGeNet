from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = [
    url(r'^$', views.index_view, name='index_view'),
    url(r'^gexplorer$', views.gene_explorer, name='gene_explorer'), 
    url(r'^pathways$', views.pathway_explorer, name='pathway_explorer'),
    url(r'^tutorial$', views.tutorial, name='tutorial')
]
