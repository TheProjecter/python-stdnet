import os
from stdnet.utils.importlib import import_module
from stdnet.conf import global_settings


ENVIRONMENT_VARIABLE = "STDNET_SETTINGS_MODULE"


class Settings(object):
    pass

def fill(self, settings_module):
        
    # update this dict from global settings (but only for ALL_CAPS settings)
    for setting in dir(settings_module):
        if setting == setting.upper():
            setattr(self, setting, getattr(settings_module, setting))


def get_settings():
    settings_module = os.environ.get(ENVIRONMENT_VARIABLE,None)
    
    if settings_module: 
        try:
            mod = import_module(settings_module)
        except ImportError, e:
            raise ImportError("Could not import settings '%s': %s" % (settings_module, e))
    else:
        mod = None
    
    sett = Settings()
    
    fill(sett,global_settings)
    if mod:
        fill(sett,mod)
    return sett


settings = get_settings()
