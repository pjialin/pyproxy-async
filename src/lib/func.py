import json


def retry(num: int = 3):
    """
    Retry a func
    :param num:
    :return:
    """
    from lib.exceptions import MaxRetryException, RetryException
    retry_num_key = '_retry_num'

    def decorator(func):
        async def wrapper(*args, **kwargs):
            retry_num = num
            if retry_num_key in kwargs:
                retry_num = kwargs.get(retry_num_key)
                kwargs.pop(retry_num_key)
            try:
                res = await func(*args, **kwargs)
            except RetryException as err:
                retry_num -= 1
                from app.main import Logger
                Logger.warning('Retry %s, remaining times %d' % (func.__name__, retry_num))
                if retry_num > 0:
                    kwargs[retry_num_key] = retry_num
                    return await wrapper(*args, **kwargs)
                raise MaxRetryException() from err

            return res

        return wrapper

    return decorator


def md5(value):
    import hashlib
    return hashlib.md5(json.dumps(value).encode()).hexdigest()


def time_int():
    import time
    return int(time.time())


def str_to_ip(ip_str: str):
    ip, port = ip_str.split(':')
    return ip, port


def run_until_complete(callback):
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(callback)
