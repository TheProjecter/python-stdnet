'''Two different implementation of a redis::map, a networked
ordered associative container
'''
from stdnet import structures


class List(structures.List):
    
    def size(self):
        '''Size of map'''
        return self.cursor.execute_command('LLEN', self.id)
    
    def push_back(self, values):
        for value in values:
            self.cursor.execute_command('RPUSH', self.id, self.cursor._res_to_val(value))
    
    def push_front(self, values):
        for value in values:
            self.cursor.execute_command('LPUSH', self.id, self.cursor._res_to_val(value))
    
    def pop_back(self):
        return self.cursor._res_to_val(self.cursor.execute_command('RPOP', self.id))
    
    def pop_front(self):
        return self.cursor._res_to_val(self.cursor.execute_command('LPOP', self.id))
    
    def _all(self):
        return self.cursor.execute_command('LRANGE', self.id, 0, -1)
        

class Set(structures.Set):
    
    def size(self):
        '''Size of set'''
        return self.cursor.execute_command('SCARD', self.id)
    
    def add(self, value):
        return self.cursor.execute_command('SADD', self.id, value)
    
    def _all(self):
        return self.cursor.execute_command('SMEMBERS', self.id)
    

class HashTable(structures.HashTable):
    
    def size(self):
        return self.cursor.hlen(self.id)
    
    def get(self, key):
        return self.cursor.hget(self.id,key)
    
    def mget(self, keys):
        '''Get multiple keys'''
        if not keys:
            raise StopIteration
        objs = self.cursor.execute_command('HMGET', self.id, *keys)
        loads = self.cursor._res_to_val
        for obj in objs:
            yield loads(obj)
    
    def add(self, key, value):
        return self.cursor.hset(self.id,key,value)
    
    def update(self, mapping):
        return self.cursor.hmset(self.id,mapping)
    
    def delete(self, key):
        return self.cursor.execute_command('HDEL', self.id, key)
    
    def keys(self):
        return self.cursor.execute_command('HKEYS', self.id)
    
    def items(self):
        result = self.cursor.execute_command('HGETALL', self.id)
        loads  = self.cursor._res_to_val
        for key,val in result.iteritems():
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
        ks = super(Map,self).keys()
        return self._keys(ks,desc)

    def items(self, desc = False):
        kv   = self.cursor.execute_command('HGETALL', self.id)
        keys = self._keys(kv.keys(),desc)
        loads = self.cursor._res_to_val
        for key in keys:
            yield key,loads(kv[str(key)])
    