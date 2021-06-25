import os
from maya import cmds
import time


def log(func):
    def wrapper(*args, **kwargs):
        print('-' * 10)
        print('\'{0}\' starts.'.format(func.__name__))
        print('args: {}.'.format(args))
        print('kwargs: {}'.format(kwargs))
        print('-' * 10)

        start = time.time()
        result = func(*args, **kwargs)
        delta = time.time() - start

        print('-' * 10)
        print('\'{0}\' has ended. It took {1} seconds.'.format(func.__name__, delta))
        print('-' * 10)

        return result
    return wrapper


@log
def build(path):
    if os.path.isfile(path):
        execfile(path)
    else:
        cmds.warning('The file \'{0}\' doesnt exist.'.format(path))
