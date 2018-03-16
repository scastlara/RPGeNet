# Create your views here.
from django.shortcuts import render, render_to_response

def index_view(request):
	response = dict()
	response['variable'] = "value"
	response['anothervariable'] = "anothervalue"
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
	return render(request, 'rpform/gexplorer.html', response)

def pathway_explorer(request):
	'''
	mygraphs = list()
	mygene = Gene(identifier=identifier)
	mygene.check()
	mygraphs = mygene.path_to_drivers() # list of GraphCytoscape objects
	'''
	pass

def tutorial(request):
	'''
	TUTO HERE
	'''
	pass