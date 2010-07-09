import copy
from base import DataMetaClass
from fields import _novalue
from stdnet.exceptions import FieldError


class StdModel(object):
    __metaclass__ = DataMetaClass
    
    def __init__(self, **kwargs):
        self._load(kwargs)
        
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self)
    
    def __str__(self):
        return ''
    
    def _load(self, kwargs):
        meta = copy.deepcopy(self.__class__._meta)
        self.__dict__['_meta'] = meta
        for name,field in meta.fields.iteritems():
            value = kwargs.pop(name,_novalue)
            self.setfield(name, field, value)
            
        for name,value in kwargs.items():
            setattr(self,name,value)
        
        for name,related in meta.related.iteritems():
            related.obj = self
            setattr(self,name,related)
        
    def __setattr__(self,name,value):
        field = self._meta.fields.get(name,None)
        self.setfield(name, field, value)
        
    def __getattr__(self,name):
        field = self._meta.fields.get(name,None)
        if field:
            value = self.__dict__.get(name,_novalue)
            if value is _novalue:
                value = field.get_model_value(name,self)
                self.__dict__[name] = value
            return value
        else:
            try:
                return self.__dict__[name]
            except KeyError:
                raise AttributeError("object '%s' has not attribute %s" % (self,name))
            
    def setfield(self, name, field, value):
        if field:
            value = field.set_model_value(name,self,value)
        if value is not _novalue:
            self.__dict__[name] = value
    
    def save(self, commit = True):
        '''Save the instance to the back-end database. The model must be registered with a backend
    otherwise a ModelNotRegistered exception will be raised.'''
        meta  = self._meta.save(commit)
        return self
        
    def __getstate__(self):
        return self.todict()
    
    def __setstate__(self,dict):
        self._load(dict)
        
    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.id == other.id
        else:
            return False
        
    def delete(self):
        return self._meta.delete()
    
    def todict(self):
        odict = self.__dict__.copy()
        meta = odict.pop('_meta')
        for name,field in meta.fields.items():
            val = field.model_get_arg()
            if val is not None:
                odict[name] = val
            else:
                if field.required:
                    raise ValueError("Field %s is required" % name)
                else:
                    odict.pop(name,None)
        return odict
        
    @property
    def uniqueid(self):
        return self._meta.basekey(self.id)
    
    

