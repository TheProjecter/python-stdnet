from itertools import izip
from datetime import date
import unittest

from stdnet import orm
from stdnet import settings_test
from stdnet.utils import populate


class Ticker(orm.StdModel):
    code    = orm.AtomField(unique = True)
    
class Field(orm.StdModel):
    code    = orm.AtomField(unique = True)

class TimeSerie(orm.StdModel):
    '''A timeserie model'''
    ticker  = orm.ForeignKey(Ticker)
    field   = orm.ForeignKey(Field)
    data    = orm.StdMap()
    
        

orm.register(Ticker,settings_test.redis)
orm.register(Field,settings_test.redis)
orm.register(TimeSerie,settings_test.redis)


class TestTimeSerie(unittest.TestCase):
    
    def setUp(self):
        self.ticker = Ticker(code = 'GOOG')
        self.ticker.save()
        self.field = Field(code = 'CLOSE')
        self.field.save()

    def testAdd(self):
        t = TimeSerie(ticker = self.ticker, field = self.field)
        t.save()
        dates  = populate('date',100)
        values = populate('float',100, start = 10, end = 400)
        for d,v in izip(dates,values):
            t.data.add(d,v)
        self.assertAlmostEqual
