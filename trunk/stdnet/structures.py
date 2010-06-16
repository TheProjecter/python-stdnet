


class Structure(object):
    
    def __init__(self, cursor, id, timeout):
        self.cursor  = cursor
        self.timeout = timeout
        self.id      = id
        
    def ids(self):
        return self.id,
        
    def add(self, *args):
        raise NotImplementedError
    
    def size(self):
        raise NotImplementedError
    
    def __iter__(self):
        raise NotImplementedError
    
    def __len__(self):
        return self.size()
    
    
class HashTable(Structure):
    
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
    pass