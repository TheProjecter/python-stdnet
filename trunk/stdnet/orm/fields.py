import time
from stdnet.exceptions import FieldError

__all__ = ['Field',
           'AutoField',
           'AtomField',
           'DateField',
           'ForeignKey',
           '_novalue']

class NoValue(object):
    pass

_novalue = NoValue()

class Field(object):
    
    def __init__(self, unique = False, ordered = False, primary_key = False,
                 required = True, index = True):
        self.primary_key = primary_key
        if primary_key:
            self.unique   = True
            self.required = True
            self.index    = True
        else:
            self.unique = unique
            if unique:
                self.index = True
            else:
                self.index = index
        self.required = required
        self.ordered  = ordered
        self.value    = None
        self.obj      = None
        self.meta     = None
        self.name     = None       
    
    def set_model_value(self, name, obj, value = _novalue):
        self.obj  = obj
        self.name = name
        self.meta = obj._meta
        if value is not _novalue:
            self.value = value
        return self.value
    
    def model_get_arg(self):
        return self.value
    
    def get_model_value(self, name, obj, value = _novalue):
        return self.value
    
    def get_value(self, name, obj):
        return self.value
    
    def _cleanvalue(self, basekey, obj, cache):
        return self.value
        
    def getkey(self,obj,value):
        pass
        
    def set(self,obj,value):    
        keyname = self.getkey(obj,value)
        raise NotImplementedError('Cannot set the field')
    
    def save(self,name,obj):
        '''Save the field and the index for object *obj*'''
        meta    = obj._meta
        cache   = meta.cache
        basekey = meta.basekey(name)
        value   = self._cleanvalue(basekey,obj,cache)
        if self.required and not value:
            raise FieldError('Field %s for %s has no value' % (name,obj))
        key     = '%s:%s' % (basekey,value)
        if self.primary_key:
            setattr(obj,name,value)
            cache.set(key,obj)            
        elif self.unique:
            cache.set(key,obj.id)
        elif self.ordered:
            cache.zadd(key,obj.id)
        else:
            cache.sadd(key,obj.id)
        self.savevalue(value)
        
    def savevalue(self, value):
        pass
    
    def add(self, *args, **kwargs):
        raise NotImplementedError("Cannot add to field")
    
    
class AutoField(Field):
    
    def _cleanvalue(self, basekey, obj, cache):
        if not self.value:
            self.value = cache.incr(basekey)
        return self.value
            

class AtomField(Field):
    
    def set(self,obj,value):
        pass


class DateField(Field):
    
    def _cleanvalue(self, basekey, obj, cache):
        dte = self.value
        if dte:
            return int(time.mktime(dte.timetuple()))


class ForeignKey(Field):
    
    def __init__(self, model, **kwargs):
        self.model = model
        super(ForeignKey,self).__init__(**kwargs)
    
    def getkey(self,obj,value):
        pass
        
    def set(self,obj,value):
        pass
    
    def _cleanvalue(self, basekey, obj, cache):
        if isinstance(self.value,self.model):
            return self.value.id
        else:
            return self.value
    
    def set_model_value(self, name, obj, value = _novalue):
        value = super(ForeignKey,self).set_model_value(name, obj, value)
        if value is not _novalue:
            if isinstance(value,self.model):
                self.value = value.id
            else:
                self.value = value
                value = _novalue
        else:
            value = self.value
        return value
    
    def model_get_arg(self):
        return self.value
        
    def get_model_value(self, name, obj, value = _novalue):
        if value == _novalue:
            value = self.value
            
        if isinstance(value,self.model):
            self.value = value.id
        else:
            meta    = self.model._meta
            cache   = meta.cache
            key     = meta.basekey('id',value)
            value   = cache.get(key)
        return value
    
    
class OrderedDictionaryField(Field):
    
    def __init__(self):
        super(TimeSerieField,self).__init__(ordered = True, required = False)
    
    def set_model_value(self, name, obj, value = _novalue):
        if value == _novalue:
            value = self
        return value
    
    def add(self, key, value):
        pass
        