from node import *
from neomodels import *
import matplotlib.pyplot as plt

class Experiment(Node):
	'''
	Class for Gene Expression experiment
	'''
	def __init__(self, identifier):
		self.identifier = identifier.upper()
		self.max = 0 # will be overwritten by check()
		self.min = 0 # will be overwritten by check()
		self.cmap_type = None

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
		else:
			# Diverging
			cmap_name = "RdBu"
		return plt.get_cmap(cmap_name)

	def _normalize_value(self, x):
		'''
		Transforms expression value from 0 to 1 using min-max normalization
		'''
		x = float(x)
		return (x - self.min) / (self.max - self.min)

	def check(self):
		'''
		Checks if experiment is in database
		Adds interval values to experiment
		'''
		NEO.query_experiment(self)
		self.cmap = self._get_cmap()

	def color_from_value(self, value):
		'''
		Returns a color for a particular expression value
		'''
		expcolor = "Black"
		if value != "NA":
			normval = self._normalize_value(value)
			expcolor = self.cmap(normval)
			expcolor = matplotlib.colors.rgb2hex(expcolor)
		return expcolor

	def assign_color_to_gene(self, gene):
		'''
		Changes the expression of a Gene object
		'''
		gene.expression = self.color_from_value(gene.expression)
		return self

	def __str__(self):
		return "Experiment %s of type %s\n\tmin: %s\n\tmax:%s\n" % (self.identifier, self.cmap_type, self.min, self.max)