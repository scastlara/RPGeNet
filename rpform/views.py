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
	mygraph.get_genes_in_lvl(identifiers, lvl, dist, exp_id)
	response = dict()
	response['jsongraph'] = mygraph.to_json()
	return render(request, 'rpform/explorer.html', response)
	'''
	pass

def pathway_explorer(request):
	
	pass