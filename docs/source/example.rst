.. _intro-example:


Define your model::
    
    from stdnet import orm
    
    class TimeSerie(orm.StdModel):
        ticker = orm.AtomField()
        data   = orm.HashField()
        
register it to a backend::

    orm.register(TimeSerie,'redis://')
    
and create objects::

    ts = TimeSerie(ticker = 'GOOG').save()
    ts.data.add(date.today(),485)
    ts.save()
