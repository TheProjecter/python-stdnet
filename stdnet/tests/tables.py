import datetime
import unittest
from itertools import izip

from stdnet import orm
from stdnet.utils import populate

class Base(orm.StdModel):
    name = orm.AtomField(unique = True)
    type = orm.AtomField()
    
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


names = populate('string',1000, min_len = 5, max_len = 20)
types = populate('integer',1000, start=0, end=10)

class TestORM(unittest.TestCase):
    
    def setUp(self):
        for name,typ in izip(names,types):
            Instrument(name = name, type = typ).save()
        
    def testIds(self):
        objs = Instrument.objects.all()
        objs = list(objs)
        self.assertTrue(len(objs)>0)
        
    def _testObject(self):
        p = self.p
        obj = Instrument.objects.get(id = p.id)
        self.assertEqual(obj.name,'eru10')
        self.assertEqual(obj.type,4)
        self.assertEqual(obj.id,1)
        self.assertEqual(obj,p)
        
    def _testFilter(self):
        objs = Instrument.objects.filter(type = 4)
        objs = list(objs)
        self.assertEqual(len(objs),2)
        for obj in objs:
            self.assertEqual(obj.type,4)
    
    def _testForeignKey(self):
        p = Instrument.objects.get(id = self.p.id)
        f = Fund(name='myfund', ccy='EUR').save()
        t = Position(instrument = p, dt = datetime.date.today(), fund = f)
        t.save()
        obj = Position.objects.get(id = t.id)
        p1  = obj.instrument
        self.assertEqual(p,p1)
        self.assertEqual(obj.instrument.name,'eru10')
        
    def _testDelete(self):
        p = self.p
        self.assertEqual(len(p._meta.keys),3)
        p.delete()
        obj = Position.objects.getid(t.id)
        
    def tearDown(self):
        orm.clearall()
        

