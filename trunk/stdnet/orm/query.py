from stdnet.exceptions import QuerySetError


class QuerySet(object):
    
    def __init__(self, meta, kwargs):
        self._meta  = meta
        self.kwargs = kwargs
        
    def filter(self,**kwargs):
        self.kwargs.update(kwargs)
    
    def getid(self, id):
        meta = self._meta
        return meta.cursor.hash(meta.basekey()).get(id)
        
    def getids(self, *ids):
        pass
    
    def aggregate(self):
        unique  = False
        meta    = self._meta
        result  = []
        for name,value in self.kwargs.items():
            if name == 'id':
                unique = True
                result = self.getid(value)
                break
            field = meta.fields[name]
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
        
    def __iter__(self):
        unique,result = self.aggregate()
        if unique:
            yield result
        else:
            ids = meta.cursor.sinter(skeys)
            for id in ids:
                key = meta.basekey('id',id)
                yield meta.cursor.get(key)