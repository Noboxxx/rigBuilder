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


def getAttr(plug):
    plugSplit = plug.split('.')
    attr = '.'.join(plugSplit[1:])
    node = plugSplit[0]

    bareAttr = attr.split('.')[-1]
    if bareAttr.endswith(']'):
        bareAttr = bareAttr.split('[')[0]

    # multi = cmds.attributeQuery(bareAttr, node=node, multi=True)
    if not cmds.objExists(plug):
        return None

    indices = cmds.getAttr(plug, multiIndices=True)

    children = cmds.attributeQuery(bareAttr, node=node, listChildren=True)

    print ''
    print '--->', plug
    print 'indices', indices
    print 'children', children
    # print 'multi', multi

    if indices:
        value = dict()
        for index in indices:
            value[int(index)] = getAttr('{}[{}]'.format(plug, index))
    else:
        if children:
            value = dict()
            for child in children:
                value[child] = getAttr('{}.{}'.format(plug, child))
        else:
            value = cmds.getAttr(plug)

    return value


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
