from stdnet.exceptions import ImproperlyConfigured, BadCacheDataStructure

novalue = object()

class ObjectCache(object):
    
    def __init__(self, meta):
        self.meta    = meta
        self.objs    = {}
        self.indexes = {}
        self.keys    = {}
        if meta.timeout:
            self.needtimeout = True
        else:
            self.needtimeout = False
            
    def addindex(self, key, value):
        s = self.indexes.get(key,None)
        if s is None:
            s = set()
            self.indexes[key] = s
        s.add(value)
        
    def clear(self):
        self.objs.clear()
        self.indexes.clear()
        self.keys.clear()
            

class BaseBackend(object):
    '''Generic interface for a backend database:
    
    * *name* name of database, such as **redis**, **couchdb**, etc..
    * *params* dictionary of configuration parameters
    '''
    def __init__(self, name, params):
        self.__name = name
        timeout = params.get('timeout', 0)
        try:
            timeout = int(timeout)
        except (ValueError, TypeError):
            timeout = 0
        self.default_timeout = timeout
        self._cachepipe = {}

    @property
    def name(self):
        return self.__name
    
    def __repr__(self):
        return '%s backend' % self.__name
    
    def __str__(self):
        return self.__repr__()
    
    def createdb(self, name):
        pass
    
    def add_object(self, obj, commit = True):
        '''Add a model object to the database:
        
        * *obj* instance of ref:`StdModel <std-model>`
        * *commit* If true model is saved to database, otherwise it remains in cache.
        '''
        meta   = obj.meta
        id     = meta.basekey()
        cache  = self._cachepipe
        cvalue = cache.get(id,None)
        if cvalue is None:
            cvalue = ObjectCache(meta)
            cache[id] = cvalue
                
        cvalue.objs[obj.id] = obj
        
        for name,field in meta.fields.items():
            if name is not 'id' and field.index:
                value   = field.hash(field.serialize())
                key     = meta.basekey(field.name,value)
                if field.unique:
                    cvalue.keys[key] = obj.id
                else:
                    cvalue.addindex(key,value)
                
        if commit:
            self.commit()
            
    def commit(self):
        '''Commit cache objects to0 backend database'''
        for id,cvalue in self._cachepipe.iteritems():
            if not cvalue.objs:
                continue
            hash = self.hash(id)
            hash.update(self.objs)
            if cvalue.needtimeout:
                cvalue.needtimeout = False
            self.commit_indexes(cvalue)
            cvalue.clear()
            
    def commit_indexes(self, cvalue):
        pass
            
    def add_object_old(self, obj, commit = True):
        '''Add a model object to the database:
        
        * *obj* instance of ref:`StdModel <std-model>`
        * *commit* If true model is saved to database, otherwise it remains in cache.
        '''
        id = obj.meta.basekey()
        if commit:
            hash = self.hash(id)
            return hash.add(obj.id, obj)
        else:
            cache  = self._cache_objs
            cvalue = cache.get(id,None)
            if cvalue is None:
                cvalue = cacheValue({})
                cache[id] = cvalue
            cvalue.value[obj.id] = obj
    
    def add_index(self, key, obj, commit = True):
        '''Add index for model instance *obj*'''
        cache  = self._cachepipe
        cvalue = cache.get(obj.meta.basekey(),None)
        if cvalue is None:
            cvalue = cacheValue(set())
            cache[key] = cvalue
        cvalue.value.add(value)
        if commit:
            self.commit()
    
    def add_string(self, key, value, commit = True, timeout = 0):
        if commit:
            return self.set(key, value, timeout = timeout)
        else:
            self._cache_strs[key] = cacheValue(value,timeout)
            
    def delete_object(self, obj):
        '''Remove a StdModel from database'''
        raise NotImplementedError()

    def get(self, key, default=None):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        raise NotImplementedError

    def delete(self, key):
        """
        Delete a key from the cache, failing silently.
        """
        raise NotImplementedError

    def get_many(self, keys):
        """
        Fetch a bunch of keys from the cache. For certain backends (memcached,
        pgsql) this can be *much* faster when fetching multiple values.

        Returns a dict mapping each key in keys to its value. If the given
        key is missing, it will be missing from the response dict.
        """
        d = {}
        for k in keys:
            val = self.get(k)
            if val is not None:
                d[k] = val
        return d

    def has_key(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        return self.get(key) is not None

    def incr(self, key, delta=1):
        """
        Add delta to value in the cache. If the key does not exist, raise a
        ValueError exception.
        """
        if key not in self:
            raise ValueError("Key '%s' not found" % key)
        new_value = self.get(key) + delta
        self.set(key, new_value)
        return new_value

    def decr(self, key, delta=1):
        """
        Subtract delta from value in the cache. If the key does not exist, raise
        a ValueError exception.
        """
        return self.incr(key, -delta)

    def __contains__(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        # This is a separate method, rather than just a copy of has_key(),
        # so that it always has the same functionality as has_key(), even
        # if a subclass overrides it.
        return self.has_key(key)

    def set_many(self, data, timeout=None):
        """
        Set a bunch of values in the cache at once from a dict of key/value
        pairs.  For certain backends (memcached), this is much more efficient
        than calling set() multiple times.

        If timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.
        """
        for key, value in data.items():
            self.set(key, value, timeout)

    def delete_many(self, keys):
        """
        Set a bunch of values in the cache at once.  For certain backends
        (memcached), this is much more efficient than calling delete() multiple
        times.
        """
        for key in keys:
            self.delete(key)

    def clear(self):
        """Remove *all* values from the cache at once."""
        raise NotImplementedError

    def list(self, id, timeout = 0):
        '''Return an instance of :ref:`List <list-structure>`
        for a given *id*.'''
        raise NotImplementedError
    
    def hash(self, id, timeout = 0):
        '''Return an instance of :ref:`HashTable <hash-structure>`
        for a given *id*.'''
        raise NotImplementedError
    
    def unordered_set(self, key, timeout = 0):
        raise NotImplementedError
    
    def map(self, key, timeout = 0):
        raise NotImplementedError

