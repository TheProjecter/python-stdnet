from stdnet.exceptions import QuerySetError


class QuerySet(object):
    '''Class used to build querysets'''
    def __init__(self, meta, kwargs):
        self._meta  = meta
        self.kwargs = kwargs
        self._seq   = None
        
    def __repr__(self):
        if self._seq is None:
            return '%s(%s)' % (self.__class__.__name__,self.kwargs)
        else:
            return str(self._seq)
    
    def __str__(self):
        return self.__repr__()
    
    def get(self, index):
        return self._unwind()[index]
    __getitem__ = get
    
    def filter(self,**kwargs):
        kwargs.update(self.kwargs)
        return self.__class__(self._meta,kwargs)
    
    def getid(self, id):
        meta = self._meta
        return meta.cursor.hash(meta.basekey()).get(id)
    
    def __len__(self):
        return len(self._unwind())
    
    def aggregate(self):
        '''Aggregate query results'''
        unique  = False
        meta    = self._meta
        result  = []
        for name,value in self.kwargs.items():
            if name == 'id':
                unique = True
                result = self.getid(value)
                break
            field = meta.fields.get(name,None)
            if not field:
                raise QuerySetError("Field %s not defined" % name)
            value = field.get_value(value)
            if field.unique:
                unique = True
                id = meta.cursor.get(meta.basekey(name,value))
                result = self.getid(id)
                break
            elif field.index:
                result.append(meta.basekey(name,value))
            else:
                raise ValueError("Field %s is not an index" % name)
        return unique, result
    
    def get(self):
        unique,result = self.aggregate()
        if not unique:
            raise QuerySetError('Queryset not unique')
        return result
        
    def items(self):
        meta = self._meta
        if not self.kwargs:
            hash = meta.cursor.hash(meta.basekey())
            for val in hash.values():
                yield val
        else:
            unique,result = self.aggregate()
            if unique:
                yield result
            else:
                meta = self._meta
                ids = meta.cursor.sinter(result)
                objs = meta.cursor.hash(meta.basekey()).mget(ids)
                for obj in objs:
                    yield obj
    
    def __iter__(self):
        return self._unwind().__iter__()
    
    def _unwind(self):
        if self._seq is None:
            self._seq = list(self.items())
        return self._seq
    
    def delete(self):
        '''Delete all the element in the queryset'''
        T = 0
        for el in self:
            T += el.delete()
        return T
    