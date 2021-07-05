import os
from maya import cmds
import time


def log(func):
    def wrapper(*args, **kwargs):
        print('')
        print('-' * 10)
        print('\'{0}\' starts.'.format(func.__name__))
        print('args: {}'.format(args))
        print('kwargs: {}'.format(kwargs))
        print('-' * 10)
        print('')

        start = time.time()
        result = func(*args, **kwargs)
        delta = time.time() - start

        print ('')
        print('-' * 10)
        print('\'{0}\' has ended. It took {1} seconds.'.format(func.__name__, delta))
        print('-' * 10)
        print('')

        return result
    return wrapper


@log
def build(path):
    if os.path.isfile(path):
        execfile(path)
    else:
        cmds.warning('The file \'{0}\' does\'nt exist.'.format(path))


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
        plug = '{}.{}'.format(folder, cls.component_type_attr_name)
        cmds.addAttr(folder, longName=cls.component_type_attr_name, dataType='string', enumName=component_type)
        cmds.setAttr(plug, cls.__name__, type='string')
        cmds.setAttr(plug, lock=True)

        if dags:
            cmds.parent(dags, folder)

        if cmds.objExists(parent):
            cmds.parent(folder, parent)

        return cls(folder)

    @classmethod
    def create(cls):
        pass

    def get_folder(self):
        return self.__folder

    @classmethod
    def connect(cls, parent, child):
        cnstr, = cmds.parentConstraint(parent, child, maintainOffset=True)
        cmds.setAttr('{}.{}'.format(cnstr, 'interpType'), 2)

        cmds.scaleConstraint(parent, child, maintainOffset=True)