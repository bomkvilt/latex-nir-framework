from __future__ import annotations



# This class must be used as a __metaclass__ for classes
# that must be created only once
# https://stackoverflow.com/a/6798042 
# 
# Usage example:
# 
#   class Logger(metaclass = Singleton):
#       pass
# 
class Singleton(type):
    # map of class' instances
    _instances = dict[type, type]()

    # class factory call
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
