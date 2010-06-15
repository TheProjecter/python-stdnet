from fields import Field, _novalue


class StdField(Field):
    
    def __init__(self):
        super(StdField,self).__init__(index = False, required = False)

    def set_model_value(self, name, obj, value = _novalue):
        super(StdField,self).set_model_value(name, obj, value)
        return self
    
    def model_get_arg(self):
        return None
            
    def id(self):
        return self.meta.basekey('id',self.obj.id,self.name)


class StdSet(StdField):
    pass


class StdList(StdField):
    pass


class StdOrderedSet(StdField):
    pass


class StdHash(StdField):
    
    def add(self, key, value):
        id = self.id()
        self.cache.hset(key,value)


class StdMap(StdField):
    '''A map is a sorted key-value container'''
    def add(self, key, value):
        id = self.id()
        c  = self.meta.cache
        c.madd(id, key, value)
        