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
    roots_attr_name = 'roots'
    ends_attr_name = 'ends'
    ctrls_attr_name = 'ctrls'
    skin_joints_attr_name = 'skinJoints'

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
        if cmds.objExists(folder):
            if cmds.objectType(folder, isAType='transform'):
                if cmds.objExists('{0}.{1}'.format(folder, cls.component_type_attr_name)):
                    return True
        return False

    @classmethod
    def create_folder(cls, dags=None, name=None, parent=None, roots=None, ends=None, ctrls=None, skin_joints=None):
        dags = tuple() if dags is None else [str(dag) for dag in dags]
        parent = str(parent)

        roots = tuple() if roots is None else [str(root) for root in roots]
        ends = tuple() if ends is None else [str(end) for end in ends]
        ctrls = tuple() if ctrls is None else [str(ctrl) for ctrl in ctrls]
        skin_joints = tuple() if skin_joints is None else [str(skin_joint) for skin_joint in skin_joints]

        component_type = cls.__name__.lower()
        name = component_type if name is None else str(name)

        folder = cmds.group(name=name, empty=True)
        type_plug = '{}.{}'.format(folder, cls.component_type_attr_name)
        cmds.addAttr(folder, longName=cls.component_type_attr_name, dataType='string', enumName=component_type)
        cmds.setAttr(type_plug, cls.__name__, type='string')
        cmds.setAttr(type_plug, lock=True)

        objects_map = (
            (cls.ends_attr_name, ends),
            (cls.roots_attr_name, roots),
            (cls.ctrls_attr_name, ctrls),
            (cls.skin_joints_attr_name, skin_joints),
        )
        for attr, objects in objects_map:
            source_plug = '{}.{}'.format(folder, attr)
            cmds.addAttr(folder, longName=attr, attributeType='message')
            for obj in objects:
                destination_plug = '{}.{}'.format(obj, attr)
                cmds.addAttr(obj, longName=attr, attributeType='message')
                cmds.connectAttr(source_plug, destination_plug)

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

    def get_roots(self):
        return cmds.listConnections('{}.{}'.format(self.get_folder(), self.roots_attr_name), source=False, destination=True) or list()

    def get_ends(self):
        return cmds.listConnections('{}.{}'.format(self.get_folder(), self.ends_attr_name), source=False, destination=True) or list()

    def get_ctrls(self):
        return cmds.listConnections('{}.{}'.format(self.get_folder(), self.ctrls_attr_name), source=False, destination=True) or list()

    def get_skin_joints(self):
        return cmds.listConnections('{}.{}'.format(self.get_folder(), self.skin_joints_attr_name), source=False, destination=True) or list()

    @classmethod
    def get_all(cls):
        components = list()
        for node in cmds.ls(type='transform'):
            if cls.is_one(node):
                components.append(cls(node))
        components.sort()
        return components

    @classmethod
    def get_all_skin_joints(cls):
        joints = list()
        for component in cls.get_all():
            joints += component.get_skin_joints()
        joints.sort()
        return joints

    @classmethod
    def get_all_ctrls(cls):
        ctrls = list()
        for component in cls.get_all():
            ctrls += component.get_ctrls()
        ctrls.sort()
        return ctrls