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
	experiments = Experiment.all_from_database()
	exp_names = [ experiment.identifier for experiment in experiments ]
	response['experiments'] = exp_names
	return render(request, 'rpform/index.html', response)


def upload_graph(request):
	'''
	Uploads graph and sends it to gexplorer template
	'''
	response = dict()
	template = 'rpform/404.html'

	if request.method == "POST":
		template = 'rpform/gexplorer.html'
		experiments = Experiment.all_from_database()
		exp_names = [ experiment.identifier for experiment in experiments ]
		response['experiments'] = exp_names
		# Upload graph
		if 'myfile' in request.FILES:
			# Uploaded file
			response['upload_json'] = request.FILES['myfile'].read()
			response['upload_json'] = response['upload_json'].replace("\xef\xbb\xbf", "")
			response['withpos'] = True
		else:
			# From Path to level 'Explore Network' button
			response['upload_json'] = request.POST['myfile']
			response['exp_id'] = request.POST['exp_id']
			response['withpos'] = False # No positions specified in json
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
		genes = request.GET['gene']
		genes = re.sub(r'\s', '', genes)
		level = int(request.GET['level'])
		exp_id = request.GET['exp']
		dist = int(request.GET['dist'])
		genes = [ gene.upper() for gene in genes.split(",") ]
		wholegraph = GraphCyt()
		wholegraph.get_genes_in_level(genes, level, dist, exp_id)
		experiment = Experiment(exp_id).check()
		wholegraph.change_expression_color(experiment)
		experiments = Experiment.all_from_database()
		exp_names = [ experiment.identifier for experiment in experiments ]
		response['experiments'] = exp_names
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
			gene_obj = Gene(identifier=gene).check()
			gene_obj.get_summary()
			gene_obj.get_go()
			gene_obj.get_aliases()
			experiments = Experiment.all_from_database()
			exp_data = dict()
			for exp in experiments:
				exp_data[exp.identifier] = exp.get_gene_expression(gene_obj)
				if exp_data[exp.identifier] != "NA":
					exp_data[exp.identifier] = round(float(exp_data[exp.identifier]), 3)
			template = 'rpform/gene_properties.html'
			response['gene'] = gene_obj
			response['exp_data'] = exp_data
		else:
			# Requesting interaction
			interaction = request.GET['interaction']
			inta, intb, int_type = interaction.split('-')
			int_obj = Interaction(parent=Gene(inta), child=Gene(intb)).check()
			int_obj.fix_string_evidences()
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
			dist = 1 # Always distance 1 because we want neighbours
			wholegraph = GraphCyt()
			wholegraph.get_genes_in_level([gene], level, dist, exp_id)
			experiment = Experiment(exp_id).check()
			wholegraph.change_expression_color(experiment)
			colors = [ gene.color for gene in wholegraph.genes ]
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
	gene = request.GET['gene'].upper()
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
	experiment = Experiment(exp_id).check()
	for target, graph in mygraphs.iteritems():
		graph.get_expression(experiment)
		graph.change_expression_color(experiment)
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
	gene1 = request.GET['gene1'].upper()
	gene2 = request.GET['gene2'].upper()
	exp_id = request.GET['exp']
	response['source'] = gene1
	response['target'] = gene2
	response['exp'] = exp_id
	try:
		gene1 = Gene(identifier=gene1).check()
	except NodeNotFound as err:
		response['error'] = err
	try:
		gene2 = Gene(identifier=gene2).check()
	except NodeNotFound as err:
		response['error'] = err
	if response['error'] is False:
		allpaths = gene1.path_to_gene(gene2)
		experiment = Experiment(exp_id).check()
		for path in allpaths:
			path.get_expression(experiment)
			path.change_expression_color(experiment)
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


def change_expression(request):
	'''
	Gets expression values for a particular experiment
	and returns the necessary colors
	'''
	if request.is_ajax():
		node_ids = request.POST['nodes'].split(",")
		level = request.POST['level']
		exp_id = request.POST['exp_id']
		genes = [ Gene(identifier=ident) for ident in node_ids ]
		expressions = { gene.identifier: gene.get_expression(exp_id) for gene in genes }
		experiment = Experiment(identifier=exp_id).check()
		for gene, expval in expressions.iteritems():
			expressions[gene] = experiment.color_from_value(expval)
		return HttpResponse(json.dumps(expressions), content_type="application/json")
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
	response = dict()
	drivers = GraphCyt()
	drivers.get_drivers()
	response['drivers'] = sorted(list(drivers.genes), key=lambda x: (x.gene_disease, x.identifier))
	return render(request, 'rpform/data.html', response)


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