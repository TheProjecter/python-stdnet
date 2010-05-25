
from jflow.core.cache.backends.base import BaseCache, ImproperlyConfigured

try:
    import redis
except:
    raise ImproperlyConfigured("Redis cache backend requires the 'redis-py' library")


class CacheClass(BaseCache):
    
    def __init__(self, server, params):
        super(CacheClass,self).__init__(params)
        servs = server.split(':')
        server = servs[0]
        port   = 6379
        if len(server) == 2:
            port = int(servs[1])
        self._cache = redis.Redis(host = server, port = port, **params)
        
    def sadd(self, key, member):
        '''Add the specified member to the set value stored at key.
        If member is already a member of the set no operation is performed.
        If key does not exist a new set with the specified member as sole member is created.
        If the key exists but does not hold a set value an error is returned. '''
        self._cache.sadd(key,member)