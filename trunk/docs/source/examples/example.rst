.. _intro-example:

A very simple example on how to manage timeseries data.

Define the models::
    
    from stdnet import orm
    
    class DateValue(object):
    def __init__(self, dt, value):
        self.dt = dt
        self.value = value

    def score(self):
        "implement the score function for sorting in the ordered set"
        return int(1000*time.mktime(self.dt.timetuple()))
    
    class TimeSerie(orm.StdModel):
        ticker = orm.AtomField()
        data   = orm.HashField()
        
register it to a backend::

    orm.register(TimeSerie,'redis://')
    
and create objects::

    ts = TimeSerie(ticker = 'GOOG').save()
    ts.data.add(date.today(),485)
    ts.save()
