'''Two different implementation of a redis::map, a networked
ordered associative container
'''
from stdnet import structures


class Set(structures.Set):
    
    def size(self):
        '''Size of map'''
        return self.cursor.zcard(self.id)
    

class HashTable(structures.HashTable):
    
    def size(self):
        return self.cursor.hlen(self.id)
    
    def get(self, key):
        return self.cursor.hget(self.id,key)
        
    def keys(self, desc = False):
        raise NotImplementedError
    
    def items(self, desc = False):
        keys = self.keys(desc = desc)
        id   = self.id
        r    = self.cursor
        for key in keys:
            yield key,r.hget(id,key)

    def add(self, key, value):
        return self.cursor.hset(self.id,key,value)
    
    def update(self, mapping):
        return self.cursor.hmset(self.id,mapping)
    
    def keys(self):
        return self.cursor.hkeys(self.id)
    
    def items(self):
        res = self.execute_command('HGETALL', self.id)
        loads = self.cursor._res_to_val
        for key,val in result:
            yield key,loads(val)

    def values(self):
        for ky,val in self.items():
            yield val
    
    
class Map(HashTable):
    
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
        kv   = self.cursor.execute_command('HGETALL', self.id)
        keys = self._keys(kv.keys(),desc)
        loads = self.cursor._res_to_val
        for key in keys:
            yield key,loads(kv[str(key)])
    