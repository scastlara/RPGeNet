import re
import json
from node import *
from gene import *
from go import *
from interaction import *

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
                neighbours = gene.get_neighbours(level, dist, exp_id)
                for neighbour in neighbours.genes:
                    neighbour.get_expression(exp_id)
                self.merge(neighbours)
            except Exception as err:
                print(err)
                print("WHAAAT: %s" % NEO)
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
            genes = self.genes_to_list()
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

    def get_drivers(self):
        '''
        Adds driver genes to genes attribute
        '''
        self.genes = NEO.query_get_drivers().genes

    def genes_to_list(self):
        '''
        Returns list of gene objects ordered
        ''' 
        return sorted(self.genes, key=lambda x: self.order[x.identifier])

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

    def __str__(self):
        if self.order:
            nodes = sorted(self.genes, key=lambda x: self.order[x.identifier])
        else:
            nodes = list(self.genes)
        string = "NODES:\n\t%s" % "\n\t".join([ node.identifier for node in nodes ])
        string += "\nEDGES:\n\t%s" % "\n\t".join([ str((inter.parent.identifier, inter.child.identifier))  for inter in self.interactions ])
        return string