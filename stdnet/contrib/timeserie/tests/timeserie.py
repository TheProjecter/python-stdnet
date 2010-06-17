from itertools import izip
from datetime import date
from random import uniform

from stdnet.stdtest import TestBase
from stdnet import orm
from stdnet.contrib.timeserie import models
from stdnet.contrib.timeserie.utils import dategenerator, default_parse_interval
from stdnet.utils import populate

class Ticker(orm.StdModel):
    code    = orm.AtomField(unique = True)
    
class Field(orm.StdModel):
    code    = orm.AtomField(unique = True)

class TimeSerie(models.TimeSerie):
    '''A timeserie model'''
    ticker  = orm.ForeignKey(Ticker)
    field   = orm.ForeignKey(Field)
        

orm.register(Ticker)
orm.register(Field)
orm.register(TimeSerie)


class TestTimeSerie(TestBase):
    
    def setUp(self):
        self.ticker = Ticker(code = 'GOOG')
        self.ticker.save()
        self.field = Field(code = 'CLOSE')
        self.field.save()
        self.ts = TimeSerie(ticker = self.ticker, field = self.field).save()

    def fill(self, a, b, targets, C, D):
        ts = self.ts
        intervals = ts.intervals(a,b)
        self.assertEqual(len(intervals),len(targets))
        for interval,target in izip(intervals,targets):
            x = interval[0]
            y = interval[1]
            self.assertEqual(x,target[0])
            self.assertEqual(y,target[1])
            for dt in dategenerator(x,y):
                ts.data.add(dt,uniform(0,1))
        ts.storestartend()
        self.assertEqual(ts.start,C)
        self.assertEqual(ts.end,D)
        
    def testInterval(self):
        '''Test interval handling'''
        ts = self.ts
        self.assertEqual(ts.start,None)
        self.assertEqual(ts.end,None)
        obj = TimeSerie.objects.get(id = 1)
        self.assertEqual(obj.start,None)
        self.assertEqual(obj.end,None)
        #
        #
        A1   = date(2010,5,10)
        B1   = date(2010,5,12)
        self.fill(A1,B1,[[A1,B1]],A1,B1)
        #
        #  original ->      A1      B1
        #  request  -> A2      B2
        #  interval -> A2  A1-
        #  range    -> A2          B1
        A2   = date(2010,5,6)
        B2   = date(2010,5,11)
        self.fill(A2,B2,[[A2,default_parse_interval(A1,-1)]],A2,B1)
        #
        #  original ->      A2      B1
        #  request  -> A3                B3
        #  interval -> A3  A2-       B1+ B3
        #  range    -> A3                B3
        A3   = date(2010,5,4)
        B3   = date(2010,5,14)
        self.fill(A3,B3,[[A3,default_parse_interval(A2,-1)],
                         [default_parse_interval(B1,1),B3]],A3,B3)
        #
        # original -> A3                B3
        # request  ->      A2     B2
        # interval -> empty
        # range    -> A3                B3
        self.fill(A2,B2,[],A3,B3)
        #
        # original ->          A3                B3
        # request  -> A4  B4
        # interval -> A4      A3-
        # range    -> A4                         B3
        A4   = date(2010,4,20)
        B4   = date(2010,5,1)
        self.fill(A4,B4,[[A4,default_parse_interval(A3,-1)]],A4,B3)
        #
        # original -> A4                         B3
        # request  ->                A2                  B5
        # interval ->                             B3+    B5
        # range    -> A4                                 B5
        B5   = date(2010,6,1)
        self.fill(A2,B5,[[default_parse_interval(B3,1),B5]],A4,B5)
        #
        # original -> A4                                 B5
        # request  ->                                        A6    B6
        # interval ->                                     B5+      B6
        # range    -> A4                                           B6
        A6   = date(2010,7,1)
        B6   = date(2010,8,1)
        self.fill(A6,B6,[[default_parse_interval(B5,1),B6]],A4,B6)
        
        
        
    def testAdd(self):
        ts = self.ts
        dates  = populate('date',100)
        values = populate('float',100, start = 10, end = 400)
        for d,v in izip(dates,values):
            ts.data.add(d,v)
        ts.save()
        obj = TimeSerie.objects.get(id = ts.id)
        data = obj.data.items()
        data = list(data)
        self.assertTrue(len(data)>0)
        d = None
        for dt,value in data:
            if d:
                self.assertTrue(dt>d)
            d = dt
    