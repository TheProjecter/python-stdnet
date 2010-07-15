from stdnet import orm

class Base(orm.StdModel):
    name = orm.AtomField(unique = True)
    ccy  = orm.AtomField()
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        abstract = True


class Instrument(Base):
    type = orm.AtomField()

    
class Fund(Base):
    pass


class Position(orm.StdModel):
    instrument = orm.ForeignKey(Instrument, related_name = 'positions')
    fund       = orm.ForeignKey(Fund)
    dt         = orm.DateField()
    
    def __str__(self):
        return '%s: %s @ %s' % (self.fund,self.instrument,self.dt)
    
    def __init__(self, size = 1, price = 1, **kwargs):
        self.size  = size
        self.price = price
        super(Position,self).__init__(**kwargs)

