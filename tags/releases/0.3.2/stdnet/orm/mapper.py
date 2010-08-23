import copy
from stdnet.main import getdb as _getdb

from query import Manager    

def clear(backend = None):
    from stdnet.conf import settings
    backend = backend or settings.DEFAULT_BACKEND
    cursor = getdb(backend)
    cursor.clear()
    
def clearall():
    for meta in _registry.values():
        meta.cursor.clear()

def register(model, backend = None, keyprefix = None, timeout = 0):
    from stdnet.conf import settings
    backend = backend or settings.DEFAULT_BACKEND
    prefix  = keyprefix or model._meta.keyprefix or settings.DEFAULT_KEYPREFIX or ''
    if prefix:
        prefix = '%s:' % prefix
    meta           = model._meta
    meta.keyprefix = prefix
    meta.timeout   = timeout or 0
    objects = getattr(model,'objects',None)
    if not objects:
        objects = Manager()
    else:
        objects = copy.copy(objects)
    model.objects    = objects
    meta.cursor      = _getdb(backend)
    objects.model    = model
    objects._meta    = meta
    objects.cursor   = meta.cursor
    _registry[model] = meta
    return meta.cursor.name


def getdb(backend = None, pickler = None):
    from stdnet.conf import settings
    return _getdb(backend or settings.DEFAULT_BACKEND, pickler = pickler)
    

_registry = {}
