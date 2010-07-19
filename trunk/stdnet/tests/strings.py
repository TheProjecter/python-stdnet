import time
import unittest
import random
from itertools import izip

from stdnet.main import getdb
from stdnet.stdtest import TestBase
from stdnet import orm

cache = orm.getdb()


class TestString(TestBase):
    
    def testSetGet(self):
        cache.set('test',1)
        self.assertEqual(cache.get('test'),1)
        cache.set('test2','ciao',1)
        self.assertEqual(cache.get('test2'),'ciao')
        time.sleep(2)
        self.assertEqual(cache.get('test2'),None)