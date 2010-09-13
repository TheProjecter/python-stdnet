from fields import Field, RelatedObject, _novalue

from stdnet.exceptions import *
from stdnet.utils import ModelFieldPickler, listPipeline, many2manyPipeline


class MultiField(Field):
    '''Base virtual class for data-structure fields:
    
    * *model* optional :ref:`StdModel <model-model>` class.
    * *related_name* same as :ref:`ForeignKey <foreignkey>` Field.
    * *pickler* a module/class/objects used to serialize values.
    * *converter* a module/class/objects used to convert keys to suitable string to use as keys in :ref:`HashTables <hash-structure>`.
        It must implement two methods, ``tokey`` to convert key to a suitable key
        for the database backend and ``tovalue`` the inverse operation. By default
        is the class::
        
            class keyconverter(object):
                @classmethod
                def tokey(cls, value):
                    return value
                @classmethod
                def tovalue(cls, value):
                    return value
            
    '''
    backend_structure = None
    _pipeline = None
    
    def __init__(self,
                 model = None,
                 pickler = None,
                 converter = None,
                 **kwargs):
        self.model       = model
        super(MultiField,self).__init__(required = False,
                                        **kwargs)
        self.index       = False
        self.unique      = False
        self.pickler     = pickler
        self.converter   = converter
        
    def register_with_model(self, name, related):
        if not self.model:
            return
        if self.model == 'self':
            self.model = related
        
    def get_full_value(self):
        id = self.meta.basekey('id',self.obj.id,self.name)
        return self.structure(id,
                              timeout = self.meta.timeout,
                              pipeline = self._pipeline,
                              pickler = self.pickler,
                              converter = self.converter)
    
    def set_value(self, name, obj, value):
        v = super(MultiField,self).set_value(name, obj, value)
        self.set_structure()
        return v
        
    def set_structure(self):
        meta = self.meta
        self.structure = getattr(meta.cursor,self.backend_structure,None)
        if self.model and not self.pickler:
            self.pickler = ModelFieldPickler(self.model)
    
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
    

class ManyToManyField(SetField, RelatedObject):
    '''A many-to-many relationship. It accepts **related_name** as extra argument.
It is the name to use for the relation from the related object
back to self. For example::
    
    class User(orm.StdModel):
        name      = orm.AtomField(unique = True)
        following = orm.ManyToManyField(model = 'self',
                                        related_name = 'followers')
'''
    _pipeline = many2manyPipeline
    
    def __init__(self, model, related_name = None, **kwargs):
        SetField.__init__(self, **kwargs)
        RelatedObject.__init__(self,
                               model,
                               relmanager = self.__class__,
                               related_name = related_name)
        self.index = False
        
    def register_with_model(self, name, related):
        related_manager = self.register_related_model(name, related)
        related_manager.name = self.related_name
        
    def set_value(self, name, obj, value):
        v = SetField.set_value(self, name, obj, value)
        related_manager = self.model._meta.related[self.related_name]
        related_manager.meta = related_manager.model._meta
        related_manager.set_structure()
        return v
    
    def get_full_value(self):
        return self
    
    def _id(self):
        return self.meta.basekey('id',self.obj.id,self.name)
        
    def _relid(self, rel):
        return self.meta.basekey('id',rel.id,self.related_name)
    
    def add(self, value):
        if not isinstance(value,self.model):
            raise FieldValueError('%s is not an instance of %s' % (value,self.model._meta.name))
        if value is self:
            raise FieldValueError('Cannot add self')
        self._add(self.obj,self.name,value)
        self._add(value,self.related_name,self.obj)
    
    def _structure(self, obj, name):
        meta = obj._meta
        id   = meta.basekey('id',obj.id,name)
        return self.structure(id,
                              timeout = meta.timeout,
                              pipeline = self._pipeline[id],
                              pickler = self.pickler,
                              converter = self.converter)
        
    def _add(self, obj, name, value):
        s = self._structure(obj,name)
        s.add(value)
    
    def save(self):
        for id,pipeline in self._pipeline:
            s    = self.structure(id,
                                  pipeline = pipeline,
                                  pickler = self.pickler,
                                  converter = self.converter)
            s.save()
        self._pipeline.clear()
        
    def __iter__(self):
        return self._structure(self.obj, self.name).__iter__()
    
    def __contains__(self, item):
        return self._structure(self.obj, self.name).__contains__(item)
    
    def size(self):
        return self._structure(self.obj, self.name).size()
    
    def count(self):
        return self.size()        
