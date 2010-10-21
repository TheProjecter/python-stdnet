from stdnet import orm

class Base(orm.StdModel):
    name = orm.SymbolField(unique = True)
    ccy  = orm.SymbolField()
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        abstract = True


class Instrument(Base):
    type = orm.SymbolField()

    
class Fund(Base):
    description = orm.CharField()


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


class PortfolioView(orm.StdModel):
    name      = orm.AtomField()
    portfolio = orm.ForeignKey(Fund)
    
class UserDefaultView(orm.StdModel):
    user = orm.AtomField()
    view = orm.ForeignKey(PortfolioView)