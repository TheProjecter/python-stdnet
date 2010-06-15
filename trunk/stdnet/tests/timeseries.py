from itertools import izip
from datetime import date
import unittest

from stdnet import orm
from stdnet import settings_test
from stdnet.utils import populate, date2timestamp


class Ticker(orm.StdModel):
    code    = orm.AtomField(unique = True)
    
class Field(orm.StdModel):
    code    = orm.AtomField(unique = True)

class TimeSerie(orm.StdModel):
    '''A timeserie model'''
    ticker  = orm.ForeignKey(Ticker)
    field   = orm.ForeignKey(Field)
    data    = orm.StdMap()
    
    def add(self, dte, v):
        self.data.add(date2timestamp(dte),v)
        

orm.register(Ticker,settings_test.redis)
orm.register(Field,settings_test.redis)
orm.register(TimeSerie,settings_test.redis)
#orm.register(Ticker)
#orm.register(Field)
#orm.register(TimeSerie)


class TestTimeSerie(unittest.TestCase):
    
    def setUp(self):
        self.ticker = Ticker(code = 'GOOG')
        self.ticker.save()
        self.field = Field(code = 'CLOSE')
        self.field.save()

    def testAdd(self):
        t = TimeSerie(ticker = self.ticker, field = self.field)
        dates  = populate('date',100)
        values = populate('float',100, start = 10, end = 400)
        for d,v in izip(dates,values):
            t.add(d,v)
        t.save()
        obj = TimeSerie.objects.getid(id = t.id)
        data = obj.data.all()
        data = list(data)
        self.assertTrue(len(data)>0)
        d = None
        for dt,value in data:
            if d:
                self.assertTrue(dt>d)
            d = dt
    
    def tearDown(self):
        self.ticker.delete()
        self.field.delete()
