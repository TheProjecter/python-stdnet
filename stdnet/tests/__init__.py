#from odict import *
#from backend_tests import *

from tables import *
from fktest import *
from datefield import *
from listfield import *
from ordered_set import *
#from stdnet.contrib.timeserie.tests import *

# Test For redis back-end
from stdnet import orm
from examples.twitter import User, Post
if orm.register(User) == 'redis':
    orm.register(Post)
    from redis_twitter import TestTwitter