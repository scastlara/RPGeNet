from django.db import models
from py2neo import Graph

# Create your models here.


class NeoDriver(object):
	'''
	Class for the Neo4jDriver
	'''
	def __init__(self, ip, port, user, passw):
		self.ip = ip
		self.port = port
		self.user = user
		self.passw = passw
		address = "http://%s:%s/db/data/" % (ip, port)
		print(address)
		self.dv = Graph(address, password=passw)

	def return_by_attributes(self, elem_name, attributes):
		'''
		Constructor of return clause based on a list of attributes for neo4j
		'''
		non_attributes = set(['label', 'parent', 'child', 'expression', 'gos'])
		return_clause = ",".join(['%s.%s as %s.%s' % (elem_name, attr, elem_name, attr) 
			                       for attr in attributes if attr not in non_attributes])
		return return_clause

	def query_expression(self, nodeobj, exp_id):
		'''
		Gets expression value for nodeobj
		'''
		query = """
			MATCH (node:%s)-[r:HAS_EXPRESSION]->(exp:EXPERIMENT)
			WHERE node.identifier == '%s'
			AND exp.identifier == '%s'
			RETURN r.value as expvalue
		"""
		results = self.dv.run(query)
		results = results.data()
		if results:
			nodeobj.expression = results[0]['expvalue']
		else:
			nodeobj.expression = 'NA'


	def query_gos(self, nodeobj):
		'''
		Gets the GO of the nodeobj Gene
		'''
		go_list = list()
		query = """
			MATCH (node:%s)-[r:HAS_GO]->(go:GO)
			WHERE node.identifier == '%s'
			RETURN go.accession as accession, 
				   go.description as description, 
			       go.domain as domain
		""" % (nodeobj.label, nodeobj.identifier)
		results = self.dv.run(query)
		results = results.data()
		if results:
			for go in results:
				go_list.append(GO(accession=go['accession'], 
								  description=go['description'], 
								  domain=go['domain']))
		return go_list

	def query_get_neighbours(self, nodeobj, lvl=1, dist=1, exp_id):
		'''
		Gets all nodes and edges connected to nodeobj in lvl graph
		at distance dist
		'''
		neighbour_graph = GraphCyt()

		query = """
			MATCH (node1:%s)-[r:INTERACT_WITH*%s]->(node2:%s)
			WHERE node1.identifier == '%s'
			AND r.lvl >= '%s'
			RETURN 
		""" % (nodeobj.label, dist, nodeobj.label, nodeobj.identifier, lvl)
		n_attributes = nodeobj.__dict__().keys()
		e_attributes = Interaction().__dict__().keys()
		query = query + self.return_by_attributes('node2', n_attributes)
		query = query + self.return_by_attributes('r', e_attributes)
		results = self.dv.run(query)
		results = results.data()
		if results:
			for row in results:
				node2 = Gene(results['node2.identifier'])
				node2.get_expression(exp_id)
				node2.fill_attributes(
					dc = results['node2.driver_confidence'],
					lvl = results['node2.lvl'],
					gc  = results['node2.gene_cards'],
					nvar = results['node2.nvariants'])
				interaction = Interaction(node1, node2)
				interaction.fill_attributes(
					parent=nodeobj,
					child=node2,
					inttype=results['inttype'],
					string=results['string'],
					biogrid=results['biogrid'],
					ppaxe=results['ppaxe'],
					ppaxe_pmid=results['ppaxe_pmid'],
					lvl=results['lvl'])
				neighbour_graph.add_gene(node2)
				neighbour_graph.add_int(interaction)
			return neighbour_graph
		else:
			raise Exception

	def query_by_id(self, nodeobj):
		'''
		Gets ONE node object of class o
		'''
		attributes = nodeobjs.__dict__().keys()
		query = """
			MATCH (node:%s)
			WHERE node.identifier = '%s'
			RETURN 
		""" % (label, identifier)
		query = query + self.return_by_attributes('node', attributes)
		results = self.dv.run(query)	
		results = results.data()
		if results:
			return results	
		else:
			raise NodeNotFound(self.identifier, self.label)
		

