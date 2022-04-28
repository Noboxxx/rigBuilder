from maya import cmds
from rigBuilder.files.core import JsonFile
from rigBuilder.files.poseInterpolatorFile import getAttr, setAttr


def getConnections(node):
    sources = cmds.listConnections(node, source=True, destination=False, plugs=True, connections=True) or list()
    sources.reverse()

    destinations = cmds.listConnections(node, source=False, destination=True, plugs=True, connections=True) or list()

    connections = sources + destinations
    connections = [connections[x:x+2] for x in range(0, len(connections), 2)]

    return connections


def splitPlug(plug):
    splitName = plug.split('.')

    node = splitName.pop(0)
    attr = '.'.join(splitName)

    return node, attr


def nodesData(nodes):
    data = dict()

    for node in nodes:
        print ''
        print '### {} ###'.format(node)
        for attr in cmds.listAttr(node, write=True, hasData=True):  # , multi=True):
            plug = '{}.{}'.format(node, attr)
            if not cmds.objExists(plug):
                # print 'NOPE:', plug
                continue

            t = cmds.getAttr(plug, type=True)
            if t == 'TdataCompound':
                continue

            value = cmds.getAttr(plug)
            if isinstance(value, (tuple, list)) or value is None:
                continue
            defaults = cmds.attributeQuery(attr, node=node, listDefault=True)
            default = None if not defaults else defaults[0]
            if default == value:
                continue
            print '--->', plug, '({})'.format(t), '->', repr(value), '(default: {})'.format(repr(default))
        print '###'
        print ''

    return data


class NodesFile(JsonFile):

    def export(self, nodes=None, force=False):
        nodesData = dict()

        nodes = nodes if nodes else cmds.ls(sl=True)
        for node in nodes:
            values = getAttr(node, ignoreDefaults=True, onlyWritable=True)
            t = cmds.objectType(node)
            d = {'type': t, 'values': values}
            if cmds.objectType(node, isAType='shape'):
                parents = cmds.listRelatives(node, parent=True)
                d['parent'] = parents[0]

        insideConnections = list()
        borderConnections = list()
        for node in nodes:
            connections = getConnections(node)

            for connection in connections:
                if connection in insideConnections or connection in borderConnections:
                    continue

                srcNode = connection[0].split('.')[0]
                desNode = connection[1].split('.')[0]

                if desNode in nodes and srcNode in nodes:
                    insideConnections.append(connection)
                else:
                    borderConnections.append(connection)

        data = {
            'nodes': nodesData,
            'insideConnections': insideConnections,
            'borderConnections': borderConnections,
        }

        self.dump(data, force=force)

    def import_(self):
        data = self.load()
        nodes = data['nodes']
        insideConnections = data['insideConnections']
        borderConnections = data['borderConnections']

        nameMap = dict()
        for nodeName, nodeInfo in nodes.items():
            kwargs = dict()
            if 'parent' in nodeInfo:
                kwargs['parent'] = nodeInfo['parent']
            node = cmds.createNode(nodeInfo['type'], name=nodeName, **kwargs)
            nameMap[nodeName] = node
            setAttr(node, nodeInfo['values'])

        for srcPlug, desPlug in insideConnections:
            srcNode, srcAttr = splitPlug(srcPlug)
            desNode, desAttr = splitPlug(desPlug)

            newSrcPlug = '.'.join((nameMap[srcNode], srcAttr))
            newDesPlug = '.'.join((nameMap[desNode], desAttr))

            cmds.connectAttr(newSrcPlug, newDesPlug)
