import asyncio
import time
from functools import wraps
from typing import Coroutine


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


async def async_run_tasks(coroutines: list[Coroutine]) -> list[asyncio.Task]:
    tasks = [asyncio.create_task(coroutine) for coroutine in coroutines]
    await asyncio.wait(tasks)

    return tasks
