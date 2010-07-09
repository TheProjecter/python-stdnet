'''
Base class for jflow cache
'''
from stdnet.exceptions import ImproperlyConfigured, BadCacheDataStructure

novalue = object()

class cacheValue(object):
    
    def __init__(self, value, timeout):
        self.timeout
        self.value = value



class BaseBackend(object):
    
    def __init__(self, name, params):
        self.__name = name
        timeout = params.get('timeout', 0)
        try:
            timeout = int(timeout)
        except (ValueError, TypeError):
            timeout = 0
        self.default_timeout = timeout
        self._cache_objs = {}
        self._cache_strs = {}
        self._cache_sets = {}
    
    def __repr__(self):
        return '%s backend' % self.__name
    
    def __str__(self):
        return self.__repr__()
    
    def createdb(self, name):
        pass
    
    def add_object(self, key, obj, commit = True, timeout = 0):
        '''Add a model object to the database'''
        if commit:
            hash = self.hash(key,timeout)
            return hash.add(obj.id, obj)
        else:
            cache = self._cache_objs
            cvalue = cache.get(key,None)
            if cvalue is None:
                cvalue = cacheValue({},timeout)
                cache[key] = cvalue
            cvalue.value[obj.id] = obj
    
    def add_string(self, key, value, commit = True, timeout = 0):
        if commit:
            return self.set(key, value, timeout = timeout)
        else:
            self._cache_strs[key] = cacheValue(value,timeout)
    
    def add_index(self, key, value, commit = True, timeout = 0):
        if commit:
            set = self.unordered_set(key,timeout)
            return set.add(value)
        else:
            cache = self._cache_sets
            cvalue = cache.get(key,None)
            if cvalue is None:
                cvalue = cacheValue(set(),timeout)
                cache[key] = cvalue
            cvalue.value.add(value)
            
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

    def hash(self, key, timeout = 0):
        raise NotImplementedError
    
    def unordered_set(self, key, timeout = 0):
        raise NotImplementedError
    
    def map(self, key, timeout = 0):
        raise NotImplementedError

