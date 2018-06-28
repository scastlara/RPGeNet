from django.db import models
from py2neo import Graph, walk
import json
import re


class NeoQuery(object):
    '''
    Class for Neo4j queries
    '''
    def __init__(self, driver, cypher):
        self.driver = driver
        self.cypher = cypher
        self.results = None

    def execute(self):
        '''
        Executes query
        '''
        try:
            results = self.driver.run(self.cypher)
        except Exception as err:
            raise NotValidQuery(self.cypher)
        if results:
            self.results = results.data()
        else:
            self.results = None
        return self.results

    def get_results(self):
        '''
        Returns dictionary with results of cypher query
        '''
        if self.results is None:
            self.execute()

        return self.results


class NeoQueryFactory(object):
    '''
    Factory for Neo4j Queries
    '''
    def __init__(self, driver):
        self.driver = driver

    def _return_by_attributes(self, elem_name, attributes):
        '''
        Constructor of return clause based on a list of attributes for neo4j
        '''
        non_attributes = set([
            'label', 'parent', 
            'child', 'expression', 
            'gos', 'int_type', 
            'aliases',
            'summary', 'summary_source'])
        return_clause = ", ".join(['%s.%s as %s_%s' % (elem_name, attr, elem_name, attr) 
                                   for attr in attributes if attr not in non_attributes])
        return return_clause

    def build_query_by_id(self, nodeobj):
        '''
        Creates query for Matching Nodes by Identifier
        '''
        attributes = nodeobj.__dict__.keys()
        cypher = """
            MATCH (node:%s)
            WHERE node.identifier = '%s'
            RETURN 
        """ % (nodeobj.label, nodeobj.identifier)
        cypher = cypher + self._return_by_attributes('node', attributes)
        return NeoQuery(self.driver, cypher)

    def build_query_by_int(self, intobj):
        '''
        Creates query to retrieve the interaction using parent-child identifiers
        and fills the attributes of the interaction
        '''
        cypher = """
            MATCH (n:GENE)-[rel:INTERACTS_WITH]->(m:GENE)
            WHERE n.identifier = '%s'
            AND   m.identifier = '%s'
        """ % (intobj.parent.identifier, intobj.child.identifier)
        cypher += 'RETURN ' + self._return_by_attributes('rel', intobj.__dict__.keys())
        return NeoQuery(self.driver, cypher)

    def build_query_expression(self, nodeobj, exp_id):
        '''
        Gets expression value for nodeobj in a given experiment
        '''
        cypher = """
            MATCH  (node:%s)-[r:HAS_EXPRESSION]->(exp:EXPERIMENT)
            WHERE  node.identifier = '%s'
            AND    exp.identifier = '%s'
            RETURN r.value as expvalue
        """ % (nodeobj.label, nodeobj.identifier, nodeobj.identifier)
        return NeoQuery(self.driver, cypher)

    def build_query_get_connections(self, genelist, level):
        '''
        Gets connections for a list of Gene objects
        '''
        gene_q_string = str(list([str(gene.identifier) for gene in genelist]))
        cypher = """
            MATCH  (n:GENE)-[rel:INTERACTS_WITH]->(m:GENE)
            WHERE  n.identifier IN %s
            AND    m.identifier IN %s
            AND    rel.level <= %s
            RETURN n.identifier AS nidientifier,
                   m.identifier AS midentifier,
        """ % (gene_q_string, gene_q_string, level)
        e_attributes = Interaction().__dict__.keys()
        cypher += self._return_by_attributes('rel', e_attributes)
        return NeoQuery(self.driver, cypher)

    def build_query_gos(self, nodeobj):
        cypher = """
            MATCH  (node:%s)-[r:HAS_GO]->(go:GO)
            WHERE  node.identifier = '%s'
            RETURN go.accession as accession, 
                   go.description as description, 
                   go.domain as domain
            ORDER BY go.domain
        """ % (nodeobj.label, nodeobj.identifier)
        return NeoQuery(self.driver, cypher)

    def build_query_get_neighbours(self, nodeobj, level, dist, exp_id):
        '''
        Creates query to get neighbours to a particular node 
        in a level and at a distance
        '''
        cypher = """
            MATCH  p=(node1:GENE)-[rels:INTERACTS_WITH*1..%s]-(node2:GENE)
            WHERE  node1.identifier = '%s'
            AND    all(r IN rels WHERE r.level<=%s)
            RETURN p as pathway, extract(r IN relationships(p)| startnode(r).identifier) as thestart
        """ % (dist, nodeobj.identifier, level)
        return NeoQuery(self.driver, cypher)

    def build_query_path_to_level(self, nodeobj, level):
        '''
        Creates query for shortest path from node to a specific level
        '''
        cypher = """
            MATCH (gene:GENE)-[p:HAS_PATH]->(path:PATHWAY)
            WHERE gene.identifier = '%s'
            AND   path.to_level = %s
            WITH  gene, path
            MATCH (gene1:GENE)-[p1:IS_IN_PATH]->(path)
            MATCH (gene2:GENE)-[p2:IS_IN_PATH]->(path)
            MATCH (gene1)-[inter:INTERACTS_WITH]->(gene2)
            WHERE toInteger(p1.order) = toInteger(p2.order) - 1
            RETURN 
        """ % (nodeobj.identifier, level)
        n_attributes = nodeobj.__dict__.keys()
        e_attributes = Interaction().__dict__.keys()
        cypher += self._return_by_attributes('gene1', n_attributes)
        cypher += ", " + self._return_by_attributes('inter', e_attributes)
        cypher += ", " + self._return_by_attributes('gene2', n_attributes)
        cypher += ", " + "path.target AS target"
        cypher += " ORDER BY path.target, p1.order"
        return NeoQuery(self.driver, cypher)

    def build_query_shortest_path(self, pobj, cobj):
        '''
        Creates query for shortest path between pobj -> cobj
        '''
        cypher = """
            MATCH  p=allShortestPaths((s:GENE)-[r:INTERACTS_WITH*]->(t:GENE))
            WHERE  s.identifier = '%s'
            AND    t.identifier = '%s'
            RETURN p
        """ % (pobj.identifier, cobj.identifier)
        return NeoQuery(self.driver, cypher)

    def build_query_summary(self, nodeobj):
        '''
        Creates query to retrieve the summary of a gene
        '''
        cypher = """
            MATCH (n:GENE)
            WHERE n.identifier = '%s'
            RETURN n.summary AS summary, n.summary_source AS summary_source
        """ % (nodeobj.identifier)
        return NeoQuery(self.driver, cypher)

    def build_query_unalias(self, nodeobj):
        '''
        Creates query to disambiguate genes
        '''
        cypher = """
            MATCH (n:ALIAS)<-[r:HAS_ALIAS]-(m:GENE)
            WHERE n.identifier = '%s'
            RETURN m.identifier as identifier
        """ % nodeobj.identifier
        return NeoQuery(self.driver, cypher)

    def build_query_all_aliases(self, nodeobj):
        '''
        Creates query to retrieve all aliases to Gene
        '''
        cypher = """
            MATCH (n:GENE)-[r:HAS_ALIAS]->(m:ALIAS)
            WHERE n.identifier = '%s'
            RETURN m.identifier as alias
        """ % nodeobj.identifier
        return NeoQuery(self.driver, cypher)

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
        self.query_factory = NeoQueryFactory(self.dv)

    def return_by_attributes(self, elem_name, attributes):
        '''
        Constructor of return clause based on a list of attributes for neo4j
        '''
        non_attributes = set([
            'label', 'parent', 
            'child', 'expression', 
            'gos', 'int_type', 
            'aliases',
            'summary', 'summary_source'])
        return_clause = ", ".join(['%s.%s as %s_%s' % (elem_name, attr, elem_name, attr) 
                                   for attr in attributes if attr not in non_attributes])
        return return_clause

    def query_by_id(self, nodeobj):
        '''
        Gets ONE node object of class 
        '''
        query = self.query_factory.build_query_by_id(nodeobj)
        results = query.get_results()
        if results:
            results = results[0]
            nodeobj.fill_attributes(results, 'node')
        else:
            raise NodeNotFound(nodeobj.identifier, nodeobj.label)

    def query_by_int(self, intobj):
        '''
        Queries the interaction using parent-child identifiers
        and fills the attributes of the interaction
        '''
        query = self.query_factory.build_query_by_int(intobj)
        results = query.get_results()
        if results:
            interaction = results[0]
            intobj.fill_attributes(interaction, 'rel')
            for int_type in ['physical_interaction', 'genetic_interaction', 'unknown_interaction']:
                if interaction['rel_' + int_type]:
                    int_type = int_type.split('_')[0] # remove '_interaction'
                    intobj.int_type.add(int_type)
            intobj.int_type = sorted(intobj.int_type)
        else:
            raise InteractionNotFound(intobj.parent.identifier, intobj.child.identifier)

    def query_expression(self, nodeobj, exp_id):
        '''
        Gets expression value for nodeobj
        '''
        query = self.query_factory.build_query_expression(nodeobj, exp_id)
        results = query.get_results()
        #print("Expression %s" % results)
        if results:
            nodeobj.expression = results[0]['expvalue']
        else:
            nodeobj.expression = 'NA'

    def query_get_connections(self, genelist, level):
        '''
        Gets connections for a list of Gene objects
        '''
        connections_graph = GraphCyt()
        for gene in genelist:
            connections_graph.add_gene(Gene(identifier=gene.identifier))
        query = self.query_factory.build_query_get_connections(genelist, level)
        results = query.get_results()
        if results:
            for interaction in results:
                intobj = Interaction(
                    parent=Gene(identifier=interaction['nidientifier']),
                    child=Gene(identifier=interaction['midentifier']))
                intobj.fill_attributes(interaction, 'rel')
                connections_graph.add_interaction(intobj)
        return connections_graph

    def query_gos(self, nodeobj):
        '''
        Gets the GO of the nodeobj Gene
        '''
        go_list = list()
        query = self.query_factory.build_query_gos(nodeobj)
        results = query.get_results()
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
        query = self.query_factory.build_query_get_neighbours(nodeobj, level, dist, exp_id)
        results = query.get_results()
        if results:
            # Add genes first
            for row in results:
                nodes = row['pathway'].nodes()
                rels  = row['pathway'].relationships()
                for i in range(0, len(nodes) - 1):
                    gene1 = Gene(nodes[i]['identifier'])
                    gene1.fill_attributes(nodes[i], None)
                    gene2 = Gene(nodes[i+1]['identifier'])
                    gene2.fill_attributes(nodes[i+1], None)
                    neighbour_graph.add_gene(gene1)
                    neighbour_graph.add_gene(gene2)
                    if gene1.identifier == row['thestart'][-1]:
                        interaction_obj = Interaction(parent=gene1, child=gene2)
                    else:
                        interaction_obj = Interaction(parent=gene2, child=gene1)
                    interaction_obj.fill_attributes(rels[i], None)
                    neighbour_graph.add_interaction(interaction_obj)
            return neighbour_graph
        else:
            raise Exception

    def query_path_to_level(self, nodeobj, level):
        '''
        Shortest paths between 'node' and any node in level 'level'
        '''
        pathways = dict()
        gene_order = 0
        query = self.query_factory.build_query_path_to_level(nodeobj, level)
        results = query.get_results()
        if results:
            for interaction in results:
                if interaction['target'] not in pathways:
                    pathways[interaction['target']] = GraphCyt()
                    gene_order = 0

                if pathways[interaction['target']].return_gene(interaction['gene1_identifier']):
                    gene1 = pathways[interaction['target']].return_gene(interaction['gene1_identifier'])
                else:
                    gene1 = Gene(interaction['gene1_identifier'])
                    gene1.fill_attributes(interaction, 'gene1')
                    pathways[interaction['target']].add_gene(gene1)
                    pathways[interaction['target']].set_order(gene1, gene_order)
                    gene_order += 1
                if pathways[interaction['target']].return_gene(interaction['gene2_identifier']):
                    gene2 = pathways[interaction['target']].return_gene(interaction['gene2_identifier'])
                else:
                    gene2 = Gene(interaction['gene2_identifier'])
                    gene2.fill_attributes(interaction, 'gene2')
                    pathways[interaction['target']].add_gene(gene2)
                    pathways[interaction['target']].set_order(gene2, gene_order)
                    gene_order += 1

                # Adding interaction here
                interaction_obj = Interaction(parent=gene1, child=gene2)
                interaction_obj.fill_attributes(interaction, 'inter')
                pathways[interaction['target']].add_interaction(interaction_obj)
        return pathways

    def query_shortest_path(self, pobj, cobj):
        '''
        Returns list of GraphCytoscape with shortest path between pobj and cobj
        '''
        pathways = list()
        query = self.query_factory.build_query_shortest_path(pobj, cobj)
        results = query.get_results()
        if results:
            for path in results:
                pathway = GraphCyt()
                i = 0
                order = 0
                g1, g2 = None, None
                for elem in walk(path['p']):
                    if i % 2 != 0:
                        rel = elem
                    else:
                        if not g1:
                            # Gene 1
                            g1 = Gene(elem['identifier'])
                            g1.fill_attributes(elem, None)

                        else:
                            g2 = Gene(elem['identifier'])
                            g2.fill_attributes(elem, None)
                            if g1 and g2:
                                interaction_obj = Interaction(parent=g1, child=g2)
                                interaction_obj.fill_attributes(rel, None)
                                pathway.add_gene(g1)
                                pathway.add_gene(g2)
                                pathway.set_order(g1, order)
                                order += 1
                                pathway.set_order(g2, order)
                                order += 1
                                pathway.add_interaction(interaction_obj)
                                g1 = g2
                                g2 = None
                    i += 1
                pathways.append(pathway)
        return pathways

    def query_get_summary(self, nodeobj):
        '''
        Returns the summary for the gene
        '''
        query = self.query_factory.build_query_summary(nodeobj)
        results = query.get_results()
        if results:
            if results[0]['summary'] is not None:
                summary = results[0]['summary']
                src = results[0]['summary_source']
            else:
                summary = "Not available."
                src = None
        else:
            summary = "Not available."
            src = None
        return summary, src

    def query_unalias(self, nodeobj):
        '''
        Changes the identifier of the gene object to the official
        identifier in the database
        '''
        query = self.query_factory.build_query_unalias(nodeobj)
        results = query.get_results()
        if results:
            nodeobj.identifier = results[0]['identifier']
        else:
            # No alias, maybe an official identifier already
            # Don't have to do anything
            return

    def query_all_aliases(self, nodeobj):
        '''
        Returns list of alias identifiers
        '''
        aliases = set()
        query = self.query_factory.build_query_all_aliases(nodeobj)
        results = query.get_results()
        if results:
            for row in results:
                aliases.add(row['alias'])
        return aliases


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
        super(GO, self).__init__(accession, label)
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
        self.int_type = set()
        self.level = 0
        self.string = False
        self.biogrid = False
        self.ppaxe = False
        self.ppaxe_score = 0
        self.ppaxe_pubmedid = "NA"
        self.biogrid_pubmedid = "NA"
        self.string_evidence = "NA"
        self.string_pubmedid = "NA"
        self.genetic_interaction = 0
        self.physical_interaction = 0
        self.unknown_interaction = 0

    def check(self):
        '''
        Queries the interaction on the DB and fills all the attributes
        '''
        NEO.query_by_int(self)

    def fill_attributes(self, interaction_dict, prefix):
        '''
        Fills the attributes of the interaction to avoid querying db
        '''
        if prefix is None:
            self.level = interaction_dict['level']
            self.string = interaction_dict['string']
            self.biogrid = interaction_dict['biogrid']
            self.ppaxe = interaction_dict['ppaxe']
            self.ppaxe_score = interaction_dict['ppaxe_score']
            self.ppaxe_pubmedid = interaction_dict['ppaxe_pubmedid']
            self.biogrid_pubmedid = interaction_dict['biogrid_pubmedid']
            self.string_evidence  = interaction_dict['string_evidence']
            self.string_pubmedid  = interaction_dict['string_pubmedid']
            self.genetic_interaction = interaction_dict['genetic_interaction']
            self.physical_interaction = interaction_dict['physical_interaction']
            self.unknown_interaction = interaction_dict['unknown_interaction']
        else:
            self.level = interaction_dict[prefix + '_level']
            self.string = interaction_dict[prefix + '_string']
            self.biogrid = interaction_dict[prefix + '_biogrid']
            self.ppaxe = interaction_dict[prefix + '_ppaxe']
            self.ppaxe_score = interaction_dict[prefix + '_ppaxe_score']
            self.ppaxe_pubmedid = interaction_dict[prefix + '_ppaxe_pubmedid']
            self.biogrid_pubmedid = interaction_dict[prefix + '_biogrid_pubmedid']
            self.string_evidence  = interaction_dict[prefix + '_string_evidence']
            self.string_pubmedid  = interaction_dict[prefix + '_string_pubmedid']
            self.genetic_interaction = interaction_dict[prefix + '_genetic_interaction']
            self.physical_interaction = interaction_dict[prefix + '_physical_interaction']
            self.unknown_interaction = interaction_dict[prefix + '_unknown_interaction'] 
    
    def fix_string_evidences(self):
        '''
        Changes String Evidences to strings of hrefs
        '''
        new_evidences = list()
        if self.string_evidence:
            for evidence in sorted(self.string_evidence):
                print(evidence)

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
                element['data']['ewidth']  = int(types[type_idx])
                element['data']['level'] = self.level
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
        self.summary = None
        self.summary_source = None
        self.aliases = None

    def check(self):
        '''
        Queries Gene on neo4j and fills the attributes.
        If not in database: NodeNotFound
        '''
        self.normalize_identifier()
        self.unalias()
        NEO.query_by_id(self)

    def normalize_identifier(self):
        '''
        Removes strange characters from identifiers
        '''
        self.identifier = re.sub(r'\W+', '_', self.identifier)

    def unalias(self):
        '''
        Unalias
        '''
        NEO.query_unalias(self)

    def fill_attributes(self, genedict, prefix):
        '''
        Fills the attributes of the object. Avoids querying db
        '''
        if prefix is None:
            self.level = genedict['level']
            self.nvariants = genedict['nvariants']
            self.gene_disease = genedict['gene_disease']
            self.inheritance_pattern = genedict['inheritance_pattern']
        else:
            self.level = genedict[prefix + '_level']
            self.nvariants = genedict[prefix + '_nvariants']
            self.gene_disease = genedict[prefix + '_gene_disease']
            self.inheritance_pattern = genedict[prefix + '_inheritance_pattern']     

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

    def get_gene_disease_class(self):
        '''
        Returns gene-disease class string
        '''
        gd_class = None
        if self.gene_disease == 1:
            gd_class = "syndromic"
        elif self.gene_disease == 2:
            gd_class = "non-syndromic"
        elif self.gene_disease == 3:
            gd_class = "both"
        return gd_class

    def level_to_class(self):
        '''
        Returns level string for cytoscape class
        '''
        level_class = None
        if self.level == 0:
            level_class = "skeleton"
        else:
            level_class = "lvl" + str(self.level)
        return level_class

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

    def to_json_dict(self, positions=None):
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
        if self.is_driver():
            element['classes'] = "driver"
        else:
            element['classes'] = self.level_to_class()
        if self.get_gene_disease_class() is not None:
            element['classes'] += " " + self.get_gene_disease_class()
        if positions is not None:
            element['position'] = dict()
            element['position']['x'] = positions[0]
            element['position']['y'] = positions[1]
        return element

    def path_to_level(self, level):
        '''
        Returns a dictionary of GraphCytoscape object with all shortest paths to all drivers
        Key = target gene identifier
        '''
        paths = NEO.query_path_to_level(self, level)
        return paths

    def path_to_gene(self, cobj):
        '''
        Shortest path to Gene Object
        '''
        path = NEO.query_shortest_path(self, cobj)
        return path

    def get_summary(self):
        '''
        Returns summary for gene
        '''
        self.summary, self.summary_source = NEO.query_get_summary(self)
        return self.summary

    def get_aliases(self):
        '''
        Returns aliases for gene
        '''
        def alias_key(a):
            '''
            Sorts aliases based on our arbitrary needs:
                First Symbols, then ENS and finally Entrez.
                Within each group, sort by length of the symbol.
            '''
            order = { 'sym': (1, len(a)), 'ens': (2, len(a)), 'num': (3, len(a)) }
            key = 'sym'
            if re.match('^ENS[GTP]', a):
                key = 'ens'
            elif re.match('^\d+$', a):
                key = 'num'
            return order[key]

        self.aliases = sorted(NEO.query_all_aliases(self), key=alias_key)
        return self.aliases

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
        self.order = dict()
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
                print("Node %s not found" % identifier)
                continue

    def return_gene(self, identifier):
        '''
        Returns a Gene Object with a matching identifier
        '''
        if self.genes:
            gene_to_return = [ gene for gene in self.genes if gene.identifier == identifier ]
            if gene_to_return:
                gene_to_return = gene_to_return[0]
            else:
                gene_to_return = None
        else:
            gene_to_return = None
        return gene_to_return

    def merge(self, graph):
        '''
        Merges self with GraphCyt object
        '''
        if graph.genes:
            self.genes = self.genes.union(graph.genes)
        if graph.interactions:
            self.interactions = self.interactions.union(graph.interactions)

    def to_json(self, positions=None):
        """
        Converts the graph to a json string to add it to cytoscape.js
        """
        edges = list()
        for edge in self.interactions:
            edges.extend(edge.to_json_dict())
        if self.order:
            genes = sorted(self.genes, key=lambda x: self.order[x.identifier])
        else:
            genes = self.genes
        graphelements = {
            'nodes': [ gene.to_json_dict(positions) for gene in genes ],
            'edges': edges
        }
        self.json = json.dumps(graphelements)
        return self.json

    def add_gene(self, gene):
        """
        Adds Gene to the graph
        """
        self.genes.add(gene)

    def add_interaction(self, interaction):
        """
        Adds Gene to the graph
        """
        self.interactions.add(interaction)

    def get_connections(self, level):
        """
        Method that looks for the edges between the nodes in the graph
        """
        connections = NEO.query_get_connections(self.genes, level)
        return connections

    def set_order(self, gene, order):
        """
        Sets order of gene to order Useful for grid layout
        """
        self.order[gene.identifier] = order

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

# NEO4J CONNECTION
NEO = NeoDriver('192.168.0.2', 8474, 8687, 'neo4j', 'p0tat0+')

class NodeNotFound(Exception):
    """Exception raised when a node is not found on the db"""
    def __init__(self, identifier, label):
        self.identifier   = identifier
        self.label = label
    def __str__(self):
        return "Identifier %s not found in label %s." % (self.identifier, self.label)

class InteractionNotFound(Exception):
    """Exception raised when a node is not found on the db"""
    def __init__(self, parent, child):
        self.identifier   = parent + "-" + child
    def __str__(self):
        return "Interaction not found %s." % (self.identifier)


class NotValidQuery(Exception):
    def __init__(self, cypher):
        self.cypher   = cypher
    def __str__(self):
        return "Not valid query: %s." % (self.cypher)