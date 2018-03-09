from django.db import models

# Create your models here.

class Node(object):
	'''
	General class for nodes in neo4j
	'''
	def __init__(self, identifier, label):
		self.identifier = identifier
		self.label = label

	def exists(self):
		pass

	def get_neighbours(self, edge_label):
		pass

	
