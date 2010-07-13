'''Interfaces for supported data-structures'''

class Structure(object):
    '''Remote structure base class.
        
        * *cursor* instance of backend database.
        * *id* structure unique id.
        * *timeout* optional timeout.'''
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
    
    def size(self):
        '''Number of elements in structure'''
        raise NotImplementedError

    def __contains__(self, val):
        raise NotImplementedError
    
    def __iter__(self):
        return self._unwind().__iter__()
    
    def _all(self):
        raise NotImplementedError
    
    def delete(self):
        '''Delete structure from remote server.'''
        raise NotImplementedError
    
    def __len__(self):
        return self.size()
    
    def _unwind(self):
        if self._cache is None:
            self._cache = self._all()
        return self._cache
    
    
class List(Structure):
    
    def push_back(self, value):
        '''Appends a copy of *value* to the end of the remote list.'''
        raise NotImplementedError
    
    def push_front(self, value):
        '''Appends a copy of *value* to the beginning of the remote list.'''
        raise NotImplementedError
    
    
class HashTable(Structure):
    '''Interface class for a remote hash-table.'''
    
    def add(self, key, value):
        '''Add *key* - *value* pair to hashtable.'''
        raise NotImplementedError
    
    def update(self, mapping):
        '''Add *mapping* dictionary to hashtable. Equivalent to python dictionary update method.'''
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

    def update(self, sset):
        raise NotImplementedError
    
