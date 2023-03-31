import logging

def catch_exceptions(func, event_id={ "request_id":"", "event_id":""}):
    
    def wrapped_function(*args, **kargs):
        try:
            return func(*args, **kargs)
        except Exception as e:
            l = logging.getLogger(func.__name__)
            l.error(e,extra=event_id, exc_info=True)
            return None                
    return wrapped_function