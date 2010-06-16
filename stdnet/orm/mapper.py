from stdnet.main import getdb
from stdnet.conf import settings

from query import QuerySet
    

class Manager(object):
    
    def get(self, **kwargs):
        qs = self.filter(**kwargs)
        return qs.get()
    
    def filter(self, **kwargs):
        return QuerySet(self._meta, kwargs)


def clear(backend = None):
    backend = backend or settings.DEFAULT_BACKEND
    cursor = getdb(backend)
    cursor.clear()


def register(model, backend = None, keyprefix = None, timeout = 0):
    backend = backend or settings.DEFAULT_BACKEND
    prefix  = keyprefix or model._meta.keyprefix or settings.DEFAULT_KEYPREFIX or ''
    if prefix:
        prefix = '%s:' % prefix
    meta    = model._meta
    meta.keyprefix = prefix
    meta.timeout   = timeout or 0
    objects = getattr(model,'objects',None)
    if not objects:
        objects = Manager()
        model.objects = objects
    meta.cursor    = getdb(backend)
    objects.model  = model
    objects._meta  = meta
    objects.cursor = meta.cursor
    

_registry = {}
