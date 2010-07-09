from fields import Field, _novalue


class StdField(Field):
    
    def __init__(self):
        super(StdField,self).__init__(index = False, required = False)
    
    def set_model_value(self, name, obj, value = _novalue):
        super(StdField,self).set_model_value(name, obj, value)
        return self
    
    def model_get_arg(self):
        return None
            
    def _id(self):
        return self.meta.basekey('id',self.obj.id,self.name)


class SetDField(StdField):
    '''A set field.'''
    pass


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
    def __init__(self):
        self._back_cache = []
        self._front_cache = []
        super(ListField,self).__init__()
    
    def size(self):
        '''Return the length of the list'''
        return self.cacheobj().size()
    
    def __iter__(self):
        self.save()
        return self.cacheobj().__iter__()
    
    def push_back(self, val):
        '''Appends a copy of val to the end of the list.'''
        self._back_cache.append(val)
        
    def push_front(self, val):
        '''Appends a copy of val to the front of the list.'''
        self._front_cache.append(val)
        
    def pop_back(self):
        '''Removes and returns the last element.'''
        self.save()
        return self.cacheobj().pop_back()
        
    def pop_front(self):
        '''Removes and returns the first element.'''
        self.save()
        return self.cacheobj().pop_front()
    
    def save(self, commit = True):
        if (self._back_cache or self._front_cache) and commit:
            obj = self.cacheobj()
            if self._back_cache:
                obj.push_back(self._back_cache)
                self._back_cache = []
            if self._front_cache:
                obj.push_front(self._front_cache)
                self._front_cache = []
    
    def cacheobj(self):
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
        return self.cacheobj().get(self.converter(key))
    
    def __setitem__(self, key, value):
        self.add(key,value)
        
    def __getitem__(self, key):
        self.ged(key)

    def cacheobj(self):
        return self.meta.cursor.hash(self._id())
    
    def items(self):
        self.save()
        obj = self.cacheobj()
        inv = self.inverse
        for key,value in obj.items():
            yield inv(key),value 
    
    def keys(self):
        self.save()
        obj = self.cacheobj()
        return obj.keys()
        
    def save(self, commit = True):
        if self._cache and commit:
            obj = self.cacheobj()
            obj.update(self._cache)
            self._cache.clear()
        

class MapField(HashField):
    '''A map is a sorted key-value container'''
    def cacheobj(self):
        return self.meta.cursor.map(self._id())
    