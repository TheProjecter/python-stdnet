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
    '''A database model metaclass contains all the information which relates a python class to a database model.
    An instance is initiated when registering a new model with a database backend:

    * *model* a subclass of :ref:`StdModel <model-model>`
    * *fields* dictionary of field instances
    * *abstract* if True, it represents an abstract model and no database elements are created.
    * *keyprefix* prefix for the database table (by default 'stdnet')
'''
    def __init__(self, model, fields, abstract = False, keyprefix = None):
        self.abstract  = abstract
        self.keyprefix = keyprefix
        self.model     = model
        self.name      = model.__name__.lower()
        self.fields    = fields
        self.related   = {}
        model._meta    = self
        if not abstract:
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
        '''primary key field'''
        return self.fields['id']
    
    @property
    def id(self):
        '''primary key value'''
        return self.pk.get_value()
    
    def has_pk(self):
        return self.pk._value
        
    def basekey(self, *args):
        '''Calculate the key to access model hash-table, and model filters in the database.
        For example::
        
            >>> a = Author(name = 'Dante Alighieri').save()
            >>> a.meta.basekey()
            'stdnet:author'
            '''
        key = '%s%s' % (self.keyprefix,self.name)
        for arg in args:
            key = '%s:%s' % (key,arg)
        return key
    
    @property
    def uniqueid(self):
        '''Unique id for an instance. This is unique across multiple model types.'''
        return self.basekey(self.id)
    
    def table(self):
        '''Return an instance of :ref:`HashTable <hash-structure>` holding
        the model table'''
        return self.cursor.hash(self.basekey())
    
    def isvalid(self):
        valid = True
        for field in self.fields.itervalues():
            try:
                valid = valid & field.isvalid()
            except FieldError:
                valid = False
        return valid
    
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
    