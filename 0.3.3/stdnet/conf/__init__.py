import os
from stdnet.utils.importlib import import_module
from stdnet.conf import global_settings


ENVIRONMENT_VARIABLE = "STDNET_SETTINGS_MODULE"


class Settings(object):
    
    def __init__(self):
        self.fill(global_settings)

    def fill(self, settings_module):
        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(settings_module):
            if setting == setting.upper():
                setattr(self, setting, getattr(settings_module, setting))


def get_settings():
    settings_module = os.environ.get(ENVIRONMENT_VARIABLE,None)
    
    sett = Settings()
    
    if settings_module: 
        try:
            mod = import_module(settings_module)
            sett.fill(mod)
        except ImportError, e:
            try:
                import json
                ds = json.loads(settings_module)
                for k,v in ds.items():
                    setattr(sett,str(k).upper(),v)
            except:
                raise ImportError("Could not import settings '%s': %s" % (settings_module, e))
    
    return sett


settings = get_settings()
