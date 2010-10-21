import datetime
import unittest
import logging
from itertools import izip

from stdnet.test import TestCase
from stdnet import orm
from stdnet.utils import populate


class TestDateModel(orm.StdModel):
    dt = orm.DateField()
    
orm.register(TestDateModel)

NUM_DATES = 1000
dates = populate('date', NUM_DATES, start=datetime.date(2010,5,1), end=datetime.date(2010,6,1))



class TestDateField(TestCase):
    
    def setUp(self):
        for dt in dates:
            TestDateModel(dt = dt).save(False)
        TestDateModel.commit()
            
    def testFilter(self):
        all = TestDateModel.objects.all()
        self.assertEqual(len(dates),all.count())
        N = 0
        done_dates = set()
        for dt in dates:
            if dt not in done_dates:
                done_dates.add(dt)
                elems = TestDateModel.objects.filter(dt = dt)
                N += elems.count()
                for elem in elems:
                    self.assertEqual(elem.dt,dt)
        self.assertEqual(all.count(),N)
        
    def testDelete(self):
        N = 0
        done_dates = set()
        for dt in dates:
            if dt not in done_dates:
                done_dates.add(dt)
                objs = TestDateModel.objects.filter(dt = dt)
                N += objs.count()
                objs.delete()
        all = TestDateModel.objects.all()
        self.assertEqual(all.count(),0)
        
            