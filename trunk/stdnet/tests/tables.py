import datetime
import unittest
from itertools import izip

from stdnet.stdtest import TestBase
from stdnet import orm
from stdnet.utils import populate

# Create some models for testing

class Base(orm.StdModel):
    name = orm.AtomField(unique = True)
    type = orm.AtomField()
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        abstract = True

class Instrument(Base):
    pass
    
class Fund(Base):
    ccy  = orm.AtomField()

class Position(orm.StdModel):
    instrument = orm.ForeignKey(Instrument)
    fund       = orm.ForeignKey(Fund)
    dt         = orm.DateField()
    
    def __init__(self, size = 1, price = 1, **kwargs):
        self.size  = size
        self.price = price
        super(Position,self).__init__(**kwargs)
    

orm.register(Instrument)
orm.register(Fund)
orm.register(Position)

TYPELEN = 10
LEN     = 100
choice_from = ['EUR','GBP','USD','JPY']
names = populate('string',LEN, min_len = 5, max_len = 20)
types = populate('integer',LEN, start=0, end=TYPELEN-1)
ccys  = populate('choice',LEN, choice_from = choice_from)

class TestORM(TestBase):
    
    def setUp(self):
        for name,typ,ccy in izip(names,types,ccys):
            Instrument(name = name, type = typ).save()
            Fund(name = name, type = typ, ccy = ccy).save()
        
    def testIds(self):
        objs = Instrument.objects.all()
        objs = list(objs)
        self.assertTrue(len(objs)>0)
        
    def testObject(self):
        obj = Instrument.objects.get(id = 1)
        self.assertEqual(obj.id,1)
        self.assertTrue(obj.name)
        obj2 = Instrument.objects.get(name = obj.name)
        self.assertEqual(obj,obj2)
        
    def testFilter(self):
        c = 0
        for t in range(TYPELEN):
            objs = Instrument.objects.filter(type = t)
            for obj in objs:
                c += 1
                self.assertEqual(obj.type,t)
        all = Instrument.objects.all()
        self.assertEqual(c,len(all))
    
    def testFilter2(self):
        tot = 0
        for t in range(TYPELEN):
            fs = Fund.objects.filter(type = t)
            count = {}
            for f in fs:
                count[f.ccy] = count.get(f.ccy,0) + 1
            for c in choice_from:
                x = count.get(c,0)
                objs = fs.filter(ccy = c)
                y = 0
                for obj in objs:
                    y += 1
                    tot += 1
                    self.assertEqual(obj.type,t)
                    self.assertEqual(obj.ccy,c)
                self.assertEqual(x,y)
        all = Instrument.objects.all()
        self.assertEqual(tot,len(all))
        
    def testForeignKey(self):
        instruments = Instrument.objects.all()
        funds = populate('choice',5,choice_from = Fund.objects.all())
        dates = populate('date',10,start=datetime.date(2010,6,1),end=datetime.date(2010,6,6))
        for f in funds:
            insts = populate('choice',10,choice_from = instruments)
            for inst,dt in izip(insts,dates):
                Position(instrument = inst, dt = dt, fund = f).save()
        #
        positions = Position.objects.all()
        for p in positions:
            self.assertTrue(isinstance(p.instrument,Instrument))
        
        
    def _testDelete(self):
        obj = Position.objects.getid(t.id)
        
        

