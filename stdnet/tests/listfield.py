from copy import copy
from itertools import izip

from stdnet.stdtest import TestBase
from stdnet.utils import populate
from stdnet import orm

elems = populate('string', 200)

class SimpleList(orm.StdModel):
    names = orm.ListField()

orm.register(SimpleList)

class TestLListField(TestBase):
    
    def testPushBackPopBack(self):
        li = SimpleList()
        names = li.names
        for elem in elems:
            names.push_back(elem)
        li.save()
        self.assertEqual(names.size(),len(elems))
        for elem in reversed(elems):
            self.assertEqual(names.pop_back(),elem)
        self.assertEqual(names.size(),0)
    
    def testPushFrontPopFront(self):
        li = SimpleList()
        names = li.names
        for elem in elems:
            names.push_front(elem)
        li.save()
        self.assertEqual(names.size(),len(elems))
        for elem in reversed(elems):
            self.assertEqual(names.pop_front(),elem)
        self.assertEqual(names.size(),0)
        
    def testIterator(self):
        li = SimpleList()
        names = li.names
        for elem in elems:
            names.push_back(elem)
        li.save()
        for el,ne in izip(elems,names):
            self.assertEqual(el,ne)

