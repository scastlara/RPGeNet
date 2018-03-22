from django.db import models
from py2neo import Graph
import json


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
        self.dv = Graph(address, password=passw)

    def return_by_attributes(self, elem_name, attributes):
        '''
        Constructor of return clause based on a list of attributes for neo4j
        '''
        non_attributes = set(['label', 'parent', 'child', 'expression', 'gos'])
        return_clause = ",".join(['%s.%s as %s_%s' % (elem_name, attr, elem_name, attr) 
                                   for attr in attributes if attr not in non_attributes])
        return return_clause

    def query_by_id(self, nodeobj):
        '''
        Gets ONE node object of class 
        '''
        attributes = nodeobj.__dict__.keys()
        query = """
            MATCH (node:%s)
            WHERE node.identifier = '%s'
            RETURN 
        """ % (nodeobj.label, nodeobj.identifier)
        query = query + self.return_by_attributes('node', attributes)
        results = self.dv.run(query)    
        results = results.data()
        if results:
            nodeobj.fill_attributes(
            results['node_driver_confidence'], 
            results['node_lvl'], 
            results['node_gene_cards'],
            results['node_nvariants'])
        else:
            raise NodeNotFound(nodeobj.identifier, nodeobj.label)

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

    def query_get_neighbours(self, nodeobj, exp_id, lvl=1, dist=1):
        '''
        Gets all nodes and edges connected to nodeobj in lvl graph
        at distance dist
        '''
        neighbour_graph = GraphCyt()
        neighbour_graph.genes.add(nodeobj)
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
                node2 = Gene(results['node2_identifier'])
                node2.get_expression(exp_id)
                node2.fill_attributes(
                    dc=results['node2_driver_confidence'],
                    lvl=results['node2_lvl'],
                    gc=results['node2_gene_cards'],
                    nvar=results['node2_nvariants'])
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
                neighbour_graph.genes.add(node2)
                neighbour_graph.interactions.add(interaction)
            return neighbour_graph
        else:
            raise Exception

    def query_path_to_drivers(self, nodeobj):
        '''
        Shortest paths to driver genes
        '''
        query = ''
        if nodeobj.is_driver():
            query = """
                MATCH  p=(source:Gene)-[r:INTERACT_WITH*]->(target:Gene)
                WHERE  r.is_path == 1
                AND    source.identifier == '%s'
                AND    target.driver_confidence >= 1
                RETURN p
                ORDER BY LENGTH(p) DESC
            """ % nodeobj.identifier
        else:
            query = """
                MATCH  p=allShortestPaths((source:Gene)-[r:INTERACT_WITH*]->(target:Gene))
                WHERE  source.identifier == '%s'
                AND    target.driver_confidence >= 1
                RETURN p
                ORDER BY LENGTH(p) DESC
            """ % nodeobj.identifier

        results = self.dv.run(query)
        results = results.data()
        for path in results:
            # Must create a list of GraphCytoscape object here
            pass

    def query_shortest_path(self, pobj, cobj):
        '''
        Returns GraphCytoscape with shortest path between pobj and cobj
        '''
        query = """
            MATCH p=shortestPath((s:Gene)-[r:INTERACT_WITH*]->(t:Gene))
            WHERE s.identifier == '%s'
            AND   t.identifier == '%s'
            RETURN p
        """ % (pobj.identifier, cobj.identifier)
        results = self.dv.run(query)
        results = results.data()
        if results:
            path = results[0]
            # Create GraphCytoscape object here

class Node(object):
    '''
    General class for nodes on neo4j
    '''
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label

    def check(self):
        '''
        Queries the node
        '''
        pass


class GO(Node):
    '''
    Class for GeneOntology Nodes
    '''
    def __init__(self, accession, description, domain):
        label = "GO"
        super(Go, self).__init__(identifier, label)
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
        self.is_path = False
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
        '''
        Returns dictionary ready to convert to json
        '''
        element = dict()
        element['data'] = dict()
        element['data']['id'] = self.parent.identifier + '-' + self.child.identifier
        element['data']['source'] = self.parent.identifier
        element['data']['target'] = self.child.identifier
        return element

    def __hash__(self):
        return hash((self.parent.identifier, self.child.identifier, self.lvl, self.type))


