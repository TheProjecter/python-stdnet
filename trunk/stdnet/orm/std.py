from fields import Field, RelatedField, _novalue
from query import MultiRelatedManager


class ModelFieldPickler(object):
    
    def __init__(self, model):
        self.model = model
        self.get   = model.objects.get
        
    def loads(self, s):
        return self.get(id = s)
    
    def dumps(self, obj):
        return obj.id
    

class listPipeline(object):
    def __init__(self):
        self.clear()
        
    def push_front(self, value):
        self.front.append(value)
        
    def push_back(self, value):
        self.back.append(value)
        
    def clear(self):
        self.back = []
        self.front = []
        
    def __len__(self):
        return len(self.back) + len(self.front)
    

class MultiField(RelatedField):
    '''Base virtual class for data-structure fields:
    
    * *model* optional :ref:`StdModel <model-model>` class. If specified, the field maintains a many-to-many object relationship.
    * *related_name* same as :ref:`ForeignKey <foreignkey>` Field.
    '''
    backend_structure = None
    _pipeline = None
    
    def __init__(self,
                 model = None,
                 related_name = None,
                 pickler = None,
                 converter = None,
                 **kwargs):
        super(MultiField,self).__init__(model = model,
                                        required = False,
                                        relmanager = MultiRelatedManager,
                                        **kwargs)
        self.index       = False
        self.unique      = False
        self.pickler     = pickler
        self.converter   = converter
        
    def get_full_value(self):
        id = self.meta.basekey('id',self.obj.id,self.name)
        return self.structure(id,
                              timeout = self.meta.timeout,
                              pipeline = self._pipeline,
                              pickler = self.pickler,
                              converter = self.converter)
    
    def set_value(self, name, obj, value):
        v = super(MultiField,self).set_value(name, obj, value)
        self.structure = getattr(self.meta.cursor,self.backend_structure,None)
        if self.model and not self.pickler:
            self.pickler = ModelFieldPickler(self.model)
        return v
    
    def serialize(self):
        return None
        
    def save_index(self, commit, value):
        if self._cache and commit:
            if self.model:
                idcache = set()
                for obj in self._cache:
                    idcache.add(obj.id)
                    related = getattr(obj,self.related_name)
                    related.add(self.obj)
                    related.save(commit)
    
    def save(self):
        return self.get_full_value().save()
        
    def __deepcopy__(self, memodict):
        obj = super(MultiField,self).__deepcopy__(memodict)
        obj._pipeline = self.__class__._pipeline()
        return obj


class SetField(MultiField):
    '''A field maintaining an unordered collection of values. It is initiated
without any argument otherr than an optional model class.
Equivalent to python ``set``. For example::

    class User(orm.StdModel):
        username  = orm.AtomField(unique = True)
        password  = orm.AtomField()
        following = orm.SetField(model = 'self',
                                 index = True,
                                 related_name = 'followers')
    
The ``following`` field define a many-to-many relationship between Users.
It can be used in the following way::
    
    >>> user = User(username = 'lsbardel', password = 'mypassword').save()
    >>> user2 = User(username = 'pippo', password = 'pippopassword').save()
    >>> user.following.add(user2)
    >>> user.save()
    >>> user2 in user.following
    True
    >>> _
    '''
    backend_structure = 'unordered_set'
    _pipeline = set
    

class ListField(MultiField):
    '''A field maintaining a list of values. When accessed from the model instance,
it returns an instance of :ref:`list structure <list-structure>`. For example::

    class UserMessage(orm.StdModel):
        user = orm.AtomField()
        messages = orm.ListField()
    
Can be used as::

    >>> m = UserMessage(user = 'pippo')
    >>> m.messages.push_back("adding my first message to the list")
    >>> m.messages.push_back("ciao")
    >>> m.save()
    '''
    backend_structure = 'list'
    _pipeline = listPipeline                


class OrderedSetField(SetField):
    '''A field maintaining an ordered set of values. It is initiated without any argument.
For example::
    
    import time
    from datetime import date
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
        data   = orm.OrderedSetField()
    
    
And to use it::

    >>> m = TimeSerie(ticker = 'GOOG')
    >>> m.data.add(DateValue(date(2010,6,1), 482.37))
    >>> m.data.add(DateValue(date(2010,6,2), 493.37))
    >>> m.data.add(DateValue(date(2010,6,3), 505.06))
    >>> m.save()
    '''
    backend_structure = 'ordered_set'


class HashField(MultiField):
    '''A Hash table field, the networked equivalent of a python dictionary.
Keys are string while values are string/numeric. It accepts to optional arguments:
'''
    backend_structure = 'hash'
    _pipeline = dict
    
