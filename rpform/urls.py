from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = [
    url(r'^$', views.index_view, name='index_view'),
    url(r'^explorer$', views.gene_explorer, name='gene_explorer'), 
    url(r'^pathways$', views.pathway_explorer, name='pathway_explorer'),
    url(r'^upload_graph$', views.upload_graph, name='upload_graph'),
    url(r'^tutorial$', views.tutorial, name='tutorial')
]
