'''Thread-safe in-memory cache backend.
'''

import time
try:
    import cPickle as pickle
except ImportError:
    import pickle

from siro.core.cache.backends.base import BaseCache
from siro.core.cache.utils import RWLock


class dummyPickle():
    
    def loads(self, data):
        return data

    def dumps(self, obj):
        return obj

class CacheClass(BaseCache):
    
    def __init__(self, _, params):
        super(CacheClass,self).__init__(params)
        try:
            dopickle = int(params.get('pickle', 1))
        except:
            dopickle = 1
        if dopickle:
            self.pickle = pickle
        else:
            self.pickle = dummyPickle()
        self._cache = {}
        self._expire_info = {}
        max_entries = params.get('max_entries', 300)
        try:
            self._max_entries = int(max_entries)
        except (ValueError, TypeError):
            self._max_entries = 300

        cull_frequency = params.get('cull_frequency', 3)
        try:
            self._cull_frequency = int(cull_frequency)
        except (ValueError, TypeError):
            self._cull_frequency = 3

        self._lock = RWLock()

    def add(self, key, value, timeout=None):
        self._lock.writer_enters()
        try:
            exp = self._expire_info.get(key)
            if exp is None or exp <= time.time():
                try:
                    self._set(key, self.pickle.dumps(value), timeout)
                    return True
                except pickle.PickleError:
                    pass
            return False
        finally:
            self._lock.writer_leaves()

    def get(self, key, default=None):
        self._lock.reader_enters()
        try:
            exp = self._expire_info.get(key)
            if exp is None:
                return default
            elif exp == 0 or exp > time.time():
                try:
                    return self.pickle.loads(self._cache[key])
                except pickle.PickleError:
                    return default
        finally:
            self._lock.reader_leaves()
        self._lock.writer_enters()
        try:
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return default
        finally:
            self._lock.writer_leaves()

    def _set(self, key, value, timeout=None):
        if len(self._cache) >= self._max_entries:
            self._cull()
        if timeout is None:
            timeout = self.default_timeout
        self._cache[key] = value
        if not timeout:
            self._expire_info[key] = 0
        else:
            self._expire_info[key] = time.time() + timeout

    def set(self, key, value, timeout=None):
        self._lock.writer_enters()
        # Python 2.3 and 2.4 don't allow combined try-except-finally blocks.
        try:
            try:
                self._set(key, self.pickle.dumps(value), timeout)
            except pickle.PickleError:
                pass
        finally:
            self._lock.writer_leaves()

    def has_key(self, key):
        self._lock.reader_enters()
        try:
            exp = self._expire_info.get(key)
            if exp is None:
                return False
            elif exp > time.time():
                return True
        finally:
            self._lock.reader_leaves()

        self._lock.writer_enters()
        try:
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return False
        finally:
            self._lock.writer_leaves()

    def _cull(self):
        if self._cull_frequency == 0:
            self.clear()
        else:
            doomed = [k for (i, k) in enumerate(self._cache) if i % self._cull_frequency == 0]
            for k in doomed:
                self._delete(k)

    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass
        try:
            del self._expire_info[key]
        except KeyError:
            pass

    def delete(self, key):
        self._lock.writer_enters()
        try:
            self._delete(key)
        finally:
            self._lock.writer_leaves()

    def clear(self):
        self._cache.clear()
        self._expire_info.clear()
        
    # Sets            
        
    def sadd(self, key, members):
        sset = self.get(key)
        if sset is None:
            sset = set()
        if not hasattr(members,'__iter__'):
            members = [members]
        for member in members:
            sset.add(member)
        self.set(key,sset)
        return len(sset)
    
    def sinter(self,key):
        return self.get(key)
    