class Gene(Node):
    '''
    Class for gene nodes on neo4j
    '''
    def __init__(self, identifier):
        label = "GENE"
        super(Gene, self).__init__(identifier, label)
        self.driver_confidence = None
        self.lvl = 0
        self.gene_cards = ''
        self.expression = 'NA'
        self.nvariants = 0
        self.gos = list()

    def check(self):
        '''
        Queries Gene on neo4j and fills the attributes.
        If not in database: NodeNotFound
        '''
        NEO.query_by_id(self)

    def fill_attributes(self, dc, lvl, gc, nvar):
        '''
        Fills the attributes of the object. Avoids querying db
        '''
        self.driver_confidence = dc
        self.lvl = lvl
        self.gene_cards = gene_cards
        self.nvariants = nvar

    def is_driver(self):
        '''
        Checks if gene is driver or not
        '''  
        if self.driver_confidence is None:
            try:
                self.check()
            except:
                return False
                
        if self.driver_confidence == 0:
            return False
        else:
            return True

    def get_expression(self, exp_id):
        '''
        Gets desired expression value for Gene
        '''
        self.expression = NEO.query_expression(self, exp_id)
        return self.expression

    def get_neighbours(self, exp_id, lvl, dist):
        '''
        Gets all the neighbours to Gene within 'lvl' interactions and at distance
        'dist' at most. All child nodes will have expression of 'exp_id'
        Returns a GraphCyt object
        '''
        ngraph = NEO.query_get_neighbours(self, exp_id, lvl, dist)
        return ngraph

    def get_go(self):
        '''
        Gets GeneOntologies of the gene
        '''
        self.gos = NEO.query_gos(self)
        return self.gos

    def to_json_dict(self):
        '''
        Returns dictionary ready to convert to json
        '''
        element = dict()
        element['data'] = dict()
        element['data']['id'] = self.identifier
        element['data']['name'] = self.identifier
        element['data']['lvl'] = self.lvl
        element['data']['exp'] = self.expression
        element['data']['driver_confidence'] = self.driver_confidence
        element['data']['nvariants'] = self.nvariants
        element['data']['gos'] = self.gos
        if self.is_driver():
            element['classes'] = "driver"
        return element

    def path_to_drivers(self):
        '''
        Returns a list of GraphCytoscape object with all shortest paths to all drivers
        '''
        paths = NEO.query_path_to_drivers(self)
        return paths

    def path_to_gene(self, cobj):
        '''
        Shortest path to Gene Object
        '''
        path = NEO.query_shortest_path(self, cobj)
        return path

    def __hash__(self):
        return hash((self.identifier, self.driver_confidence))


class GraphCyt(object):
    '''
    Gene collection and interactions collection.
    Example for FORM1 (get all genes connected to list of genes in lvl and distance)
    mygraph = GraphCyt()
    mygraph.get_genes_by_lvl(identifiers, lvl, dist, exp_id)
    mygraph.to_json()
    '''
    def __init__(self):
        self.genes = set()
        self.interactions = set()

    def get_genes_in_lvl(self, identifiers, exp_id, lvl=1, dist=1):
        '''
        Adds to genes collection all the genes with the specified lvl
        and matching identifiers
        '''
        for identifier in identifiers:
            gene = Gene(identifier=identifier)
            try:
                gene.check()
                gene.get_expression(exp_id)
                self.genes.add(gene)
                self.merge(gene.get_neighbours(lvl, dist, exp_id))
            except:
                continue

    def merge(self, graph):
        '''
        Merges self with GraphCyt object
        '''
        if graph.genes:
            self.genes.add(graph.genes)
        if graph.interactions:
            self.interactions.add(graph.interactions)

        pass

    def to_json(self):
        """
        Converts the graph to a json string to add it to cytoscape.js
        """
        graphelements = {
            'nodes': [gene.to_jsondict() for gene in self.genes],
            'edges': [edge.to_jsondict() for edge in self.interactions]
        }
        graphelements = json.dumps(graphelements)
        return graphelements


NEO = NeoDriver('127.0.0.1', '7474', 'neo4j', '5961')


class NodeNotFound(Exception):
    """Exception raised when a node is not found on the db"""
    def __init__(self, identifier, label):
        self.identifier   = identifier
        self.label = label
    def __str__(self):
        return "Identifier %s not found in label %s." % (self.identifier, self.label)
