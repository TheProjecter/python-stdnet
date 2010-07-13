from stdnet.exceptions import QuerySetError


class svset(object):
    
    def __init__(self, result):
        self.result = result
        
    def __len__(self):
        return 1
    


class QuerySet(object):
    '''Queryset manager'''
    
    def __init__(self, meta, fargs = None, eargs = None):
        '''A query set is  initialized with
        
        * *meta* an model instance meta attribute,
        * *fargs* dictionary containing the lookup parameters to include.
        * *eargs* dictionary containing the lookup parameters to exclude.
        '''
        self._meta  = meta
        self.fargs  = fargs
        self.eargs  = eargs
        self.qset   = None
        self._count = None
        self._seq   = None
        
    def __repr__(self):
        if self._seq is None:
            s = self.__class__.__name__
            if self.fargs:
                s = '%s.filter(%s)' % (s,self.fargs)
            if self.eargs:
                s = '%s.exclude(%s)' % (s,self.eargs)
            return s
        else:
            return str(self._seq)
    
    def __str__(self):
        return self.__repr__()
    
    def get(self, index):
        return self._unwind()[index]
    __getitem__ = get
    
    def filter(self,**kwargs):
        '''Returns a new ``QuerySet`` containing objects that match the given lookup parameters.'''
        kwargs.update(self.fargs)
        return self.__class__(self._meta,fargs=kwargs,eargs=self.eargs)
    
    def exclude(self,**kwargs):
        '''Returns a new ``QuerySet`` containing objects that do not match the given lookup parameters.'''
        kwargs.update(self.eargs)
        return self.__class__(self._meta,fargs=self.fargs,eargs=kwargs)
    
    #def getid(self, id):
    #    meta = self._meta
    #    return meta.cursor.hash(meta.basekey()).get(id)
    
    def count(self):
        '''Return the number of objects in the queryset without fetching objects'''
        self.buildquery()
        if self.qset == 'all':
            meta = self._meta
            return meta.cursor.hash(meta.basekey()).size()
        else:
            return len(self.qset)
        
    def __len__(self):
        return self.count()
    
    def buildquery(self):
        if self.qset is not None:
            return
        meta = self._meta
        unique, fargs = self.aggregate(self.fargs)
        if unique:
            self.qset = svset(meta.cursor.get_object(meta, fargs[0], fargs[1]))
        else:
            if self.eargs:
                unique, eargs = self.aggregate(self.eargs, False)
            else:
                eargs = None
            self.qset = self._meta.cursor.query(meta, fargs, eargs)
        
    def aggregate(self, kwargs, filter = True):
        '''Aggregate query results'''
        unique  = False
        meta    = self._meta
        result  = {}
        for name,value in kwargs.items():
            unique = True
            if name is not 'id':
                field = meta.fields.get(name,None)
                if not field:
                    raise QuerySetError("Could not filter. Field %s not defined." % name)
                value = field.get_value(value)
                unique = field.unique
            if unique:
                result[name] = value
                if filter:
                    result = name,value
                    unique = True
                    break
                else:
                    result[name] = value   
            elif field.index:
                result[name] = value
            else:
                raise ValueError("Field %s is not an index" % name)
        return unique, result
    
    def aggregate_(self, kwargs):
        '''Aggregate query results'''
        unique  = False
        meta    = self._meta
        result  = []
        for name,value in kwargs.items():
            if name == 'id':
                unique = True
                result = self.getid(value)
                break
            field = meta.fields.get(name,None)
            if not field:
                raise QuerySetError("Could not filter. Field %s not defined." % name)
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
        self.buildquery()
        if len(self.qset) == 1:
            try:
                return self.qset.result
            except:
                id = tuple(self.qset)[0]
                meta = self._meta
                return meta.cursor.hash(meta.basekey()).get(id)
        else:
            raise QuerySetError('Get query yielded non unique results')
        
    def items(self):
        self.buildquery()
        meta = self._meta
        ids = self.qset
        if isinstance(ids,svset):
            yield ids.result
        else:
            hash = meta.cursor.hash(meta.basekey())
            if ids == 'all':
                for val in hash.values():
                    yield val
            else:
                objs = meta.cursor.hash(meta.basekey()).mget(ids)
                for obj in objs:
                    yield obj
    
    def __iter__(self):
        if self._seq is not None:
            for item in self._seq:
                yield item
        else:
            seq  = []
            self._seq = seq
            for item in self.items():
                seq.append(item)
                yield item
    
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
        return QuerySet(self._meta, fargs = kwargs)
    
    def exclude(self, **kwargs):
        return QuerySet(self._meta, eargs = kwargs)

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


class ManyToManyRelatedManager(RelatedManager):
    
    def __init__(self, fieldname, related):
        self.related    = related
        self.fieldname  = fieldname
        self.obj        = None
        
    def filter(self, **kwargs):
        if self.obj:
            kwargs[self.fieldname] = self.obj.id
            return QuerySet(self.related._meta, kwargs)
    
    
    