from django.db import models
from py2neo import Graph
import json


class NeoDriver(object):
    '''
    Class for the Neo4jDriver
    '''
    def __init__(self, ip, port, bolt_port, user, passw):
        self.ip = ip
        self.port = port
        self.user = user
        self.passw = passw
        address = "http://%s:%s/db/data/" % (ip, port)
        self.dv = Graph(address, password=passw, bolt_port=bolt_port)

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
        results = results.data()[0]
        if results:
            nodeobj.fill_attributes(
                results['node_level'], 
                results['node_nvariants'],
                results['node_gene_disease'], 
                results['node_inheritance_pattern'])
        else:
            raise NodeNotFound(nodeobj.identifier, nodeobj.label)

    def query_expression(self, nodeobj, exp_id):
        '''
        Gets expression value for nodeobj
        '''
        query = """
            MATCH (node:%s)-[r:HAS_EXPRESSION]->(exp:EXPERIMENT)
            WHERE node.identifier = '%s'
            AND exp.identifier = '%s'
            RETURN r.value as expvalue
        """ % (nodeobj.label, nodeobj.identifier, nodeobj.identifier)
        results = self.dv.run(query)
        results = results.data()
        if results:
            nodeobj.expression = results[0]['expvalue']
        else:
            nodeobj.expression = 'NA'


    def query_get_connections(self, genelist, level):
        '''
        Gets connections for a list of Gene objects
        '''
        gene_q_string = str(list([str(gene.identifier) for gene in genelist]))
        query = """
            MATCH (n:GENE)-[r:INTERACTS_WITH]-(m:GENE)
            WHERE n.identifier IN %s
            AND   m.identifier IN %s
            RETURN n.identifier AS nidientifier,
                   m.identifeir AS midentifier,
                   r.level      AS rlevel,
                   r.type       AS rtype,
                   r.ppaxe      AS rppaxe,
                   r.ppaxe_pmid AS rppaxe_pmid,
                   r.biogrid    AS rbiogrid,
                   r.string     AS rstring
        """ % (gene_q_string, gene_q_string)
        results = self.dv.run(query)
        results = results.data()
        ints = list()
        if results:
            for interaction in results:
                ints.append(Interaction(
                    parent=Gene(identifier=interaction['nidientifier']),
                    child=Gene(identifier=interaction['midentifier']),
                    type=interaction['rtype'],
                    level=interaction['rlevel'],
                    ppaxe=interaction['rppaxe'],
                    ppaxe_pmid=interaction['rppaxe_pmid'],
                    biogrid=interaction['r.biogrid'],
                    string=interaction['r.string']))
        return ints

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

    def query_get_neighbours(self, nodeobj, level=1, dist=1, exp_id="ABSOLUTE"):
        '''
        Gets all nodes and edges connected to nodeobj in level graph
        at distance dist
        '''
        neighbour_graph = GraphCyt()
        neighbour_graph.genes.add(nodeobj)
        query = """
            MATCH (node1:%s)-[r:INTERACTS_WITH*1..%s]-(node2:%s)
            WHERE node1.identifier = '%s'
            AND  ALL(rel in r WHERE rel.level <= %s)
            RETURN 
        """ % (nodeobj.label, dist, nodeobj.label, nodeobj.identifier, level)
        n_attributes = nodeobj.__dict__.keys()
        e_attributes = Interaction().__dict__.keys()
        query = query + self.return_by_attributes('node2', n_attributes)
        query = query + ',' + "r as rel"
        results = self.dv.run(query)
        results = results.data()
        if results:
            # Add genes first
            for row in results:
                node2 = Gene(row['node2_identifier'])
                node2.get_expression(exp_id)
                node2.fill_attributes(
                    level=row['node2_level'],
                    nvar=row['node2_nvariants'],
                    dc=row['node2_gene_disease'],
                    inh=row['node2_inheritance_pattern'])
                neighbour_graph.genes.add(node2)
            for row in results:
                for interaction in row['rel']:
                    gene1 = neighbour_graph.return_gene(interaction['gene_1'])
                    gene2 = neighbour_graph.return_gene(interaction['gene_2'])
                    interaction_obj = Interaction(parent=gene1, child=gene2)
                    interaction_obj.fill_attributes(
                        level=interaction['level'], 
                        string=interaction['string'], 
                        biogrid=interaction['biogrid'], 
                        ppaxe=interaction['ppaxe'], 
                        ppaxe_score=interaction['ppaxe_score'],
                        ppaxe_pubmedid=interaction['ppaxe_pubmedid'], 
                        biogrid_pubmedid=interaction['biogrid_pubmedid'], 
                        genetic_interaction=interaction['genetic_interaction'], 
                        physical_interaction=interaction['physical_interaction'], 
                        unknown_interaction=interaction['unknown_interaction'])
                    neighbour_graph.interactions.add(interaction_obj)
            return neighbour_graph
        else:
            raise Exception

    def query_path_to_level(self, nodeobj, level):
        '''
        Shortest paths between 'node' and any node in level 'level'
        '''
        pass
    '''
    def query_path_to_drivers(self, nodeobj):
        #Shortest paths to driver genes
        query = ''
        if nodeobj.is_driver():
            query = """
                MATCH  p=(source:Gene)-[r:INTERACTS_WITH*]->(target:Gene)
                WHERE  r.is_path == 1
                AND    source.identifier == '%s'
                AND    target.gene_disease >= 1
                RETURN p
                ORDER BY LENGTH(p) DESC
            """ % nodeobj.identifier
        else:
            query = """
                MATCH  p=allShortestPaths((source:Gene)-[r:INTERACTS_WITH*]->(target:Gene))
                WHERE  source.identifier == '%s'
                AND    target.gene_disease >= 1
                RETURN p
                ORDER BY LENGTH(p) DESC
            """ % nodeobj.identifier

        results = self.dv.run(query)
        results = results.data()
        for path in results:
            # Must create a list of GraphCytoscape object here
            pass
    '''
    def query_shortest_path(self, pobj, cobj):
        '''
        Returns GraphCytoscape with shortest path between pobj and cobj
        '''
        query = """
            MATCH p=shortestPath((s:Gene)-[r:INTERACTS_WITH*]->(t:Gene))
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
        type = 1 -> genetic
        type = 2 -> ppi
        type = 3 -> both
        type = 4 -> unknown
        '''
        self.parent = parent
        self.child = child
        self.level = 0
        self.string = False
        self.biogrid = False
        self.ppaxe = False
        self.ppaxe_score = 0
        self.ppaxe_pubmedid = "NA"
        self.biogrid_pubmedid = "NA"
        self.genetic_interaction = 0
        self.physical_interaction = 0
        self.unknown_interaction = 0

    def fill_attributes(self, level, string, biogrid, 
                        ppaxe, ppaxe_score, ppaxe_pubmedid, biogrid_pubmedid, 
                        genetic_interaction=0, physical_interaction=0, 
                        unknown_interaction=0):
        '''
        Fills the attributes of the interaction to avoid querying db
        '''
        self.level = level
        self.string = string
        self.biogrid = biogrid
        self.ppaxe = ppaxe
        self.ppaxe_score = ppaxe_score
        self.ppaxe_pubmedid = ppaxe_pubmedid
        self.biogrid_pubmedid = biogrid_pubmedid
        self.genetic_interaction = genetic_interaction
        self.physical_interaction = physical_interaction
        self.unknown_interaction = unknown_interaction
   

    def to_json_dict(self):
        '''
        Returns dictionary ready to convert to json
        '''
        type_idx = 0
        type_names = ["physical", "genetic", "unknown"]
        types = (self.physical_interaction, self.genetic_interaction, self.unknown_interaction)
        elements = list()
        for typeint in types:
            if int(typeint) == 0:
                type_idx += 1
                continue
            else:
                element = dict()
                element['data'] = dict()
                element['data']['id'] = self.parent.identifier + '-' + self.child.identifier + '-' + type_names[type_idx]
                element['data']['source'] = self.parent.identifier
                element['data']['target'] = self.child.identifier
                element['data']['width']  = types[type_idx]
                element['classes'] = type_names[type_idx]
                elements.append(element)
                type_idx += 1
        return elements

    def __hash__(self):
        return hash((self.parent.identifier, self.child.identifier, self.level))


class Gene(Node):
    '''
    Class for gene nodes on neo4j
    identifier: STRING
    level: [ 0 | 1 | 2 | 3 | 4 | 5 ]
    nvariants: INT
    gene_disease: 
        0 (non-driver)
        1 (Syndromic)
        2 (Non-Syndromic)
        3 (Both)
        4 (Unknown)

    '''
    def __init__(self, identifier):
        label = "GENE"
        super(Gene, self).__init__(identifier, label)
        self.gene_disease = None
        self.level = 0
        self.expression = 'NA'
        self.nvariants = 0
        self.gos = list()
        self.inheritance_pattern = 0

    def check(self):
        '''
        Queries Gene on neo4j and fills the attributes.
        If not in database: NodeNotFound
        '''
        NEO.query_by_id(self)

    def fill_attributes(self, level, nvar, dc, inh):
        '''
        Fills the attributes of the object. Avoids querying db
        '''
        self.level = level
        self.nvariants = nvar
        self.gene_disease = dc
        self.inheritance_pattern = inh

    def is_driver(self):
        '''
        Checks if gene is driver or not
            # gene_disease = 0 -> No-driver
            # gene_disease = 1 -> Syndromic
            # gene_disease = 2 -> Non-syndromic
            # gene_disease = 3 -> Both
        '''  
        if self.gene_disease is None:
            try:
                self.check()
            except:
                return False
        if int(self.gene_disease) == 0:
            return False
        else: 
            return True

    def get_expression(self, exp_id):
        '''
        Gets desired expression value for Gene
        '''
        self.expression = NEO.query_expression(self, exp_id)
        return self.expression

    def get_neighbours(self, level, dist, exp_id):
        '''
        Gets all the neighbours to Gene within 'level' interactions and at distance
        'dist' at most. All child nodes will have expression of 'exp_id'
        Returns a GraphCyt object.
        '''
        ngraph = NEO.query_get_neighbours(self, level, dist, exp_id)
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
        element['data']['level'] = self.level
        element['data']['exp'] = self.expression
        element['data']['gene_disease'] = self.gene_disease
        element['data']['nvariants'] = self.nvariants
        element['data']['inheritance_pattern'] = self.inheritance_pattern
        element['data']['gos'] = self.gos
        if self.is_driver():
            element['classes'] = "driver"
        return element


    def path_to_level(self, level):
        '''
        Returns a list of GraphCytoscape object with all shortest paths to all drivers
        '''
        paths = NEO.query_path_to_level(self, level)
        return paths


    def path_to_gene(self, cobj):
        '''
        Shortest path to Gene Object
        '''
        path = NEO.query_shortest_path(self, cobj)
        return path

    def __hash__(self):
        return hash((self.identifier, self.gene_disease, self.level))


class GraphCyt(object):
    '''
    Gene collection and interactions collection.
    Example for FORM1 (get all genes connected to list of genes in level and distance)
    mygraph = GraphCyt()
    mygraph.get_genes_by_level(identifiers, level, dist, exp_id)
    mygraph.to_json()
    '''
    def __init__(self):
        self.genes = set()
        self.interactions = set()
        self.json = ""

    def get_genes_in_level(self, identifiers, level=1, dist=1, exp_id="ABSOLUTE"):
        '''
        Adds to genes collection all the genes with the specified level
        and matching identifiers with their neighbours at dist=dist within
        the graph of level=level
        '''
        for identifier in identifiers:
            gene = Gene(identifier=identifier)
            try:
                gene.check()
                gene.get_expression(exp_id)
                self.genes.add(gene)
                self.merge(gene.get_neighbours(level, dist, exp_id))
            except Exception as err:
                print(err)
                print("Node %s not found" % identifier)
                continue

    def return_gene(self, identifier):
        '''
        Returns a Gene Object with a matching identifier
        '''
        gene_to_return = [ gene for gene in self.genes if gene.identifier == identifier ]
        return gene_to_return[0]

    def merge(self, graph):
        '''
        Merges self with GraphCyt object
        '''
        if graph.genes:
            self.genes = self.genes.union(graph.genes)
        if graph.interactions:
            self.interactions = self.interactions.union(graph.interactions)

    def to_json(self):
        """
        Converts the graph to a json string to add it to cytoscape.js
        """
        edges = list()
        for edge in self.interactions:
            edges.extend(edge.to_json_dict())
        graphelements = {
            'nodes': [ gene.to_json_dict() for gene in self.genes ],
            'edges': edges
        }
        self.json = json.dumps(graphelements)
        return self.json

    def add_gene(self, gene):
        """
        Adds Gene to the graph
        """
        self.genes.add(gene)

    def get_connections(self, level):
        """
        Method that looks for the edges between the nodes in the graph
        
        connections = NEO.get_connections_query(self.genes, level)
        self.interactions.add(connections)

        node_q_string = str(list([str(node.symbol) for node in self.nodes]))
        query = GET_CONNECTIONS_QUERY % (node_q_string, node_q_string)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            for row in results:
                parameters = dict()
                parameters = {
                    'int_prob'    : round(float(row['int_prob']), 3),
                    'path_length' : round(float(row['path_length']), 3),
                    'cellcom_nto' : round(float(row['cellcom_nto']), 3),
                    'molfun_nto'  : round(float(row['molfun_nto']), 3),
                    'bioproc_nto' : round(float(row['bioproc_nto']), 3),
                    'dom_int_sc'  : round(float(row['dom_int_sc']), 3)
                }
                newinteraction = PredInteraction(
                    database      = row['database'][0],
                    source_symbol = row['nsymbol'],
                    target        = PredictedNode(row['msymbol'], row['database'][0], query=False),
                    parameters    = parameters
                )
                self.add_interaction(newinteraction)
              """
    def __bool__(self):
        if self.genes:
            return True
        else:
            return False

    def __nonzero__(self):
        if self.genes:
            return True
        else:
            return False

NEO = NeoDriver('192.168.0.2', 8474, 8687, 'neo4j', 'p0tat0+')


class NodeNotFound(Exception):
    """Exception raised when a node is not found on the db"""
    def __init__(self, identifier, label):
        self.identifier   = identifier
        self.label = label
    def __str__(self):
        return "Identifier %s not found in label %s." % (self.identifier, self.label)
