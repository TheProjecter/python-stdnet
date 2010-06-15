from stdnet.main import get_cache
from stdnet.conf import settings


class QuerySet(object):
    
    def __init__(self, meta, kwargs):
        self._meta  = meta
        self.kwargs = kwargs
        
    def filter(self,**kwargs):
        self.kwargs.update(kwargs)
        
    def __iter__(self):
        skeys = []
        meta  = self._meta
        for v in self.kwargs.items():
            skeys.append(meta.basekey(*v))
        ids = meta.cache.sinter(skeys)
        for id in ids:
            key = meta.basekey('id',id)
            yield meta.cache.get(key)
    


class Manager(object):
    
    def getid(self, id):
        '''retrive object form id'''
        key = self._meta.basekey('id',id)
        return self.cache.get(key)
    
    def filter(self, **kwargs):
        return QuerySet(self._meta, kwargs)           
         
        


def clear(backend = None):
    backend = backend or settings.DEFAULT_BACKEND
    cache = get_cache(backend)
    cache.clear()

def register(model, backend = None, keyprefix = None, namespace = None):
    backend = backend or settings.DEFAULT_BACKEND
    prefix  = keyprefix or model._meta.keyprefix or 'stdnet'
    meta    = model._meta
    meta.keyprefix = prefix
    objects = getattr(model,'objects',None)
    if not objects:
        objects = Manager()
        model.objects = objects
    meta.cache = get_cache(backend)
    objects.model = model
    objects._meta = meta
    objects.cache = meta.cache
    

_registry = {}