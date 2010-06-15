


class iMap(object):
    
    def add(self, key, value):
        raise NotImplementedError
    
    def size(self):
        raise NotImplementedError
    
    def keys(self, desc = False):
        raise NotImplementedError
    
    def values(self, desc = False):
        raise NotImplementedError

    def items(self, desc = False):
        raise NotImplementedError
        
    def __iter__(self):
        return self.keys().__iter__()
    
    def __len__(self):
        return self.size()