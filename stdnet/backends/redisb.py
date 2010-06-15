
from stdnet.backends.base import BaseCache, ImproperlyConfigured, novalue

try:
    import redis
except:
    raise ImproperlyConfigured("Redis cache backend requires the 'redis' library. Do easy_install redis")



class RedisMap(object):
    
    def __init__(self, id):
        self.id      = id
        self.setkey  = '%s:set' % id
        self.hashkey = id
        self.minkey  = '%s:min_key' % id
        self.maxkey  = '%s:max_key' % id
    
    def len(self, redis):
        return redis.zcard(self.setkey)
    
    def keys(self):
        return self.id,self.hashkey,self.setkey,self.minkey,self.maxkey
    
    def add(self, redis, key, value):
        if redis.zadd(self.setkey,key,key):
            min_val = redis.get(self.minkey)
            if min_val is None: 
                redis.set(self.minkey, key)
                redis.set(self.maxkey, key)
            elif key < min_val:
                redis.set(self.minkey, key)
            else:
                max_val = redis.get(self.maxkey)
                if key > max_val:
                    redis.set(self.maxkey, key)        
        return redis.hset(self.hashkey, key, value)

    def range(self, redis, start = 0, end = -1, desc = False):
        keys   = redis.zrange(self.setkey, start, end, desc = desc)
        hashid = self.hashkey
        for key in keys:
            yield key,redis.hget(hashid,key)


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
    
    def delete(self, *keys):
        km = ()
        for key in keys:
            km += RedisMap(key).keys()
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
    def madd(self, id, key, value):
        return RedisMap(id).add(self._cache,key,value)
    
    def mlen(self, id):
        return RedisMap(id).len(self._cache)
    
    def mrange(self, id, start = 0, end = -1, desc = False):
        return RedisMap(id).range(self._cache, start, end, desc = desc)
