import unittest
from itertools import izip

from stdnet.main import get_cache
from stdnet.utils import populate
from stdnet import settings_test

def available(cache):
    cache.set("stdnet-test",1)
    avail = cache.get("stdnet-test") or False
    cache.delete("stdnet-test")
    return avail

class testLocMem(unittest.TestCase):
    cache        = get_cache('locmem://?timeout=300')
    keyset1      = 'stdnet-test-set'
    keyset2      = 'stdnet-test-set2'
    keyordered   = 'stdnet-test-ordered'
    
    def setUp(self):
        pass
    
    def testSet(self):
        cache = self.cache
        key   = self.keyset1
        self.assertTrue(cache.sadd(key,'first-entry'))
        self.assertTrue(cache.sadd(key,'another one'))
        self.assertTrue(cache.sadd(key,'the third one'))
        data = cache.smembers(key)
        self.assertEqual(len(data),3)
        self.assertFalse(cache.sadd(key,'first-entry'))
        
    def testDelete(self):
        cache = self.cache
        key   = self.keyset1
        self.assertTrue(cache.sadd(key,'first-entry'))
        self.assertTrue(cache.sadd(key,'second-entry'))
        a = cache.delete(key)
        b = 1
        
    def _testBadSet(self):
        cache = self.cache
        key   = self.keyset2
        self.assertTrue(cache.add(key,'bla'))
        cache.sadd(key,'bla2')
            
    def testOrdered(self):
        cache = self.cache
        key   = self.keyordered
        cache.zadd(key,'bla')
        cache.zadd(key,'bla')
        self.assertEqual(cache.zlen(key),1)
        
    def testOrdered2(self):
        cache = self.cache
        key   = self.keyordered
        keys  = populate('integer',100,0,10000)
        for k in populate('integer',100,0,10000):
            cache.zadd(key,k)
        
        elems = cache.zrange(key,1000,6000)
        p = 0
        for k in elems:
            if p:
                self.assertTrue(k>p)
            p = k
        
        
    def tearDown(self):
        cache = self.cache
        cache.delete(self.keyset1,self.keyset2,self.keyordered)


cache_memcached = get_cache(settings_test.memcached)

if available(cache_memcached):
        
    class testMemcached(testLocMem):
        cache = cache_memcached
        

cache_redis = get_cache(settings_test.redis)

if available(cache_redis):
    
    class testRedis(testLocMem):
        cache = cache_redis
    
    
