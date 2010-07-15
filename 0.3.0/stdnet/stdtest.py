import unittest
from stdnet import orm


class TestBase(unittest.TestCase):
    
    def tearDown(self):
        orm.clearall()