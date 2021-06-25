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


class Component(object):

    component_type_attr_name = 'componentType'

    def __init__(self, folder):
        if not self.is_one(folder):
            cmds.error('\'{0}\' is not a valid component folder'.format(folder))
        self.__folder = folder

    def __str__(self):
        return self.get_folder()

    def __repr__(self):
        return self.get_folder()

    @classmethod
    def is_one(cls, folder):
        if cmds.objExists('{0}.{1}'.format(folder, cls.component_type_attr_name)):
            return True
        return False

    @classmethod
    def create_folder(cls, dags=None, name=None, parent=None):
        dags = tuple() if dags is None else [str(dag) for dag in dags]
        parent = str(parent)

        component_type = cls.__name__.lower()
        name = component_type if name is None else str(name)

        folder = cmds.group(name=name, empty=True)
        cmds.addAttr('{0}.{1}'.format(folder, cls.component_type_attr_name), attributeData='string', enumName=component_type)

        if dags:
            cmds.parent(dags, folder)

        if cmds.objExists(parent):
            cmds.parent(folder, parent)

        return cls(folder)

    @classmethod
    def create(cls):
        raise NotImplementedError

    def get_folder(self):
        return self.__folder
