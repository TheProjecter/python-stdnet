from stdnet.exceptions import QuerySetError


class QuerySet(object):
    '''Queryset manager'''
    
    def __init__(self, meta, kwargs):
        '''A query set is  initialized with
        
        * *meta* an model instance meta attribute,
        * *kwargs* dictionary of query keys
        '''
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
    
    def count(self):
        '''Return the number of objects in the queryset without fetching objects'''
        raise NotImplementedError
        
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
    

class Manager(object):
    
    def get(self, **kwargs):
        qs = self.filter(**kwargs)
        return qs.get()
    
    def get_or_create(self, **kwargs):
        res = self.get(**kwargs)
        if not res:
            res = self.model(**kwargs)
            res.save()
        return res
    
    def filter(self, **kwargs):
        return QuerySet(self._meta, kwargs)

    def all(self):
        return self.filter()
    
    
class RelatedManager(Manager):
    
    def __init__(self, fieldname, related):
        self.related    = related
        self.fieldname  = fieldname
        self.obj        = None
        
    def filter(self, **kwargs):
        if self.obj:
            kwargs[self.fieldname] = self.obj.id
            return QuerySet(self.related._meta, kwargs)
            #meta = self.related._meta
            #id   = meta.basekey(self.fieldname,self.obj.id)
            #data = meta.cursor.unordered_set(id)
            #hash = meta.cursor.hash(meta.basekey())
            #return hash.mget(data)
    
    def __deepcopy__(self, memodict):
        # We only copy here
        return self.__class__(self.fieldname,self.related)