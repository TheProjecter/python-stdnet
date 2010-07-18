import copy
from base import DataMetaClass
from fields import _novalue
from stdnet.exceptions import *


class StdModel(object):
    '''A model is the single, definitive source of data
about your data. It contains the essential fields and behaviors
of the data you're storing. Each model maps to a single
database Hash-table.'''

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
            self.__set_field(name, field, value)
            
        for name,value in kwargs.items():
            setattr(self,name,value)
        
        for name,related in meta.related.iteritems():
            related.obj = self
            #setattr(self,name,related)
        
    def __setattr__(self,name,value):
        field = self._meta.fields.get(name,None)
        self.__set_field(name, field, value)
        
    def __getattr__(self, name):
        field = self._meta.fields.get(name,None)
        if field:
            return field.get_full_value()
        else:
            try:
                return self.__dict__[name]
            except KeyError:
                try:
                    return self._meta.related[name]
                except KeyError:
                    return self.customAttribute(name)
        
    def customAttribute(self, name):
        '''Override this function to provide custom attributes'''
        raise AttributeError("object '%s' has not attribute %s" % (self,name))
    
    def __set_field(self, name, field, value):
        if field:
            field.set_value(name,self,value)
        else:
            self.__dict__[name] = value
    
    def save(self, commit = True):
        '''Save the instance to the back-end database. The model must be registered with a backend
    otherwise a ``ModelNotRegistered`` exception will be raised.'''
        meta = self._meta
        if not meta.cursor:
            raise ModelNotRegistered('Model %s is not registered with a backend database. Cannot save any instance.' % meta.name)
        if meta.isvalid():
            meta.cursor.add_object(self, commit = commit)
        else:
            raise ObjectNotValidated('Object %s did not validate. Cannot save to database.' % self)
        return self
    
    def isvalid(self):
        return self.meta.isvalid()
        
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
        '''Delete an instance from database. If the instance is not available (it does not have an id) and
``StdNetException`` exception will raise.'''
        meta = self._meta
        if not meta.has_pk():
            raise StdNetException('Cannot delete object. It was never saved.')
        # Gather related objects to delete
        objs = meta.related_objects()
        T = 0
        for obj in objs:
            T += obj.delete()
        return T + meta.cursor.delete_object(self)
    
    def todict(self):
        odict = self.__dict__.copy()
        meta = odict.pop('_meta')
        for name,field in meta.fields.items():
            val = field.serialize()
            if val is not None:
                odict[name] = val
            else:
                if field.required:
                    raise ValueError("Field %s is required" % name)
                else:
                    odict.pop(name,None)
        return odict
        
    @classmethod
    def commit(cls):
        return cls._meta.cursor.commit()
    
    

