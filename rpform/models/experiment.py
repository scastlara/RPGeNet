from node import *
from neomodels import *
from matplotlib import pyplot, colors

class Experiment(Node):
	'''
	Class for Gene Expression experiment
	'''
	def __init__(self, identifier):
		self.identifier = identifier.upper()
		self.max = 0 # will be overwritten by check()
		self.min = 0 # will be overwritten by check()
		self.cmap_type = None
		# Expressions will be colored
		# according to this scale:
		self.wmax = None
		self.wmin = None

	@classmethod
	def all_from_database(cls):
		'''
		Returns list of all Experiment objects available in neo4j
		'''
		return NEO.query_get_all_experiments(cls)

	def _get_cmap(self):
		'''
		Assigns a colormap depending on the type
		'''
		cmap_name = None
		if self.cmap_type == 0:
			# Sequential
			cmap_name = "Blues"
			self.wmax = self.max
			self.wmin = self.min
		else:
			# Diverging
			cmap_name = "RdYlBu"
			self.wmax = 5
			self.wmin = -5
		return pyplot.get_cmap(cmap_name)

	def _normalize_value(self, x):
		'''
		Transforms expression value from 0 to 1 using min-max normalization
		'''
		x = float(x)
		normval = float()
		if x >= self.wmax:
			normval = float(1)
		elif x <= self.wmin:
			normval = float(0)
		else:
			normval = (x - self.wmin) / (self.wmax - self.wmin)
		if self.cmap_type == 1:
			# If relative, invert colors
			normval = 1 - normval
		return normval

	def check(self):
		'''
		Checks if experiment is in database
		Adds interval values to experiment
		'''
		NEO.query_experiment(self)
		self.cmap = self._get_cmap()
		return self

	def color_from_value(self, value):
		'''
		Returns a color for a particular expression value
		'''
		expcolor = "#000000"
		if value != "NA":
			normval  = self._normalize_value(value)
			expcolor = self.cmap(normval)
			expcolor = colors.rgb2hex(expcolor)
		return expcolor

	def assign_color_to_gene(self, gene):
		'''
		Changes the expression of a Gene object
		'''
		gene.expression = self.color_from_value(gene.expression)
		return self

	def get_gene_expression(self, gene):
		'''
		Retrieves expression data for gene
		'''
		return NEO.query_expression(gene, self.identifier)


	def __str__(self):
		return "Experiment %s of type %s\n\tmin: %s\n\tmax:%s\n" % (self.identifier, self.cmap_type, self.min, self.max)