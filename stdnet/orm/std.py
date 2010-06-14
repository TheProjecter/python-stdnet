from fields import Field


class StdField(Field):
    
    def __init__(self):
        super(StdField,self).__init__(index = False)

class SetField(Field):
    pass

class ListField(Field):
    pass

class OrderedSetField(Field):
    pass


class HashField(Field):
    
    def add(self, key, value):
        id = self.id()
        self.cache.hset(key,value)
