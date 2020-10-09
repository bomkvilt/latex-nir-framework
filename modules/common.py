
### define static variables
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])

        def callback(*args):
            return func(*args, func)
        
        return callback
    return decorate
