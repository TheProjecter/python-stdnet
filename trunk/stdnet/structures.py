'''Interfaces for supported data-structures'''

class Structure(object):
    
    def __init__(self, cursor, id, timeout):
        self.cursor  = cursor
        self.timeout = timeout
        self.id      = id
        self._cache  = None
    
    def __repr__(self):
        base = '%s:%s' % (self.__class__.__name__,self.id)
        if self._cache is None:
            return base
        else:
            return '%s %s' % (base,self._cache)
        
    def __str__(self):
        return self.__repr__()
        
    def ids(self):
        return self.id,
    
    def size(self):
        raise NotImplementedError
    
    def __iter__(self):
        return self._unwind().__iter__()
    
    def _all(self):
        raise NotImplementedError
    
    def __len__(self):
        return self.size()
    
    def _unwind(self):
        if self._cache is None:
            self._cache = self._all()
        return self._cache
    
    
class List(Structure):
    
    def push_back(self, value):
        raise NotImplementedError
    
    def push_front(self, value):
        raise NotImplementedError
    
    
class HashTable(Structure):
    
    def add(self, key, value):
        raise NotImplementedError
    
    def get(self, key):
        raise NotImplementedError
    
    def mget(self, keys):
        raise NotImplementedError
    
    def keys(self, desc = False):
        raise NotImplementedError
    
    def values(self, desc = False):
        raise NotImplementedError

    def items(self, desc = False):
        raise NotImplementedError
    
    def __iter__(self):
        return self.keys().__iter__()


class Set(Structure):
    
    def add(self, value):
        raise NotImplementedError
    
    
