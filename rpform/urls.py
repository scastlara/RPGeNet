import os
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
# from django.conf.urls import url
from . import views
from django.contrib import admin

# basedirpath = settings.BASE_DIR
# os.path.join(basedirpath, )

admin.autodiscover()
urlpatterns = [
    # url(r'^static/.*$', views.static.serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^RPGeNet/$', views.index_view, name='index_view'),
    url(r'^RPGeNet/gexplorer$', views.gene_explorer, name='gene_explorer'), 
    url(r'^RPGeNet/pathways$', views.pathway_explorer, name='pathway_explorer'),
    url(r'^RPGeNet/shortest_path$', views.shortest_path, name='shortest_path'),
    url(r'^RPGeNet/upload_graph$', views.upload_graph, name='upload_graph'),
    url(r'^RPGeNet/add_neighbours', views.add_neighbours, name='add_neighbours'),
    url(r'^RPGeNet/change_expression', views.change_expression, name='change_expression'),
    url(r'^RPGeNet/get_properties$', views.get_properties, name='get_properties'),
    url(r'^RPGeNet/show_connections$', views.show_connections, name='show_connections'),
    url(r'^RPGeNet/tutorial$', views.tutorial, name='tutorial'),
    url(r'^RPGeNet/about$', views.about, name='about'),
    url(r'^RPGeNet/data$', views.data, name='data'),
] + staticfiles_urlpatterns()
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
