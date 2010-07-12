.. _twitter-example:

A very simple twitter clone implemented using stdnet library::

	from stdnet import orm
	
	class Post(orm.StdModel):
    
	    def __init__(self, data = ''):
	        self.dt   = datetime.now()
	        self.data = data
	        super(Post,self).__init__()

	class User(orm.StdModel):
	    '''A model for holding information about users'''
	    username  = orm.AtomField(unique = True)
	    password  = orm.AtomField()
	    updates   = orm.ListField()
	    following = orm.SetField()
	    followers = orm.SetField()
	    
	    def __str__(self):
	        return self.username
	    
	    def newupdate(self, data):
	        p  = Post(data = data).save()
	        self.updates.push_front(p.id)
	        return p
	    
	    def follow(self, user):
	        '''Follow a user'''
	        self.following.add(user)
	        user.followers.add(self)
	        self.following.save()
	        user.followers.save()