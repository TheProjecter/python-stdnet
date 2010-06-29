import copy
from fields import Field, AutoField
from stdnet.exceptions import *

def get_fields(bases, attrs):
    fields = {}
    for base in bases:
        if hasattr(base, '_meta'):
            fields.update(base._meta.fields)
    
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
        self.related   = {}
        model._meta    = self
        if not self.abstract:
            try:
                pk = self.pk
            except:
                fields['id'] = AutoField(primary_key = True)
            if not self.pk.primary_key:
                raise FieldError("Primary key must be named id")
            
        for name,field in self.fields.items():
            if not abstract:
                field.register_with_model(name,model)
            if name == 'id':
                continue
            if field.primary_key:
                raise FieldError("Primary key already available %s." % name)
            
        self.cursor = None
        self.keys  = None
        
    @property
    def pk(self):
        return self.fields['id']
    
    @property
    def id(self):
        return self.pk.value
    
    def has_pk(self):
        return self.pk.value
        
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
        '''Delete the object from the back-end database'''
        if not self.has_pk():
            raise StdNetException('Cannot delete object. It was never saved.')
        # Gather related objects to delete
        objs = self.related_objects()
        T = 0
        for obj in objs:
            T += obj.delete()
        return T + self.cursor.delete_object(self)
    
    def related_objects(self):
        objs = []
        for rel in self.related.itervalues():
            objs.extend(rel.all())
        return objs
                
                            
    def __deepcopy__(self, memodict):
        # We deep copy on fields and create the keys list
        obj = copy.copy(self)
        obj.fields = copy.deepcopy(self.fields, memodict)
        obj.related = copy.deepcopy(self.related, memodict)
        memodict[id(self)] = obj
        return obj



class DataMetaClass(type):
    '''StdModel python metaclass'''
    def __new__(cls, name, bases, attrs):
        super_new = super(DataMetaClass, cls).__new__
        parents = [b for b in bases if isinstance(b, DataMetaClass)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        
        # remove the Meta class if present
        meta      = attrs.pop('Meta', None)
        # remove and build field list
        fields    = get_fields(bases, attrs)
        # create the new class
        new_class = super_new(cls, name, bases, attrs)
        if meta:
            kwargs   = meta_options(**meta.__dict__)
        else:
            kwargs   = {}
        Metaclass(new_class,fields,**kwargs)
        return new_class
    

def meta_options(abstract = False,
                 keyprefix = None,
                 **kwargs):
    return {'abstract': abstract,
            'keyprefix': keyprefix}
    