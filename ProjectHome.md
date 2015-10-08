**The project has moved over to github at** http://github.com/lsbardel/python-stdnet

  * [Documentation](http://lsbardel.github.com/python-stdnet/)
  * [Downloads](http://pypi.python.org/pypi/python-stdnet/)

An [Object Relational Mapping](http://en.wikipedia.org/wiki/Object-relational_mapping) for remote data-structures.


```
from stdnet import orm

class Ticker(orm.StdModel):
    name   = orm.AtomField(unique = True)
    ccy    = orm.AtomField()
    
    def __str__(self):
        return self.name

class Field(orm.StdModel):
    name   = orm.AtomField(unique = True)

class TimeSerie(orm.StdModel):
    ticker = orm.ForeignKey(Ticker)
    field  = orm.ForeignKey(Field)
    data   = orm.HashField()

# Register your model to a backend
orm.register(Ticker,'redis://localhost:6379/?db=3')
orm.register(Field,'redis://localhost:6379/?db=3')
orm.register(TimeSerie,'redis://localhost:6379/?db=4')
```