from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = [
    url(r'^$', views.index_view, name='index_view'),
    url(r'^gexplorer$', views.gene_explorer, name='gene_explorer'), 
    url(r'^pathways$', views.pathway_explorer, name='pathway_explorer'),
    url(r'^add_neighbours', views.add_neighbours, name='add_neighbours'),
    url(r'^tutorial$', views.tutorial, name='tutorial'),
    url(r'^get_properties$', views.get_properties, name='get_properties'),
    url(r'^show_connections$', views.show_connections, name='show_connections'),
    url(r'^about$', views.about, name='about'),
    url(r'^data$', views.data, name='data'),
]
