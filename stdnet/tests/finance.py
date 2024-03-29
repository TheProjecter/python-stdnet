import datetime
import logging
from itertools import izip
from random import randint

from stdnet.test import TestCase
from stdnet.utils import populate
from stdnet.exceptions import QuerySetError

from examples.models import Instrument, Fund, Position, PortfolioView, UserDefaultView


INST_LEN    = 100
FUND_LEN    = 10
POS_LEN     = 30
NUM_USERS   = 10
NUM_DATES   = 2

ccys_types  = ['EUR','GBP','AUD','USD','CHF','JPY']
insts_types = ['equity','bond','future','cash','option']

inst_names = populate('string',INST_LEN, min_len = 5, max_len = 20)
inst_types = populate('choice',INST_LEN, choice_from = insts_types)
inst_ccys  = populate('choice',INST_LEN, choice_from = ccys_types)

fund_names = populate('string',FUND_LEN, min_len = 5, max_len = 20)
fund_ccys  = populate('choice',FUND_LEN, choice_from = ccys_types)

users      = populate('string', NUM_USERS, min_len = 8, max_len = 14)
view_names = populate('string', 4*FUND_LEN, min_len = 10, max_len = 20)

dates = populate('date',NUM_DATES,start=datetime.date(2009,6,1),end=datetime.date(2010,6,6))



class TestFinanceApplication(TestCase):
    
    def setUp(self):
        '''Create Instruments and Funds commiting at the end for speed'''
        orm = self.orm
        orm.register(Instrument)
        orm.register(Fund)
        orm.register(Position)
        orm.register(PortfolioView)
        orm.register(UserDefaultView)
        for name,typ,ccy in izip(inst_names,inst_types,inst_ccys):
            Instrument(name = name, type = typ, ccy = ccy).save(False)
        Instrument.commit()
        for name,ccy in izip(fund_names,fund_ccys):
            Fund(name = name, ccy = ccy).save(False)
        Fund.commit()
    
    def makePositions(self):
        '''Create Positions objects which hold foreign key to instruments and funds'''
        instruments = Instrument.objects.all()
        n = 0
        for f in Fund.objects.all():
            insts = populate('choice',POS_LEN,choice_from = instruments)
            for dt in dates:
                for inst in insts:
                    n += 1
                    Position(instrument = inst, dt = dt, fund = f).save(False)
        Position.commit()
        return n
        
    def testGetObject(self):
        '''Test get method for id and unique field'''
        obj = Instrument.objects.get(id = 1)
        self.assertEqual(obj.id,1)
        self.assertTrue(obj.name)
        obj2 = Instrument.objects.get(name = obj.name)
        self.assertEqual(obj,obj2)
        
    def testLen(self):
        '''Simply test len of objects greater than zero'''
        objs = Instrument.objects.all()
        self.assertTrue(len(objs)>0)
    
    def testFilter(self):
        '''Test filtering on a model without foreignkeys'''
        try:
            result = Instrument.objects.get(type = 'equity')
        except QuerySetError:
            pass
        else:
            self.fail('get query on non-unique field should have failed')
        tot = 0
        for t in insts_types:
            fs = Instrument.objects.filter(type = t)
            N  = fs.count()
            count = {}
            for f in fs:
                count[f.ccy] = count.get(f.ccy,0) + 1
            for c in ccys_types:
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
        '''Test filtering with foreignkeys'''
        self.makePositions()
        #
        positions = Position.objects.all()
        for p in positions:
            self.assertTrue(isinstance(p.instrument,Instrument))
            self.assertTrue(isinstance(p.fund,Fund))
            pos = Position.objects.filter(instrument = p.instrument,
                                          fund = p.fund)
            found = 0
            for po in pos:
                if po == p:
                    found += 1
            self.assertEqual(found,1)
                
        # Testing 
        total_positions = len(positions)
        totp = 0
        for instrument in Instrument.objects.all():
            pos  = list(instrument.positions.all())
            for p in pos:
                self.assertTrue(isinstance(p,Position))
                self.assertEqual(p.instrument,instrument)
            totp += len(pos)
        
        self.assertEqual(total_positions,totp)
        
    def testRelatedManagerFilter(self):
        self.makePositions()
        instruments = Instrument.objects.all()
        for instrument in instruments:
            positions = instrument.positions.all()
            funds = {}
            flist = []
            for pos in positions:
                fund = pos.fund
                n    = funds.get(fund.id,0) + 1
                funds[fund.id] = n
                if n == 1:
                    flist.append(fund)
            for fund in flist:
                positions = instrument.positions.filter(fund = fund)
                self.assertEqual(len(positions),funds[fund.id])
            
        
    def testDeleteSimple(self):
        '''Test delete on models without related models'''
        instruments = Instrument.objects.all()
        funds = Fund.objects.all()
        Ni = len(instruments)
        Nf = len(funds)
        self.assertEqual(Ni,instruments.delete())
        self.assertEqual(Nf,funds.delete())
        
    def testDelete(self):
        '''Test delete on models with related models'''
        # Create Positions which hold foreign keys to Instruments
        Np = self.makePositions()
        instruments = Instrument.objects.all()
        Ni = len(instruments)
        T = instruments.delete()
        self.assertEqual(T,Np+Ni)
        
    def __testNestedLookUp(self):
        # Create Portfolio views
        funds = Fund.objects.all()
        N     = funds.count()
        for name in view_names:
            fund = funds[randint(0,N-1)] 
            PortfolioView(name = name, portfolio = fund).save(False)
        PortfolioView.commit()
        views = PortfolioView.objects.all()
        N = views.count()
        for user in users:
            for i in range(0,FUND_LEN): 
                view = views[randint(0,N-1)]
                user = UserDefaultView(user = user, view = view).save()
        UserDefaultView.commit()
        #
        #Finally do the filtering
        N = 0
        for fund in funds:
            res = UserDefaultView.objects.filter(view__portfolio = fund)
            N += res.count()
            
        
         

