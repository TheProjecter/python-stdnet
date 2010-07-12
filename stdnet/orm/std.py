from fields import Field, RelatedField, _novalue


class StdField(RelatedField):
    '''Base class for data-structure fields'''
    def __init__(self, model = None, index = False, required = False, **kwargs):
        self._cache = set()
        super(StdField,self).__init__(model = model, index = index,
                                      required = required, **kwargs)
        
    def set_model_value(self, name, obj, value = _novalue):
        super(StdField,self).set_model_value(name, obj, value)
        return self
    
    def model_get_arg(self):
        return None
    
    def delete(self):
        self.dbobj().delete()
    
    def dbobj(self):
        raise NotImplementedError('Could not obtain database object')
    
    def from_value(self, value):
        if self.model:
            return value.id
        else:
            return value
    
    def _id(self):
        '''The structure id in the database. It depends on the object id
and the name of the field.'''
        return self.meta.basekey('id',self.obj.id,self.name)
    
    def save_index(self, commit, value):
        if self._cache and commit:
            if self.model:
                idcache = set()
                for obj in self._cache:
                    idcache.add(obj.id)
                    related = getattr(obj,self.related_name)
                    related.add(self.obj)
                    related.save(commit)
                    


class SetField(StdField):
    '''A field maintaining an unordered collection of string/numeric values. It is initiated
without any argument. Equivalent to python ``set``. For example::

    class User(orm.StdModel):
        username  = orm.AtomField(unique = True)
        password  = orm.AtomField()
        friends   = orm.SetField()
    
    
It can be used in the following way::
    
    >>> user = User(username = 'lsbardel', password = 'mypassword').save()
    >>> user2 = User(username = 'pippo', password = 'pippopassword').save()
    >>> user.add(user2)
    >>> user.save()
    >>> user2 in user.friends
    True
    >>> _
    '''    
    def __iter__(self):
        self.save()
        return self.dbobj().__iter__()
    
    def dbobj(self):
        return self.meta.cursor.unordered_set(self._id())
    
    def add(self, value):
        '''Add a *value* to the set. If value is
an instance of :ref:`StdModel <model-model>`, the id will be added.'''
        self._cache.add(value)
        
    def update(self, values):
        '''Update self with the union of itself and *values*.'''
        
        self._cache.update(set(self.from_value(value) for value in values))
    
    def __contains__(self, value):
        self.save()
        return self.from_value(value) in self.dbobj()
    
    def savevalue(self, commit = True, **kwargs):
        if self._cache and commit:
            obj = self.dbobj()
            obj.update(self._cache)
            self._cache.clear()
            

class ListField(StdField):
    '''A field maintaining a list of string/numeric values. It is initiated without any argument.
For example::

    class UserMessage(orm.StdModel):
        user = orm.AtomField()
        messages = orm.ListField()
    
    m = UserMessage(user = 'pippo')
    m.push_back("ciao")
    m.save()
    '''
    def __init__(self, **kwargs):
        self._back_cache = []
        self._front_cache = []
        super(ListField,self).__init__(**kwargs)
    
    def size(self):
        '''Return the length of the list'''
        return self.dbobj().size()
    
    def __iter__(self):
        self.save()
        return self.dbobj().__iter__()
    
    def push_back(self, value):
        '''Appends a copy of *value* to the end of the list. If *value* is
an instance of :ref:`StdModel <model-model>`, the id will be used.'''
        self._back_cache.append(self.from_value(value))
        
    def push_front(self, value):
        '''Appends a copy of *value* to the front of the list. If *value* is
an instance of :ref:`StdModel <model-model>`, the id will be used.'''
        self._front_cache.append(self.from_value(value))
        
    def pop_back(self):
        '''Removes and returns the last element.'''
        self.save()
        return self.dbobj().pop_back()
        
    def pop_front(self):
        '''Removes and returns the first element.'''
        self.save()
        return self.dbobj().pop_front()
    
    def save(self, commit = True):
        if (self._back_cache or self._front_cache) and commit:
            obj = self.dbobj()
            if self._back_cache:
                obj.push_back(self._back_cache)
                self._back_cache = []
            if self._front_cache:
                obj.push_front(self._front_cache)
                self._front_cache = []
    
    def dbobj(self):
        return self.meta.cursor.list(self._id())
                

class OrderedSetField(StdField):
    pass


defcon = lambda x: x

class HashField(StdField):
    '''A Hash table field, the networked equivalent of a python dictionary.
Keys are string while values are string/numeric. It accepts to optional arguments:
    * *converter* to convert the key into a new representation.
    * *inverse* the inverse of *converter*.
'''
    def __init__(self, converter = None, inverse = None):
        self._cache    = {}
        self.converter = converter or defcon
        self.inverse   = inverse or defcon
        super(HashField,self).__init__()
            
    def add(self, key, value):
        '''Add a key with value *value*. If key is available, its value will be updated'''
        self._cache[self.converter(key)] = value
        
    def get(self, key):
        '''Get a key value. If key is not available it will return None.'''
        self.save()
        return self.dbobj().get(self.converter(key))
    
    def __setitem__(self, key, value):
        self.add(key,value)
        
    def __getitem__(self, key):
        self.ged(key)

    def dbobj(self):
        return self.meta.cursor.hash(self._id())
    
    def items(self):
        self.save()
        obj = self.dbobj()
        inv = self.inverse
        for key,value in obj.items():
            yield inv(key),value 
    
    def keys(self):
        self.save()
        obj = self.dbobj()
        return obj.keys()
        
    def save(self, commit = True):
        if self._cache and commit:
            obj = self.dbobj()
            obj.update(self._cache)
            self._cache.clear()
        


class MapField(HashField):
    '''A map is a sorted key-value container'''
    def dbobj(self):
        return self.meta.cursor.map(self._id())

    