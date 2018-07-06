from node import *

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