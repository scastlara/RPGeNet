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
        self.int_best = 'none'
        self.level    = 0
        self.strength = 0
        self.string   = False
        self.biogrid  = False
        self.ppaxe    = False
        self.ppaxe_score   = 0
        self.string_score  = 0
        self.string_scores = "NA"
        self.ppaxe_evidences   = "NA"
        self.biogrid_evidences = "NA"
        self.string_evidences  = "NA"
        self.string_actions    = "NA"
        self.genetic_interaction  = 0
        self.physical_interaction = 0
        self.unknown_interaction  = 0
        self.string_action        = 0
        # self.unknown_physical  = "NA"
        # self.unknown_genetic   = "NA"
        # self.unknown_both      = "NA"

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
            self.level    = interaction_dict['level']
            self.strength = interaction_dict['strength']
            self.string   = interaction_dict['string']
            self.biogrid  = interaction_dict['biogrid']
            self.ppaxe    = interaction_dict['ppaxe']
            self.ppaxe_score   = interaction_dict['ppaxe_score']
            self.string_score  = interaction_dict['string_score']
            self.string_scores = interaction_dict['string_scores']
            self.ppaxe_evidences   = interaction_dict['ppaxe_evidences']
            self.biogrid_evidences = interaction_dict['biogrid_evidences']
            self.string_evidences  = interaction_dict['string_evidences']
            self.string_actions    = interaction_dict['string_actions']
            self.genetic_interaction  = interaction_dict['genetic_interaction']
            self.physical_interaction = interaction_dict['physical_interaction']
            self.unknown_interaction  = interaction_dict['unknown_interaction']
            self.string_action        = interaction_dict['string_action']
            # self.unknown_physical = interaction_dict['unknown_physical']
            # self.unknown_genetic  = interaction_dict['unknown_genetic']
            # self.unknown_both     = interaction_dict['unknown_both']
        else:
            self.level    = interaction_dict[prefix + '_level']
            self.strength = interaction_dict[prefix + '_strength']
            self.string   = interaction_dict[prefix + '_string']
            self.biogrid  = interaction_dict[prefix + '_biogrid']
            self.ppaxe    = interaction_dict[prefix + '_ppaxe']
            self.ppaxe_score   = interaction_dict[prefix + '_ppaxe_score']
            self.string_score  = interaction_dict[prefix + '_string_score']
            self.string_scores = interaction_dict[prefix + '_string_scores']
            self.ppaxe_evidences   = interaction_dict[prefix + '_ppaxe_evidences']
            self.biogrid_evidences = interaction_dict[prefix + '_biogrid_evidences']
            self.string_evidences  = interaction_dict[prefix + '_string_evidences']
            self.string_actions    = interaction_dict[prefix + '_string_actions']
            self.genetic_interaction  = interaction_dict[prefix + '_genetic_interaction']
            self.physical_interaction = interaction_dict[prefix + '_physical_interaction']
            self.unknown_interaction  = interaction_dict[prefix + '_unknown_interaction']
            self.string_action        = interaction_dict[prefix + '_string_action']
            # self.unknown_physical = interaction_dict[prefix + '_unknown_physical']
            # self.unknown_genetic  = interaction_dict[prefix + '_unknown_genetic']
            # self.unknown_both     = interaction_dict[prefix + '_unknown_both']
        sum = self.genetic_interaction + self.physical_interaction + self.unknown_interaction
        if sum == 0:
            self.int_best = 'none'
        elif self.physical_interaction > self.genetic_interaction and self.physical_interaction > self.unknown_interaction:
            self.int_best = 'physical'
        elif self.genetic_interaction > self.physical_interaction and self.genetic_interaction > self.unknown_interaction:
            self.int_best = 'genetic'
        elif self.unknown_interaction > self.physical_interaction and self.unknown_interaction > self.genetic_interaction:
            self.int_best = 'unknown'
        else:
            self.int_best = 'mixed'

    @staticmethod
    def decode_hex_evstring(hexstr):
        '''
        Converting hex string into chars [for ppaxe_evidences]:
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

    @staticmethod
    def make_fixed_urls(evids):
        '''
        Check a scalar/array of evidences to convert into html anchors
        '''
        thyurls = {
            'PMID':       '<a href="https://www.ncbi.nlm.nih.gov/pubmed/%s" title="PubMed ID" target="_blank">%s</a>',
            'GO':         '<a href="http://amigo.geneontology.org/amigo/medial_search?q=GO%%3A%s&searchtype=all" title="Gene Ontology ID" target="_blank">GO:%s</a>',
            'PDB':        '<a href="https://www.rcsb.org/structure/%s" title="PDB ID" target="_blank">%s</a>',
            'INTACT':     '<a href="https://www.ebi.ac.uk/intact/interaction/%s" title="INTACT ID" target="_blank">%s</a>',
            #'IMEX':       '<a href="https://www.ebi.ac.uk/intact/cv/%s" title="IMEX ID" target="_blank">%s</a>',
            'IMEX':      '<a href="https://www.ebi.ac.uk/intact/imex/main.xhtml?query=%s#" title="IMEX ID" target="_blank">%s</a>',
            'KEGG':       '<a href="https://www.kegg.jp/kegg-bin/show_pathway?%s" title="KEGG ID" target="_blank">%s</a>',
            #
            # those below do not have a proper search URL to build a query link
            'RCTM':       '<a href="https://reactome.org/" title="REACTOME ID" alt="%s" target="_blank">%s</a>',
            'PROTEOMEHD': '<a href="https://www.proteomehd.net/" title="ProteomeHD ID" alt="%s" target="_blank">ProtHD%s</a>',
            'BCRT':       '<a href="https://cgap.nci.nih.gov/Pathways/BioCarta_Pathways" title="BioCarta ID" alt="%s" target="_blank">%s</a>',
            'DIP':        '<a href="https://dip.doe-mbi.ucla.edu/dip/Main.cgi" title="Database of Interacting Proteins ID" alt="%s" target="_blank">%s</a>',
            'EFO':        '<a href="https://www.ebi.ac.uk/efo/" title="Experimental Factor Ontology ID" alt="%s" target="_blank">EFO:%s</a>',
        }
        evidsarg = list()
        if type(evids) in (list, ):
            evidsarg = evids
        else:
            evidsarg.append(evids)
        aryofevs = list()
        for thyevid in evidsarg:
            if re.search(r'^DIP-', thyevid):
                thyevid = ("DIP:%s" % thyevid) # a patch for some DIP IDs
            if re.search(r'^efo:', thyevid):
                thyevid = re.sub(r'^efo:', '', thyevid)
                thyevid = re.sub(r'\'', '', thyevid) # a patch for some EFO IDs
            refchunks = thyevid.split(':')
            # print("E: %s  I: %s  T: %s" % \
            #      (thyevid, refchunks[0], (refchunks[1] if len(refchunks) > 1 else "NA")))
            if refchunks[0] in thyurls:
                # print(thyurls.get(refchunks[0]) % (refchunks[1], refchunks[1]))
                aryofevs.append(thyurls.get(refchunks[0]) % (refchunks[1], refchunks[1]))
            else:
                aryofevs.append(thyevid)
            # print("\n")
        return ', '.join(aryofevs)

    def check_string_scores(self):
        aryofary = list()
        if self.string_scores != "NA":
            for myscore in self.string_scores:
                thyscore = ("%.3f" % (float(myscore) / float(1000))) if myscore >= 0 else "N.A.";
                aryofary.append(thyscore)
            self.string_scores = aryofary
        
    # @staticmethod
    def split_by_tilde(self):
        '''
        Returning an array of arrays if strings contain the tilde char to separate fields.
        '''
        aryofstr = [ 'biogrid_evidences', 'ppaxe_evidences',
                     'string_evidences',  'string_actions'   ]
        #            'unknown_physical', 'unknown_genetic', 'unknown_both' ]
        for myattribute in aryofstr:
            aryofary = list()
            for mystring in getattr(self, myattribute):
                if mystring == "NA" or not mystring:
                    continue
                subary = mystring.split('~')
                myfilterfld = 0
                # print(subary)
                subary[0] = subary[0].split('+')
                if subary[1] != "NA" and subary[1] != "-":
                    subary[1] = ("%.3f" % (float(subary[1]) / float(1000))) if subary[1] >= 0 else "N.A."
                if myattribute == 'biogrid_evidences':
                    subary[2] = re.sub(r'_',' ',subary[2])
                if myattribute == 'string_evidences':
                    myfilterfld = 2
                #     if subary[1] != "NA":
                #         subary[1] = ("%.3f" % (float(subary[1]) / float(1000))) if subary[1] >= 0 else "N.A."
                #         # aryofevs = subary[0].split('+')
                #         # subary[0] = aryofevs
                if myattribute == 'ppaxe_evidences':
                    # if subary[1] != "NA":
                    #     subary[1] = ("%.3f" % (float(subary[1]) / float(1000))) if subary[1] >= 0 else "N.A."
                    subary[2] = self.decode_hex_evstring(subary[2])
                    # subary[1] = float(subary[1].replace("_",".")) # ppaxe_score fixed
                    # print(subary)
                subary.append(subary[myfilterfld])
                ids = sorted(subary[0], key=lambda x: x[0])
                subary[0] = self.make_fixed_urls(ids)
                aryofary.append(subary)
            aryofary = sorted(aryofary, key=lambda x: x[-1])
            setattr(self, myattribute, aryofary)
        
    def fix_string_evidences(self):
        '''
        Changes String Evidences to strings of hrefs
        '''
        new_evidences = list()
        if self.string_evidences:
            for evidence in sorted(self.string_evidences):
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
