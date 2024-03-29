from datetime import datetime
from itertools import izip

from stdnet.test import TestCase
from stdnet.utils import populate

from examples.models import Calendar, DateValue

NUM_DATES = 100

dates = populate('date',NUM_DATES)
values = populate('string', NUM_DATES, min_len = 10, max_len = 120)


class TestOrderedSet(TestCase):
    
    def setUp(self):
        self.orm.register(Calendar)
        self.orm.register(DateValue)
        ts = Calendar(name = 'MyCalendar').save()
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
                
            
        
        