from maya.api import OpenMaya
from rigBuilder.files.core import JsonFile
from maya import cmds


def setAttr(plug, attributesMap=None):
    for attr, value in attributesMap.items():
        p = '{}.{}'.format(plug, attr)

        if isinstance(value, (list, tuple)):
            for i, v in enumerate(value):
                setAttr('{}[{}]'.format(p, i), v)
        elif isinstance(value, dict):
            for k, v in value.items():
                if k.isdigit():
                    setAttr('{}[{}]'.format(p, k), v)
                else:
                    setAttr('{}.{}'.format(p, k), v)

        else:
            cmds.setAttr(p, value)


def attributeChildren(plug):
    children = [i for i in cmds.listAttr(plug) if i.count('.') == 1]
    return [i.split('.')[-1] for i in children if not plug.endswith(i)]


def getAttr(obj):  # type: (OpenMaya.MPlug or basestring) -> any
    if not isinstance(obj, OpenMaya.MPlug):
        selection = OpenMaya.MSelectionList()
        selection.add(obj)
        try:
            plug = selection.getPlug(0)  # type: OpenMaya.MPlug
        except TypeError:
            obj = selection.getDependNode(0)  # type: OpenMaya.MObject
            node = OpenMaya.MFnDependencyNode(obj)
            values = dict()
            for index in range(node.attributeCount()):
                attribute = OpenMaya.MFnAttribute(node.attribute(index))
                plug = OpenMaya.MPlug(node.object(), attribute.object())
                if str(plug).count('.') == 1:
                    values[attribute.name] = getAttr(plug)
            return values
    else:
        plug = obj

    if plug.isArray:
        values = dict()
        for index in plug.getExistingArrayAttributeIndices():
            child = plug.elementByPhysicalIndex(index)
            values[index] = getAttr(child)
        return values

    elif plug.isCompound:
        values = dict()
        for index in range(plug.numChildren()):
            child = plug.child(index)
            attribute = OpenMaya.MFnAttribute(child.attribute()).name
            values[attribute] = getAttr(child)
        return values

    t = cmds.getAttr(plug, type=True)

    if t == 'message':
        return None

    return cmds.getAttr(plug)


class PoseInterpolatorFile(JsonFile):

    attributes = {
        'regularization': 0.0,
        'interpolation': 0,
        'outputSmoothing': 0.0,
        'allowNegativeWeights': True,
        'enableRotation': True,
        'enableTranslation': False
    }

    poseAttributes = {
        'poseName': None,
        'isIndependent': False,
        'poseRotationFalloff': 180.0,
        'poseTranslationFalloff': 0.0,
        'poseType': 1,
        'poseFalloff': 1.0,
        'isEnabled': True,
        'poseRotation': None,
        'poseTranslation': None,
    }

    def export(self, nodes=None, force=False):
        nodes = nodes if nodes is not None else cmds.ls(type='poseInterpolator')

        data = dict()
        for node in nodes:

            transforms = cmds.listRelatives(node, parent=True)
            parents = cmds.listRelatives(transforms[0], parent=True)
            drivers = cmds.listConnections('{}.driver[0].driverMatrix'.format(node), source=True, destination=False)

            data[node] = {
                'transform': transforms[0],
                'parent': parents[0] if parents else None,
                'driver': drivers[0] if drivers else None,
                'poses': getAttr('{}.pose'.format(node))
            }

            for attr, default in self.attributes.items():
                value = cmds.getAttr('{}.{}'.format(node, attr))
                if value != default:
                    data[node][attr] = value

        self.dump(data, force=force)

    def import_(self):
        pass
