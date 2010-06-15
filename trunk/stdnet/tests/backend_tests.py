import unittest
from itertools import izip

from stdnet.main import get_cache
from stdnet.utils import populate, date2timestamp, OrderedDict
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
         
    def testMap(self):
        cache  = self.cache
        id     = self.keyordered
        keys   = populate('date',100)
        values = populate('float',100)
        d      = OrderedDict()
        for k,v in izip(keys,values):
            ts = date2timestamp(k)
            d[ts] = v
            cache.madd(id,ts,v)
        
        self.assertTrue(cache.mlen(id)>0)
        self.assertEqual(cache.mlen(id),len(d))
        kp = None
        for k,v in cache.mrange(id):
            k = int(k)
            v = float(v)
            if kp is not None:
                self.assertTrue(k>kp)
            vd = d[k]
            self.assertAlmostEqual(v,vd)
            kp = k
        
        
    def tearDown(self):
        cache = self.cache
        cache.delete(self.keyset1,self.keyset2,self.keyordered)


cache_memcached = get_cache(settings_test.memcached)

if available(cache_memcached) and False:    
    class testMemcached(testLocMem):
        cache = cache_memcached
        

cache_redis = get_cache(settings_test.redis)

if available(cache_redis):
    
    class testRedis(testLocMem):
        cache = cache_redis
    
    
