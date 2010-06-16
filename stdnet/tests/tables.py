import datetime
import unittest

from stdnet import orm

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


class TestORM(unittest.TestCase):
    
    def setUp(self):
        self.p = Instrument(name = 'eru10', type = 4).save()
        Instrument(name = 'erz10', type = 4).save()
        Instrument(name = 'goog', type = 2).save()
        
    def testIds(self):
        p = self.p
        self.assertEqual(len(Instrument._meta.fields),3)
        self.assertEqual(len(Fund._meta.fields),4)
        self.assertEqual(p.name,'eru10')
        self.assertEqual(p.type, 4)
        self.assertEqual(p.id,1)
        
    def testObject(self):
        p = self.p
        obj = Instrument.objects.get(id = p.id)
        self.assertEqual(obj.name,'eru10')
        self.assertEqual(obj.type,4)
        self.assertEqual(obj.id,1)
        self.assertEqual(obj,p)
        
    def testFilter(self):
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
        orm.clear()
        

