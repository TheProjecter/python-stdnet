
from stdnet.backends.base import BaseCache, ImproperlyConfigured

try:
    import redis
except:
    raise ImproperlyConfigured("Redis cache backend requires the 'redis' library. Do easy_install redis")


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
        self.get    = cache.get
        self.delete = cache.delete
        self.sismember = cache.sismember
        self.smembers  = cache.smembers
        self.zlen      = cache.zcard
    
    def sadd(self, key, member):
        '''Add the specified member to the set value stored at key.
        If member is already a member of the set no operation is performed.
        If key does not exist a new set with the specified member as sole member is created.
        If the key exists but does not hold a set value an error is returned. '''
        sadd = self._cache.sadd
        if hasattr(member,'__iter__'):
            for m in member:
                n = sadd(key,m)
            return n
        else:
            return sadd(key,member)
    
    def zadd(self, key, value):
        return self._cache.format_bulk('ZADD', key, value, value)
        
    def zrange(self, key, start, end, withscores = True):
        res = self._cache.zrangebyscore(key,start,end,withscores=withscores)
        if withscores:
            for v,k in res:
                yield k,v
        else:
            for v in res:
                yield v
    
    