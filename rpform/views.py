# Create your views here.
from django.shortcuts import render, render_to_response

def index_view(request):
	response = dict()
	response['variable'] = "value"
	response['anothervariable'] = "anothervalue"
	return render(request, 'rpform/index.html', response)

def explorer(request):
	'''
	mygraph = GraphCyt()
	mygraph.get_genes_by_lvl(identifiers, lvl, dist, exp_id)
	response = dict()
	response['jsongraph'] = mygraph.to_json()
	return render(request, 'rpform/explorer.html', response)
	'''
	pass

'''
def explorer(request):
	genename = request.GET['genename']
	level = request.GET['level']
	distance = request.GET['distance']

	mygraph = GraphCytoscape()
	mygraph.find_nodes(nodes=genename, level=level, distance=distance)
	if mygraph.has_nodes():
		myjson = mygraph.transform_to_json()
		return render(request, 'rpform/explorer.html', {'error': 'no-error', json': myjson})
	else:
		return (render, 'rpform/explorer.html', {'error': 'no genes found'})
'''
