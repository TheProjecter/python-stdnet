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


class HashField(StdField):
    
    def __init__(self):
        super(HashField,self).__init__()
        self._cache = {}
        
    def add(self, key, value):
        self._cache[key] = value

    def cacheobj(self):
        return self.meta.cache.hash(self._id())
    
    def all(self):
        self.save()
        obj = self.cacheobj()
        return obj.items() 
            
    def save(self, commit = True):
        if self._cache and commit:
            obj = self.cacheobj()
            obj.update(self._cache)
            self._cache.clear()
        

class MapField(HashField):
    '''A map is a sorted key-value container'''
    def cacheobj(self):
        return self.meta.cursor.map(self._id())
    