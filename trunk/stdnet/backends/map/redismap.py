'''Two different implementation of a redis::map, a networked
ordered associative container
'''
from stdnet.interfaces import iMap


class RedisMap(iMap):
    
    def __init__(self, redis, id):
        '''Map instance:
        
            * **redis** instance of redis cache client
            * **id** reference id of map
        '''
        self.id      = id
        self.setkey  = '%s:set' % id
        self.minkey  = '%s:min_key' % id
        self.maxkey  = '%s:max_key' % id
        self.redis   = redis
    
    def size(self):
        '''Size of map'''
        return self.redis.hlen(self.id)
    
    def ids(self):
        return self.id,self.setkey,self.minkey,self.maxkey
    
    def setminmax(self, key):
        return
        r = self.redis
        min_val = r.get(self.minkey)
        if min_val is None: 
            r.set(self.minkey, key)
            r.set(self.maxkey, key)
        elif key < min_val:
            r.set(self.minkey, key)
        else:
            max_val = r.get(self.maxkey)
            if key > max_val:
                r.set(self.maxkey, key)

    def keys(self, desc = False):
        raise NotImplementedError
    
    def values(self, desc = False):
        for key,value in self.items(desc = desc):
            yield value
    
    def items(self, desc = False):
        keys = self.keys(desc = desc)
        id   = self.id
        r    = self.redis
        for key in keys:
            yield key,r.hget(id,key)



class RedisMap1(RedisMap):
    
    def add(self, key, value):
        return self.redis.hset(self.id,key,value)
    
    def update(self, mapping):
        self.redis.hmset(self.id,mapping)
    
    def _keys(self, keys, desc):
        ks = [int(v) for v in keys]
        ks.sort()
        if desc:
            return reversed(ks)
        else:
            return ks
        
    def keys(self, desc = False):
        return self._keys(self.redis.hkeys(self.id),desc)
    
    def items(self, desc = False):
        kv   = self.redis.hgetall(self.id)
        keys = self._keys(kv.keys(),desc)
        for key in keys:
            yield key,kv[str(key)]
            
            
class RedisMap2(RedisMap):
    '''This is twice as slow as  RedisMap1. Do not use it.'''
    def add(self, key, value):
        if self.redis.zadd(self.setkey,key,key):
            self.setminmax(key)
        return self.redis.hset(self.id, key, value)

    def keys(self, desc = False):
        return self.redis.zrange(self.setkey, 0, -1, desc = desc)