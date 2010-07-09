
class StdNetException(Exception):
    pass

class ModelNotRegistered(StdNetException):
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