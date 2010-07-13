import copy
from base import DataMetaClass
from fields import _novalue
from stdnet.exceptions import FieldError


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
            setattr(self,name,related)
        
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
                raise AttributeError("object '%s' has not attribute %s" % (self,name))
            
    def __set_field(self, name, field, value):
        if field:
            field.set_value(name,self,value)
        else:
            self.__dict__[name] = value
    
    def save(self, commit = True):
        '''Save the instance to the back-end database. The model must be registered with a backend
    otherwise a ``ModelNotRegistered`` exception will be raised.'''
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
        '''Delete an instance from database. If the instance is not available (it does not have an id) and
``StdNetException`` exception will raise.'''
        return self._meta.delete()
    
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
    
    @property
    def meta(self):
        '''Return an instance of :ref:`Database Metaclass <database-metaclass>`'''
        return self._meta
        
    @property
    def uniqueid(self):
        '''Unique id for an instance. This is unique across multiple model types.'''
        return self._meta.basekey(self.id)
    
    

