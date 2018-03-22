"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from rpform.models import *

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class GeneTest(TestCase):
	def test_init(self):
		'''
		Tests init of Gene
		'''
		gene = Gene("Identifier")
		assert(gene.identifier == "Identifier")

	def test_to_json_dict(self):
		'''
		Tests to json dictionary
		'''
		gene = Gene("Identifier")
		required = set(["id", "name", "lvl", "exp", "driver_confidence", "nvariants", "gos"])
		assert(set(gene.to_json_dict()['data'].keys()) == required)

	def test_check_fail(self):
		'''
		Tests if non-existing node returns NodeNotFound
		'''
		gene = Gene("Identifier")
		try:
			gene.check()
			self.fail("NodeNotFound not raised")
		except NodeNotFound:
			pass


class NeoDriverTest(TestCase):
	def test_init(self):
		'''
		Tests connection no NEO4j
		'''
		try:
			NEO = NeoDriver('127.0.0.1', '7474', 'neo4j', '5961')
		except Exception:
			self.fail("Can't connect to Neo4j db")

	def test_return_by_attributes(self):
		'''
		Tests return constructor method
		'''
		NEO = NeoDriver('127.0.0.1', '7474', 'neo4j', '5961')
		qstr = NEO.return_by_attributes("node1", ['id', 'parent', 'child', 'attribute1', 'attribute2'])
		estr = "node1.id as node1_id,node1.attribute1 as node1_attribute1,node1.attribute2 as node1_attribute2"
		assert(qstr == estr)

	