class Node(object):
	'''
	General class for nodes on neo4j
	'''
	def __init__(self, identifier, label):
		self.identifier = identifier
		self.label = label

	def query(self):
		'''
		Queries the node
		'''
		pass

	def get_neighbours(self, edge_label, attributes):
		pass

class GO(Node):
	'''
	Class for GeneOntology Nodes
	'''
	label = "GO"
	def __init__(self, accession, description, domain):
		self.accession = accession
		self.description = description
		self.domain = domain

class Interaction(object):
	'''
	Class for Gene-Gene interactions
	'''
	def __init__(self, parent=False, child=False):
		'''
		parent = Gene()
		child  = Gene()
		'''
		self.parent = parent
		self.child = child
		self.type = "genetic"
		self.string = False
		self.biogrid = False
		self.ppaxe = False
		self.ppaxe_pmid = ""
		self.lvl = 0

	def fill_attributes(self, inttype, string, biogrid, 
						ppaxe, ppaxe_pmid, lvl):
		'''
		Fills the attributes of the interaction to avoid querying db
		'''
		self.type = inttype
		self.string = string
		self.biogrid = biogrid
		self.ppaxe = ppaxe
		self.ppaxe_pmid = ppaxe_pmid
		self.lvl = lvl

	def to_json_dict(self):
		pass

class Gene(Node):
	'''
	Class for gene nodes on neo4j
	'''
	label = "GENE"
	def __init__(self, identifier):
		super(Node, self).__init__(identifier, label)
		self.driver_confidence = 0
		self.lvl = 0
		self.gene_cards = ''
		self.expression = 'NA'
		self.nvariants = 0
		self.gos = list()

	def query(self):
		'''
		Queries Gene on neo4j and fills the attributes
		'''
		results = NEO.query_by_id(self)
		self.fill_attributes(
			results['node.driver_confidence'], 
			results['node.lvl'], 
			results['node.gene_cards'],
			results['node.nvariants'])

	def fill_attributes(self, dc, lvl, gc, nvar):
		'''
		Fills the attributes of the object. Avoids querying db
		'''
		self.driver_confidence = dc
		self.lvl = lvl
		self.gene_cards = gene_cards
		self.nvariants = nvar


	def get_expression(self, exp_id):
		'''
		Gets desired expression value for Gene
		'''
		self.expression = NEO.query_expression(self, exp_id)

	def get_neighbours(self, lvl, dist, exp_id):
		'''
		Gets all the neighbours to Gene within 'lvl' interactions and at distance
		'dist' at most. All child nodes will have expression of 'exp_id'
		Returns a GraphCyt object
		'''
		ngraph = NEO.query_get_neighbours(self, lvl, dist, exp_id)
		return ngraph

	def get_go(self):
		'''
		Gets GeneOntologies of the gene
		'''
		self.gos = NEO.query_gos(self)


	def to_json_dict(self):
		pass


class GraphCyt(object):
	'''
	Gene collection and interactions collection.
	Example for FORM1 (get all genes connected to list of genes in lvl and distance)
	mygraph = GraphCyt()
	mygraph.get_genes_by_lvl(identifiers, lvl, dist, exp_id)
	mygraph.to_json()
	'''
	def __init__(self):
		self.genes = list()
		self.interactions = list()

	def get_genes_by_lvl(self, identifiers, lvl, dist=1, exp_id):
		'''
		Adds to genes collection all the genes with the specified lvl
		and matching identifiers
		'''
		for identifier in identifiers:
			gene = Gene(identifier=identifier)
			try:
				gene.query()
				gene.get_expression(exp_id)
				self.genes.add(gene)
				self.merge(gene.get_neighbours(lvl, dist, exp_id))
			except:
				continue

	def merge(self, graph):
		'''
		Merges two GraphCyt objects
		'''
		if graph.genes:
			self.genes.add(graph.genes)
		if graph.interactions:
			self.interactions.add(graph.interactions)

	def to_json(self):
		pass




NEO = NeoDriver('127.0.0.1', '7474', 'neo4j', '5961')

class NodeNotFound(Exception):
    """Exception raised when a node is not found on the db"""
    def __init__(self, identifier, label):
        self.identifier   = identifier
        self.label = label
    def __str__(self):
        return "Identifier %s not found in label %s." % (self.identifier, self.label)
