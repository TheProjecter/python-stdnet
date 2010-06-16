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
            self.required = required
            if unique:
                self.index = True
            else:
                self.index = index
        self.ordered  = ordered
        self.value    = None
        self.obj      = None
        self.meta     = None
        self.name     = None   
        
    def register_with_model(self, model):
        '''Called by the model meta class when the model class is created'''
        pass
    
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
    
    def _cleanvalue(self):
        return self.value
        
    def getkey(self,obj,value):
        pass
        
    def set(self,obj,value):    
        keyname = self.getkey(obj,value)
        raise NotImplementedError('Cannot set the field')
    
    def save(self, commit):
        '''Save the field and the index for object *obj*'''
        name    = self.name
        obj     = self.obj
        meta    = self.meta
        value   = self._cleanvalue()
        if self.required and not value:
            raise FieldError('Field %s for %s has no value' % (name,obj))
        
        if self.primary_key:
            key = meta.basekey()
            setattr(obj,name,value)
            return meta.cursor.add_object(key,obj,commit)
        
        elif self.index:
            key     = meta.basekey(name,value)
            if self.unique:
                return meta.cursor.add_string(key, obj.id, commit, timeout = meta.timeout)
            elif self.ordered:
                raise NotImplementedError
            else:
                return meta.cursor.add_index(key, obj.id, commit, timeout = meta.timeout)
        
            self.savevalue(value)
        
    def savevalue(self, value):
        pass
    
    def add(self, *args, **kwargs):
        raise NotImplementedError("Cannot add to field")
    
    
class AutoField(Field):
    
    def _cleanvalue(self):
        if not self.value:
            meta = self.meta
            self.value = meta.cursor.incr(meta.basekey('ids'))
        return self.value
            

class AtomField(Field):
    
    def set(self,obj,value):
        pass


class DateField(Field):
    
    def _cleanvalue(self):
        dte = self.value
        if dte:
            return int(time.mktime(dte.timetuple()))



class RelatedManager(object):
    
    def __init__(self, related):
        self.related = related


class ForeignKey(Field):
    
    def __init__(self, model, related_name = None, **kwargs):
        self.model = model
        self.related_name = related_name
        super(ForeignKey,self).__init__(**kwargs)
        
    def register_with_model(self, model):
        name = self.related_name or '%s_set' % model._meta.name
        setattr(self.model,name,RelatedManager(model))
    
    def getkey(self,obj,value):
        pass
        
    def set(self,obj,value):
        pass
    
    def _cleanvalue(self):
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
            key     = meta.basekey('id',value)
            value   = meta.cursor.get(key)
        return value
    
    
        