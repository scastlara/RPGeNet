# Create your views here.
from django.shortcuts import render, render_to_response
import re
from rpform.models import *

def index_view(request):
	response = dict()
	return render(request, 'rpform/index.html', response)

def gene_explorer(request):
	'''
	mygraph = GraphCyt()
	mygraph.get_genes_in_lvl(identifiers, exp_id, lvl, dist)
	response = dict()
	response['jsongraph'] = mygraph.to_json()
	return render(request, 'rpform/gexplorer.html', response)
	'''
	response = dict()
	if request.method == "POST":
		# Upload graph
		response['upload_json'] = request.FILES['myfile'].read()
		response['upload_json'] = response['upload_json'].replace("\xef\xbb\xbf", "")
	else:
		# Simple search
		# Check form request [HERE]
		genes = request.GET['gene']
		lvl = request.GET['lvl']
		exp_id = request.GET['exp']
		dist = request.GET['dist']
		genes = [ gene.upper() for gene in genes.split(",") ]
		wholegraph = GraphCyt()
		wholegraph.get_genes_in_lvl(genes, lvl, dist, exp_id)
		response['jsongraph'] = wholegraph.to_json()
	return render(request, 'rpform/gexplorer.html', response)

def pathway_explorer(request):
	'''
	mygraphs = list()
	mygene = Gene(identifier=identifier)
	mygene.check()
	mygraphs = mygene.path_to_lvl(lvl) # list of GraphCytoscape objects
	'''
	gene = request.GET['gene']
	lvl = request.GET['path-to']
	exp_id = request.GET['exp']
	print ("%s and %s and %s" % (gene, lvl, exp_id))
	response = dict()
	mygraphs = list()
	mygene = Gene(identifier=gene)
	try:
		mygene.check()
	except NodeNotFound:
		pass
	mygraphs = mygene.path_to_lvl(lvl) # list of GraphCytoscape objects
	if mygraphs:
		jsongraphs = [ graph.to_json() for graph in mygraphs ]
		response['pathways'] = jsongraphs
	return render(request, 'rpform/pexplorer.html', response)

def tutorial(request):
	'''
	TUTO HERE
	'''
	pass