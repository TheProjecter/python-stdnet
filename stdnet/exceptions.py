
class StdNetException(Exception):
    '''A general StdNet exception'''
    pass

class ModelNotRegistered(StdNetException):
    '''Raised when trying to save an instance of a Model not registered with a backend database.'''
    pass

class ObjectNotValidated(StdNetException):
    '''Raised when an instance of a Model fails to validate (there are missing fields which are required).'''
    pass

class ImproperlyConfigured(StdNetException):
    "stdnet is somehow improperly configured"
    pass

class BadCacheDataStructure(StdNetException):
    pass

class FieldError(StdNetException):
    pass

class QuerySetError(StdNetException):
    pass