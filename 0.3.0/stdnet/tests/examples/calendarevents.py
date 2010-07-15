import time
from datetime import date
from stdnet import orm
from stdnet.utils import json

class DateValue(orm.StdModel):
    "An helper class for adding calendar events"
    
    def __init__(self, dt, value):
        self.dt = dt
        self.value = value
        super(DateValue,self).__init__()
    
    def score(self):
        "implement the score function for sorting in the ordered set"
        return int(1000*time.mktime(self.dt.timetuple()))
    
    
class Calendar(orm.StdModel):
    name   = orm.AtomField(unique = True)
    data   = orm.OrderedSetField(model = DateValue)
    
    def add(self, dt, value):
        event = DateValue(dt,value).save()
        self.data.add(event)
        
