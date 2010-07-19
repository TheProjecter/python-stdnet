import datetime
import unittest
import random
from itertools import izip

from stdnet.stdtest import TestBase
from stdnet import orm


class SimpleModel(orm.StdModel):
    code = orm.AtomField(unique = True)

orm.register(SimpleModel)
    

class TestManager(TestBase):
    
    def testGetOrCreate(self):
        v,created = SimpleModel.objects.get_or_create(code = 'test')
        self.assertTrue(created)
        self.assertEqual(v.code,'test')
        v2,created = SimpleModel.objects.get_or_create(code = 'test')
        self.assertFalse(created)
        self.assertEqual(v,v2)