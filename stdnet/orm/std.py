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

class StdSet(StdField):
    pass


class StdList(StdField):
    pass


class StdOrderedSet(StdField):
    pass


defcon = lambda x: x

class HashField(StdField):
    
    def __init__(self, converter = defcon, inverse = defcon):
        self._cache    = {}
        self.converter = converter
        self.inverse   = inverse
        super(HashField,self).__init__()
        
    def converter(self, key):
        return key
    
    def inverse(self, key):
        return key
        
    def add(self, key, value):
        self._cache[self.converter(key)] = value
        
    def get(self, key):
        self.save()
        obj = self.cacheobj()
        return obj.get(self.converter(key))

    def cacheobj(self):
        return self.meta.cache.hash(self._id())
    
    def items(self):
        self.save()
        obj = self.cacheobj()
        return obj.items()
    
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
    