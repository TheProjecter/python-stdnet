import unittest

from stdnet.main import get_cache


class MemCached(unittest.TestCase):
    keyset1      = 'stdnet-test-set'
    keysetDelete = 'stdnet-test-set-delete'
    keyset2      = 'stdnet-test-set2'
    
    def setUp(self):
        self.cache = get_cache('memcached://127.0.0.1:11211/?timeout=10')
    
    def testSet(self):
        cache = self.cache
        key   = self.keyset1
        self.assertEqual(cache.sadd(key,'first-entry'),1)
        self.assertEqual(cache.sadd(key,'another one'),2)
        self.assertEqual(cache.sadd(key,'the third one'),3)
        data = [d for d in cache.sinter(key)]
        self.assertEqual(len(data),3)
        self.assertEqual(cache.sadd(key,'first-entry'),3)
        
    def testDelete(self):
        cache = self.cache
        key   = self.keysetDelete
        self.assertEqual(cache.sadd(key,'first-entry'),1)
        self.assertEqual(cache.sadd(key,'second-entry'),2)
        a = cache.delete(key)
        b = 1
        
    def _testBadSet(self):
        cache = self.cache
        key   = self.keyset2
        self.assertTrue(cache.add(key,'bla'))
        cache.sadd(key,'bla2')
        
        
    def tearDown(self):
        cache = self.cache
        cache.delete(self.keyset1)
        cache.delete(self.keyset2)
        