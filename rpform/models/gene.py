from node import *
from neomodels import *
import re

class Gene(Node):
    '''
    Class for gene nodes on neo4j
    identifier: STRING
    level: [ -1 | 0 | 1 | 2 | 3 | 4 | 5 ]
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
        self.color = None

    def check(self):
        '''
        Queries Gene on neo4j and fills the attributes.
        If not in database: NodeNotFound
        '''
        self.normalize_identifier()
        self.unalias()
        NEO.query_by_id(self)
        return self

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

    def fill_attributes(self, genedict, prefix=None):
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
        element['data']['color'] = self.color
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
