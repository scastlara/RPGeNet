# Create your views here.
from django.shortcuts import render, render_to_response
from django.http      import HttpResponse
from django.template import RequestContext
import re
from rpform.models import *
import json

def index_view(request):
	'''
	Index view
	'''
	response = dict()
	return render(request, 'rpform/index.html', response)


def upload_graph(request):
	'''
	Uploads graph and sends it to gexplorer template
	'''
	response = dict()
	template = 'rpform/404.html'

	if request.method == "POST":
		template = 'rpform/gexplorer.html'

		# Upload graph
		if 'myfile' in request.FILES:
			# Uploaded file
			response['upload_json'] = request.FILES['myfile'].read()
			response['upload_json'] = response['upload_json'].replace("\xef\xbb\xbf", "")
			response['with_pos'] = True
		else:
			# From Path to level 'Explore Network' button
			response['upload_json'] = request.POST['myfile']
			response['exp_id'] = request.POST['exp_id']
			response['with_pos'] = False # No positions specified in json
		response['level'] = request.POST['upload-level']

		# Check if valid json
		try:
			json.loads(response['upload_json'])
		except ValueError:
			response['not_json'] = True;
	return render(request, template, response)
		

def gene_explorer(request):
	'''
	Look for interactions for your genes in specific levels of the
	RPGeNet graph
	'''
	response = dict()
	if request.method == "GET":
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
			gene_obj.get_go()
			template = 'rpform/gene_properties.html'
			response['gene'] = gene_obj
		else:
			# Requesting interaction
			interaction = request.GET['interaction']
			inta, intb, int_type = interaction.split('-')
			int_obj = Interaction(parent=Gene(inta), child=Gene(intb))
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
			x = request.GET['x']
			y = request.GET['y']
			dist = 1 # Always distance 1
			wholegraph = GraphCyt()
			wholegraph.get_genes_in_level([gene], level, dist, exp_id)
			json_data = wholegraph.to_json((x,y))
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
	level = int(request.GET['path-to'])
	exp_id = request.GET['exp']
	response = dict()
	response['gene'] = gene
	response['level'] = "Drivers"
	if level == 0:
		response['level'] = "Skeleton"
	response['exp'] = exp_id
	response['appname'] = "Pathway to Level"
	mygraphs = list()
	mygene = Gene(identifier=gene)
	try:
		mygene.check()
	except NodeNotFound:
		pass
	mygraphs = mygene.path_to_level(level) # list of GraphCytoscape objects
	if mygraphs:
		response['plen'] = len(mygraphs[mygraphs.keys()[0]].interactions)
		response['numpaths'] = len(mygraphs.keys())
		response['pathways'] = { target: graph.to_json() for target, graph in mygraphs.iteritems() }
	return render(request, 'rpform/pexplorer.html', response)


def shortest_path(request):
	'''
	Finds shortest paths between two genes
	'''
	response = dict()
	response['error'] = False
	response['appname'] = "Shortest Paths"
	gene1 = request.GET['gene1']
	gene2 = request.GET['gene2']
	exp_id = request.GET['exp']
	response['source'] = gene1
	response['target'] = gene2
	response['exp'] = exp_id
	try:
		gene1 = Gene(identifier=gene1)
		gene1.check()
	except NodeNotFound as err:
		response['error'] = err
	try:
		gene2 = Gene(identifier=gene2)
		gene2.check()
	except NodeNotFound as err:
		response['error'] = err

	if response['error'] is False:
		allpaths = gene1.path_to_gene(gene2)
		response['plen'] = len(allpaths[0].interactions)
		response['numpaths'] = len(allpaths)
		response['pathways'] = { idx:allpaths[idx].to_json() for idx in range(0, len(allpaths)) }
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


def handler404(request):
    """
    Handler for error 404, doesn't work.
    """
    response = render_to_response('rpform/404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    """
    Handler for error 500 (internal server error), doesn't work.
    """
    response = render_to_response('rpform/500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response