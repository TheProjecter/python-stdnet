from stdnet.utils import jsonPickler
from stdnet.backends.base import BaseBackend, ImproperlyConfigured, novalue
from stdnet.backends.structures.structredis import List,Set,OrderedSet,HashTable

try:
    import redis
except:
    raise ImproperlyConfigured("Redis cache backend requires the 'redis' library. Do easy_install redis")


class BackEnd(BaseBackend):
    
    def __init__(self, name, server, params, **kwargs):
        super(BackEnd,self).__init__(name, params, **kwargs)
        servs = server.split(':')
        server = servs[0]
        port   = 6379
        if len(server) == 2:
            port = int(servs[1])
        self.db              = self.params.pop('db',0)
        redispy              = redis.Redis(host = server, port = port, db = self.db)
        self.redispy         = redispy
        self.execute_command = redispy.execute_command
        self.incr            = redispy.incr
        self.clear           = redispy.flushdb
        self.sinter          = redispy.sinter
    
    def set_timeout(self, id, timeout):
        timeout = timeout or self.default_timeout
        if timeout:
            self.execute_command('EXPIRE', id, timeout)
    
    def has_key(self, id):
        return self.execute_command('EXISTS', id)
    
    def set(self, id, value, timeout = None):
        value = self._val_to_store_info(value)
        r = self._cache.set(id,value)
        self.set_timeout(id,timeout)
        return r
    
    def get(self, id):
        return self.execute_command('GET', id)
            
    def delete_indexes(self, obj):
        '''Delete an object from the database'''
        meta  = obj.meta
        objid = obj.id
        for field in meta.fields.itervalues():
            if field.primary_key:
                continue
            if field.index:
                value = field.hash(field.serialize())
                fid   = meta.basekey(field.name,value)
                if field.unique:
                    if not self.execute_command('DEL', fid):
                        raise Exception('could not delete unique index at %s' % fid)
                else:
                    if not self.execute_command('SREM', fid, objid):
                        raise Exception('could not delete index at set %s' % fid)
            field.delete()
        return 1
            
    def query(self, meta, fargs, eargs):
        '''Query a model table'''
        qset = None
        if fargs:
            skeys = [meta.basekey(name,value) for name,value in fargs.iteritems()]
            qset  = self.sinter(skeys)
        if eargs:
            skeys = [meta.basekey(name,value) for name,value in fargs.iteritems()]
            eset  = self.sinter(skeys)
            if not qset:
                qset = set(hash(meta.basekey()).keys())
            return qset.difference(eset)
        else:
            if qset is None:
                return 'all'
            else:
                return qset
    
    def _set_keys(self):
        items = []
        [items.extend(item) for item in self._keys.iteritems()]
        self.execute_command('MSET', *items)
        
    # Data structures
    
    def list(self, *args, **kwargs):
        return List(self, *args, **kwargs)
    
    def unordered_set(self, *args, **kwargs):
        return Set(self, *args, **kwargs)
    
    def ordered_set(self, *args, **kwargs):
        return OrderedSet(self, *args, **kwargs)
    
    def hash(self, *args, **kwargs):
        return HashTable(self, *args, **kwargs)
    
    
