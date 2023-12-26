import time
from functools import wraps


def class_local_cache(expire_time: int = 60):
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            str_args = '_'.join([str(arg) for arg in args])
            str_kwrags = '_'.join([f'{key}_{value}' for key, value in kwargs.items()])
            key = f'{func.__name__}_{str_args}_{str_kwrags}'
            if key in cache:
                if cache[key]['expire_time'] > time.time():
                    return cache[key]['value']
                else:
                    del cache[key]

            result = func(*args, **kwargs)
            cache[key] = {
                'value': result,
                'expire_time': time.time() + expire_time
            }
            return result

        return wrapper
    return decorator
