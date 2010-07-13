import datetime
import unittest
import logging
from itertools import izip

from stdnet.stdtest import TestBase
from stdnet import orm
from stdnet.utils import populate


class TestDateModel(orm.StdModel):
    dt = orm.DateField()
    
orm.register(TestDateModel)

NUM_DATES = 1000
dates = populate('date', NUM_DATES, start=datetime.date(2010,5,1), end=datetime.date(2010,6,1))



class TestdateField(TestBase):
    
    def setUp(self):
        for dt in dates:
            TestDateModel(dt = dt).save(False)
        TestDateModel.commit()
            
    def testFilter(self):
        all = TestDateModel.objects.all()
        self.assertEqual(len(dates),all.count())
        N = 0
        for dt in dates:
            elems = TestDateModel.objects.filter(dt = dt)
            N += elems.count()
        self.assertEqual(all.count(),N)
        
            