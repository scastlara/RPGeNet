from py2neo import Graph, walk
from exceptions import *

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

    def build_query_experiment(self, experiment):
        '''
        Creates query to retrieve experiment with min/max values
        '''
        cypher = """
            MATCH (n:EXPERIMENT)
            WHERE n.identifier = '%s'
            RETURN n.max, n.min
        """ % experiment.identifier
        return NeoQuery(self.driver, cypher)


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

    def __str__(self):
        return self.cypher


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
            expression = results[0]['expvalue']
        else:
            print("NOEXPRESSIOOOOON")
            expression = 'NA'
        return expression

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

    def query_experiment(self, experiment):
        '''
        Checks Experiment in DB and returns the Experiment max and min values.
        '''
        query = self.query_factory.build_query_experiment(experiment)
        print(query)
        results = query.get_results()
        if results:
            pass
        else:
            raise ExperimentNotFound(experiment)


# NEO4J CONNECTION
NEO = NeoDriver('192.168.0.2', 8474, 8687, 'neo4j', 'p0tat0+')


# Do this to avoid import errors
# see: 
# https://stackoverflow.com/questions/11698530/two-python-modules-require-each-others-contents-can-that-work
from graphcyt import *