'''Interfaces for supported data-structures'''
from orm import StdModel

class Structure(object):
    '''Remote structure base class.
        
        * *cursor* instance of backend database.
        * *id* structure unique id.
        * *timeout* optional timeout.'''
    def __init__(self, cursor, id, timeout = 0, pipeline = None, pickler = None):
        self.cursor    = cursor
        self.pickler   = pickler or cursor.pickler
        self.id        = id
        self.timeout   = timeout
        self._cache    = None
        self._pipeline = pipeline
    
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
        if self._cache is None:
            return self._size()
        else:
            return len(self._cache)
    
    def __iter__(self):
        raise NotImplementedError()
    
    def _all(self):
        raise NotImplementedError
    
    def _size(self):
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
    
    def save(self):
        if self._pipeline:
            s = self._save()
            self._pipeline.clear()
            return s
        else:
            return 0
        
    def _save(self):
        raise NotImplementedError("Could not save")


class Set(Structure):
    '''An unordered set structure'''
    
    def __iter__(self):
        if not self._cache:
            cache = []
            loads = self.pickler.loads
            for item in self._all():
                item = loads(item)
                cache.append(item)
                yield item
            self.cache = cache
        else:
            for item in self.cache:
                yield item
                
    def add(self, value):
        '''Add *value* to the set'''
        self._pipeline.add(self.pickler.dumps(value))

    def update(self, values):
        '''Add iterable *values* to the set'''
        pipeline = self._pipeline
        for value in values:
            pipeline.add(self.pickler.dumps(value))


class OrderedSet(Set):
    '''An ordered set structure'''
    
    def __iter__(self):
        if not self._cache:
            cache = []
            loads = self.pickler.loads
            for item in self._all():
                item = loads(item)
                cache.append(item)
                yield item
            self.cache = cache
        else:
            for item in self.cache:
                yield item
                
    def add(self, value):
        '''Add *value* to the set'''
        self._pipeline.add((value.score(),self.pickler.dumps(value)))
    
class List(Structure):

    def __iter__(self):
        if not self._cache:
            cache = []
            loads = self.pickler.loads
            for item in self._all():
                item = loads(item)
                cache.append(item)
                yield item
            self.cache = cache
        else:
            for item in self.cache:
                yield item
    
    def pop_back(self):
        raise NotImplementedError
    
    def pop_front(self):
        raise NotImplementedError
    
    def push_back(self, value):
        '''Appends a copy of *value* to the end of the remote list.'''
        self._pipeline.push_back(self.pickler.dumps(value))
    
    def push_front(self, value):
        '''Appends a copy of *value* to the beginning of the remote list.'''
        self._pipeline.push_front(self.pickler.dumps(value))
    
    
class HashTable(Structure):
    '''Interface class for a remote hash-table.'''
    
    def add(self, key, value):
        '''Add *key* - *value* pair to hashtable.'''
        self._pipeline[key] = self.pickler.dumps(value)
    __setitem__ = add
    
    def update(self, mapping):
        '''Add *mapping* dictionary to hashtable. Equivalent to python dictionary update method.'''
        p = self._pipeline
        for k,value in mapping:
            p[key] = self.pickler.dumps(value)
    
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

    
