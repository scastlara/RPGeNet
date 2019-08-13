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
        self.string  = False
        self.biogrid = False
        self.ppaxe   = False
        self.ppaxe_score = 0
        self.ppaxe_pubmedid   = "NA"
        self.biogrid_pubmedid = "NA"
        self.string_evidence  = "NA"
        self.string_pubmedid  = "NA"
        self.unknown_physical = "NA"
        self.unknown_genetic  = "NA"
        self.unknown_both     = "NA"
        self.genetic_interaction  = 0
        self.physical_interaction = 0
        self.unknown_interaction  = 0

    def check(self):
        '''
        Queries the interaction on the DB and fills all the attributes
        '''
        NEO.query_by_int(self)
        return self

    def fill_attributes(self, interaction_dict, prefix=None):
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
            self.unknown_physical = interaction_dict['unknown_physical']
            self.unknown_genetic  = interaction_dict['unknown_genetic']
            self.unknown_both     = interaction_dict['unknown_both']
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
            self.unknown_physical = interaction_dict[prefix + '_unknown_physical']
            self.unknown_genetic  = interaction_dict[prefix + '_unknown_genetic']
            self.unknown_both     = interaction_dict[prefix + '_unknown_both']
            self.genetic_interaction = interaction_dict[prefix + '_genetic_interaction']
            self.physical_interaction = interaction_dict[prefix + '_physical_interaction']
            self.unknown_interaction = interaction_dict[prefix + '_unknown_interaction'] 


    @staticmethod
    def decode_hex_evstring(hexstr):
        '''
        Converting hex string into chars [for ppaxe_pubmedid]:
          import binascii
          str(binascii.hexlify(b"HI HOW ARE YOU!"),"ascii")
          >> '484920484f572041524520594f5521'
          # binascii is not required to decode...
          str='blabla~484920484f572041524520594f5521'
          (kkstr,hxstr)=str.split('~')
          ''.join(chr(int(hxstr[i:i+2],16)) for i in range(0,len(hxstr),2))
          >> 'HI HOW ARE YOU!'
        '''
        newstring = ''.join(chr(int(hexstr[i:i+2],16)) for i in range(0,len(hexstr),2))
        newstring = re.sub(r'^<z>','<span class="ppaxe">',newstring)
        newstring = re.sub(r'<\/z>$','</span>',newstring)
        return newstring

    # @staticmethod
    def split_by_tilde(self):
        '''
        Returning an array of arrays if strings contain the tilde char to separate fields.
        '''
        aryofstr = [ 'biogrid_pubmedid', 'ppaxe_pubmedid', 'string_pubmedid',
                     'string_evidence', 'unknown_physical', 'unknown_genetic', 'unknown_both', ]
        for myattribute in aryofstr:
            aryofary = list()
            for mystring in getattr(self, myattribute):
                if mystring == "NA" or not mystring:
                    continue
                subary = mystring.split('~')
                # print(subary)
                if myattribute == 'ppaxe_pubmedid':
                    subary[1] = float(subary[1].replace("_","."))
                    subary[2] = self.decode_hex_evstring(subary[2])
                    # print(subary)
                aryofary.append(subary)
            aryofary = sorted(aryofary, key=lambda x: x[0])
            setattr(self, myattribute, aryofary)
        
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
