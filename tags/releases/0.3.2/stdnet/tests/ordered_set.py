'''A twitter'''
from datetime import datetime
from itertools import izip

from stdnet import orm
from stdnet.stdtest import TestBase
from stdnet.utils import populate

from examples.calendarevents import Calendar, DateValue

orm.register(Calendar)
orm.register(DateValue)

NUM_DATES = 100

dates = populate('date',NUM_DATES)
values = populate('string', NUM_DATES, min_len = 10, max_len = 120)


class TestOrderedSet(TestBase):
    
    def setUp(self):
        ts = Calendar(name = 'MyCalendar')
        for dt,value in izip(dates,values):
            ts.add(dt,value)
        ts.save()
        
    def testOrder(self):
        ts = Calendar.objects.get(name = 'MyCalendar')
        self.assertEqual(ts.data.size(),NUM_DATES)
        dprec = None
        for event in ts.data:
            if dprec:
                self.assertTrue(event.dt >= dprec)
            dprec = event.dt    
                
            
        
        