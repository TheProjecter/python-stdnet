
from stdnet.backends.base import BaseCache, ImproperlyConfigured, novalue
from stdnet.backends.map.redismap import RedisMap1,RedisMap2

try:
    import redis
except:
    raise ImproperlyConfigured("Redis cache backend requires the 'redis' library. Do easy_install redis")

try:
    import cPickle as pickle
except ImportError:
    import pickle

maptypes = {1:RedisMap1,2:RedisMap2}




class CacheClass(BaseCache):
    
    def __init__(self, server, params, pickler = pickle):
        super(CacheClass,self).__init__(params)
        servs = server.split(':')
        server = servs[0]
        port   = 6379
        if len(server) == 2:
            port = int(servs[1])
        self.pickler         = pickler
        self.params          = params
        self.db              = params.pop('db',0)
        self.default_timeout = params.pop('timeout',0)
        cache                = redis.Redis(host = server, port = port, db = self.db)
        self._cache          = cache
        self.execute_command = cache.execute_command
        self.incr      = cache.incr
        self.sismember = cache.sismember
        self.smembers  = cache.smembers
        self.zlen      = cache.zcard
        self.clear     = cache.flushdb
        self.sinter    = cache.sinter
        
    def _get_memcache_timeout(self, timeout):
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        if timeout is None:
            return self.default_timeout
        return timeout
    
    def set_timeout(self, id, timeout):
        timeout = timeout or self.default_timeout
        if timeout:
            self.cache.execute_command('EXPIRE', id, timeout)
        
    def set(self, id, value, timeout = None):
        value = self._val_to_store_info(value)
        r = self._cache.set(id,value)
        self.set_timeout(id,timeout)
        return r
    
    def get(self, id):
        res = self.execute_command('GET', id)
        return self._res_to_val(res)        
        
    def delete(self, *keys):
        km = ()
        for key in keys:
            km += RedisMap1(self,key).ids()
        return self._cache.delete(*km)
     
    def sadd(self, key, member):
        sadd = self._cache.sadd
        if hasattr(member,'__iter__'):
            for m in member:
                n = sadd(key,m)
            return n
        else:
            return sadd(key,member)
    
    def zadd(self, key, value, score = novalue):
        if score == novalue:
            score = value
        return self._cache.execute_command('ZADD', key, score, value)
        
    def zrange(self, key, start, end, withscores = True):
        res = self._cache.zrangebyscore(key,start,end,withscores=withscores)
        if withscores:
            for v,k in res:
                yield k,v
        else:
            for v in res:
                yield v
    
    
    def unordered_set(self, id):
        return UnorderedSet(self,id)
    
    def map(self, id, typ = 1):
        return maptypes[typ](self._cache,id)
    
    def _val_to_store_info(self, value):
        return self.pickler.dumps(value)
    
    def _res_to_val(self, res):
        if not res:
            return res
        try:
            return self.pickler.loads(res)
        except:
            return res
        