'''A twitter'''
from datetime import datetime
from itertools import izip
from examples.twitter import User
from stdnet import orm
from stdnet.stdtest import TestBase
from stdnet.utils import populate
from random import randint


NUM_USERS = 100
MIN_FOLLOWERS = 10
MAX_FOLLOWERS = 30

usernames = populate('string',NUM_USERS, min_len = 5, max_len = 20)
passwords = populate('string',NUM_USERS, min_len = 8, max_len = 20)


class TestTwitter(TestBase):

    def setUp(self):
        for username,password in izip(usernames,passwords):
            User(username = username, password = password).save(False)
        User.commit()
    
    def testFollowers(self):
        '''Add followers to a user'''
        users = User.objects.all()
        N = users.count()
        
        # Follow users
        for user in users:
            n = randint(MIN_FOLLOWERS,MAX_FOLLOWERS)
            for tofollow in populate('choice',n, choice_from = users):
                if tofollow.id != user.id:
                    user.following.add(tofollow)
            n = user.following.save()
            self.assertEqual(user.following.size(),n)
        
        # Get a random user
        #id = randint(1,N)
        #user = User.objects.get(id = id)
        # loop over its followers and access user is in the following set of its followers
        #for id in user.followers:
        #    u = User.objects.get(id = id)
        #    self.assertTrue(user in u.following)
            
    def testMessages(self):
        users = User.objects.all()
        N = len(users)
        id = randint(1,N)
        user = User.objects.get(id = id)
        user.newupdate('this is my first message')
        user.newupdate('and this is another one')
        user.updates.save()
        self.assertEqual(user.updates.size(),2)
            
        
            