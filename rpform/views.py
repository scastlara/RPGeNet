# Create your views here.
from django.shortcuts import render, render_to_response
import re
from rpform.models import *
import json

def index_view(request):
	'''
	Index view
	'''
	response = dict()
	return render(request, 'rpform/index.html', response)

def gene_explorer(request):
	'''
	Look for interactions for your genes in specific levels of the
	RPGeNet graph
	'''
	response = dict()
	if request.method == "POST":
		# Upload graph
		response['upload_json'] = request.FILES['myfile'].read()
		response['upload_json'] = response['upload_json'].replace("\xef\xbb\xbf", "")
		# Check if valid json
		try:
			json.loads(response['upload_json'])
		except ValueError:
			response['not_json'] = True;
	else:
		# Simple search
		# Check form request [HERE]
		genes = request.GET['gene']
		level = request.GET['level']
		exp_id = request.GET['exp']
		dist = request.GET['dist']
		genes = [ gene.upper() for gene in genes.split(",") ]
		wholegraph = GraphCyt()
		wholegraph.get_genes_in_level(genes, level, dist, exp_id)
		if wholegraph:
			response['jsongraph'] = wholegraph.to_json()
	return render(request, 'rpform/gexplorer.html', response)

def pathway_explorer(request):
	'''
	Find Pathways from your genes to specific levels of the RPGeNet graph
	'''
	gene = request.GET['gene']
	level = request.GET['path-to']
	exp_id = request.GET['exp']
	print ("%s and %s and %s" % (gene, level, exp_id))
	response = dict()
	mygraphs = list()
	mygene = Gene(identifier=gene)
	try:
		mygene.check()
	except NodeNotFound:
		pass
	mygraphs = mygene.path_to_level(level) # list of GraphCytoscape objects
	if mygraphs:
		jsongraphs = [ graph.to_json() for graph in mygraphs ]
		response['pathways'] = jsongraphs
	return render(request, 'rpform/pexplorer.html', response)

def tutorial(request):
	'''
	Tutorial view
	'''
	return render(request, 'rpform/tutorial.html')

def data(request):
	'''
	Data view
	'''
	return render(request, 'rpform/data.html')


def about(request):
	'''
	About view
	'''
	return render(request, 'rpform/about.html')