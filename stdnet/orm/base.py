import copy
from fields import Field, AutoField

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
    '''Model metaclass contains all the information which relates the python object to
    the database model'''
    
    def __init__(self, model, fields, abstract = False, keyprefix = None):
        self.abstract  = abstract
        self.keyprefix = keyprefix
        self.model     = model
        self.name      = model.__name__.lower()
        self.fields    = fields
        model._meta    = self
        if not self.abstract:
            try:
                pk = self.pk
            except:
                fields['id'] = AutoField(primary_key = True)
            if not self.pk.primary_key:
                raise FieldError("Primary key must be named id")
            
        for name,field in self.fields.items():
            field.register_with_model(model)
            if name == 'id':
                continue
            if field.primary_key:
                raise FieldError("Primary key already available %s." % name)
            
        self.cursor = None
        self.keys  = None
        
    @property
    def pk(self):
        return self.fields['id']
        
    def basekey(self, *args):
        key = '%s%s' % (self.keyprefix,self.name)
        for arg in args:
            key = '%s:%s' % (key,arg)
        return key
    
    def save(self, commit = True):
        res = self.pk.save(commit)
        for name,field in self.fields.items():
            if name is not 'id':
                field.save(commit)
        
    def delete(self):
        if self.keys:
            return self.cursor.delete(*tuple(self.keys))
            
    def __deepcopy__(self, memodict):
        # We deep copy on fields and create the keys list
        obj = copy.copy(self)
        obj.fields = copy.deepcopy(self.fields, memodict)
        obj.keys   = []
        memodict[id(self)] = obj
        return obj        



class DataMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        super_new = super(DataMetaClass, cls).__new__
        parents = [b for b in bases if isinstance(b, DataMetaClass)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        
        # Create the class.
        meta      = attrs.pop('Meta', None)
        new_class = super_new(cls, name, bases, attrs)
        if meta:
            kwargs   = meta_options(**meta.__dict__)
        else:
            kwargs   = {}
        fields           = get_fields(bases, attrs)
        Metaclass(new_class,fields,**kwargs)
        return new_class
    

def meta_options(abstract = False,
                 keyprefix = None,
                 **kwargs):
    return {'abstract': abstract,
            'keyprefix': keyprefix}
    