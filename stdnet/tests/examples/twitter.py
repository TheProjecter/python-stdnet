from datetime import datetime
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
    updates   = orm.ListField(model = Post)
    following = orm.SetField(model = 'self',
                             related_name = 'followers')
    
    def __str__(self):
        return self.username
    
    def newupdate(self, data):
        p  = Post(data = data).save()
        self.updates.push_front(p)
        return p
    
        

    

    

    