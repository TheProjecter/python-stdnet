from stdnet.main import get_cache
from stdnet.conf import settings


class Manager(object):
    
    def filter(self, **kwargs):
        pass
    
    def getid(self, id):
        '''retrive object form id'''
        key = self._meta.basekey('id',id)
        return self.cache.get(key)
        


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