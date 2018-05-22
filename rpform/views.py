# Create your views here.
from django.shortcuts import render, render_to_response
from django.http      import HttpResponse
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
		response['level'] = request.POST['upload-level']
		# Check if valid json
		try:
			json.loads(response['upload_json'])
		except ValueError:
			response['not_json'] = True;
	else:
		# Simple search
		# Check form request [HERE]
		genes = request.GET['gene']
		genes = re.sub(r'\s', '', genes)
		level = request.GET['level']
		exp_id = request.GET['exp']
		dist = request.GET['dist']
		genes = [ gene.upper() for gene in genes.split(",") ]
		wholegraph = GraphCyt()
		wholegraph.get_genes_in_level(genes, level, dist, exp_id)
		if wholegraph:
			response['jsongraph'] = wholegraph.to_json()
		response['level'] = level
		response['dist']  = dist
		response['exp_id'] = exp_id
	return render(request, 'rpform/gexplorer.html', response)

def get_properties(request):
	'''
	Returns information about a particular gene when clicked
	'''
	if request.is_ajax():
		response = dict()
		template = ''
		if 'gene' in request.GET:
			# Requesting gene
			gene = request.GET['gene']
			gene_obj = Gene(identifier=gene)
			gene_obj.check()
			#gene_obj.get_go()
			template = 'rpform/gene_properties.html'
			response['gene'] = gene_obj
		else:
			# Requesting interaction
			interaction = request.GET['interaction']
			inta, intb, int_type = interaction.split('-')
			int_obj = Interaction(parent=Gene(inta), child=Gene(intb))
			int_obj.restrict_type(int_type)
			int_obj.check()
			template = 'rpform/int_properties.html'
			response['interaction'] = int_obj
		return render(request, template, response)
	else:
		return render(request, 'rpform/404.html')

def add_neighbours(request):
	'''
	Returns json from AJAX request to add neighbours to clicked nodes on gexplorer
	'''
	if request.is_ajax():
		response = dict()
		if 'gene' in request.GET and 'level' in request.GET and 'exp' in request.GET:
			gene = request.GET['gene']
			level = request.GET['level']
			exp_id = request.GET['exp']
			dist = 1 # Always distance 1
			wholegraph = GraphCyt()
			wholegraph.get_genes_in_level([gene], level, dist, exp_id)
			json_data = wholegraph.to_json()
			return HttpResponse(json_data, content_type="application/json")
		else:
			return HttpResponse(json.dumps(json_data), content_type="application/json")
	else:
		return render(request, 'rpform/404.html')


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

def show_connections(request):
    """
    View that handles an AJAX request and, given a list of identifiers, returns
    all the interactions between those identifiers/nodes.
    """
    if request.is_ajax():
        nodes_including = request.POST['nodes'].split(",")
        level = request.POST['level']
        graphelements   = GraphCyt()
        for symbol in nodes_including:
            graphelements.add_gene( Gene(identifier=symbol) )
        connections = graphelements.get_connections(level)
        connections = connections.to_json()
        return HttpResponse(connections, content_type="application/json")
    else:
        return render(request, 'rpform/404.html')

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