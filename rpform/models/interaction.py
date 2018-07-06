from neomodels import *

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