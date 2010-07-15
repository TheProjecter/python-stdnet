import datetime
import unittest
import random
from itertools import izip

from stdnet.stdtest import TestBase
from stdnet import orm

# Create the model for testing.
class Node(orm.StdModel):
    parent = orm.ForeignKey('self', required = False, related_name = 'children')
    def __init__(self, weight = 1.0, **kwargs):
        super(Node,self).__init__(**kwargs)
        self.weight = weight
    
    def __str__(self):
        return '%s' % self.weight
    
orm.register(Node)

STEPS   = 10

class TestSelfForeignKey(TestBase):
    
    def create(self, N, root):
        for n in range(N):
            node = Node(parent = root, weight = random.uniform(0,1)).save()
            
    def setUp(self):
        root = Node(weight = 1.0).save()
        for n in range(STEPS):
            node = Node(parent = root, weight = random.uniform(0,1)).save()
            self.create(random.randint(0,9), node)
    
    def testSelfRelated(self):
        root = Node.objects.filter(parent = None)
        self.assertEqual(len(root),1)
        root = root[0]
        children = list(root.children.all())
        self.assertEqual(len(children),STEPS)
        for child in children:
            self.assertEqual(child.parent,root)
            
        