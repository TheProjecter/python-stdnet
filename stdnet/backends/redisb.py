
from stdnet.backends.base import BaseCache, ImproperlyConfigured, novalue
from stdnet.backends.map.redismap import RedisMap1,RedisMap2

try:
    import redis
except:
    raise ImproperlyConfigured("Redis cache backend requires the 'redis' library. Do easy_install redis")

maptypes = {1:RedisMap1,2:RedisMap2}


class CacheClass(BaseCache):
    
    def __init__(self, server, params):
        super(CacheClass,self).__init__(params)
        servs = server.split(':')
        server = servs[0]
        port   = 6379
        if len(server) == 2:
            port = int(servs[1])
        self.params = params
        self.db     = params.pop('db',0)
        cache       = redis.Redis(host = server, port = port, db = self.db)
        self._cache = cache
        self.set    = cache.set
        self.get       = cache.get
        self.incr      = cache.incr
        self.sismember = cache.sismember
        self.smembers  = cache.smembers
        self.zlen      = cache.zcard
        self.hset      = cache.hset
        self.hlen      = cache.hlen
        self.hkeys     = cache.hkeys
    
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
    
    # Map
    def map(self, id, typ = 1):
        return maptypes[typ](self._cache,id)
    