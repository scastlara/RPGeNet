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

class ExperimentNotFound(Exception):
    def __init__(self, experiment):
        self.experiment   = experiment.identifier
    def __str__(self):
        return "Not valid Experiment: %s." % (self.experiment)    