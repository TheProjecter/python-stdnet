import datetime
import unittest

from stdnet import orm

class Instrument(orm.StdModel):
    name = orm.AtomField(unique = True)
    type = orm.AtomField()

class Trade(orm.StdModel):
    instrument = orm.ForeignKey(Instrument)
    date       = orm.DateField()
    
orm.register(Instrument)
orm.register(Trade)


class TestORM(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def testIds(self):
        p = Instrument(name = 'luca', type = 4)
        self.assertEqual(p.name,'luca')
        self.assertEqual(p.type, 4)
        self.assertEqual(p.id,None)
        p.save()
        self.assertEqual(p.id,1)
        p2 = Instrument(name = 'equity', type = 2)
        p2.save()
        self.assertEqual(p2.id,2)
        
    def testObject(self):
        p = Instrument(name = 'luca', type = 4)
        p.save()
        self.assertEqual(p.id,1)
        obj = Instrument.objects.getid(p.id)
        self.assertEqual(obj.name,'luca')
        self.assertEqual(obj.type,4)
        self.assertEqual(obj.id,1)
        self.assertEqual(obj,p)
    
    def testForeignKey(self):
        p = Instrument(name = 'future', type = 4)
        p.save()
        t = Trade(instrument = p, date = datetime.date.today())
        t.save()
        obj = Trade.objects.getid(t.id)
        p1  = obj.instrument
        self.assertEqual(p,p1)
        self.assertEqual(obj.instrument.name,'future')
        
    def tearDown(self):
        orm.clear()
        

