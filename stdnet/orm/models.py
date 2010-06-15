import copy
from fields import Field, AutoField, _novalue
from stdnet.exceptions import FieldError



def get_fields(bases, attrs):
    fields = {}
    for base in reversed(bases):
        if hasattr(base, 'orm_fields'):
            fields.update(base.orm_fields)
    
    for name,field in attrs.items():
        if isinstance(field,Field):
            fields[name] = attrs.pop(name)
    
    return fields



class Metaclass(object):
    keyprefix = 'stdnet' 
    
    def __init__(self, model, fields):
        self.model  = model
        self.name   = model.__name__.lower()
        self.fields = fields
        self.pk     = None
        for name,field in self.fields.items():
            if field.primary_key:
                if name == 'id':
                    self.pk = field
                else:
                    raise FieldError("Primary key must be named id, not %s" % name)
        
        if not self.pk:
            self.pk = AutoField(primary_key = True)
            self.fields['id'] = self.pk
        
        self.cache = None
        
    def basekey(self, *args):
        key = '%s:%s' % (self.keyprefix,self.name)
        for arg in args:
            key = '%s:%s' % (key,arg)
        return key
    
    def save(self, obj):
        self.pk.save()
        for name,field in self.fields.items():
            if name is not 'id':
                field.save()
    
    def delete(self, obj):
        
            
    def __deepcopy__(self, memodict):
        # We don't have to deepcopy very much here, since most things are not
        # intended to be altered after initial creation.
        obj = copy.copy(self)
        obj.fields = copy.deepcopy(self.fields, memodict)
        obj.pk = obj.fields['id']
        memodict[id(self)] = obj
        return obj




class DataMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        super_new = super(DataMetaClass, cls).__new__
        fields = get_fields(bases, attrs)
        klass = super_new(cls, name, bases, attrs)
        meta             = Metaclass(klass,fields)
        klass._meta      = meta
        return klass
        
        

class StdModel(object):
    __metaclass__ = DataMetaClass
    
    def __init__(self, **kwargs):
        self._load(kwargs)
    
    def _load(self, kwargs):
        meta = copy.deepcopy(self.__class__._meta)
        self.__dict__['_meta'] = meta
        for name,field in meta.fields.items():
            value = kwargs.pop(name,_novalue)
            self.setfield(name, field, value)
            
        for name,value in kwargs.items():
            setattr(self,name,value)
        
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
            return self.__dict__[name]
            
    def setfield(self, name, field, value):
        if field:
            value = field.set_model_value(name,self,value)
        if value is not _novalue:
            self.__dict__[name] = value
    
    def save(self):
        meta  = self._meta.save(self)
        
    def __getstate__(self):
        odict = self.__dict__.copy()
        meta = odict.pop('_meta')
        for name,field in meta.fields.items():
            val = field.model_get_arg()
            if val:
                odict[name] = val
            else:
                odict.pop(name)
        return odict
    
    def __setstate__(self,dict):
        self._load(dict)
        
    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.id == other.id
        else:
            return False
        
    def delete(self):
        meta  = self._meta.delete(self)
    
        
    

