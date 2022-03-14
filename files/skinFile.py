import math

from maya import cmds
from rigBuilder.files.core import JsonFile


class SkinFile(JsonFile):

    def export(self, meshes=None, force=False):

        meshes = meshes if meshes is not None else cmds.listRelatives(
            cmds.ls(sl=True, type='transform'), type='mesh', allDescendents=True
        )

        data = dict()
        for mesh in meshes:
            for skinCluster in cmds.listHistory(mesh):
                if not cmds.objectType(skinCluster, isAType='skinCluster') or skinCluster in data:
                    continue

                targets = cmds.skinCluster(skinCluster, q=True, geometry=True)

                weights = list()
                for vertexIndex in cmds.getAttr('{}.weightList'.format(skinCluster), multiIndices=True):
                    infIndices = cmds.getAttr('{}.weightList[{}].weights'.format(skinCluster, vertexIndex), multiIndices=True)
                    infWeights = cmds.getAttr('{}.weightList[{}].weights'.format(skinCluster, vertexIndex))[0]
                    weights.append(zip(infIndices, infWeights))

                influences = list()
                for influence in cmds.skinCluster(skinCluster, q=True, influence=True):
                    influences.append((influence, cmds.xform(influence, q=True, translation=True, worldSpace=True)))

                data[skinCluster] = {
                    'influences': influences,
                    'weights': weights,
                    'targets': targets
                }

        self.dump(data, force=force)

    @staticmethod
    def distance(pointA, pointB):
        result = 0
        for r in [(b - a) ** 2 for a, b in zip(pointA, pointB)]:
            result += r
        return abs(math.sqrt(result))

    @staticmethod
    def getClosestJoint(position):
        distance = -1
        joint = None
        for j in cmds.ls(type='joint'):
            p = cmds.xform(j, q=True, translation=True, worldSpace=True)
            d = SkinFile.distance(position, p)
            if distance == -1 or d < distance:
                distance = d
                joint = j

        return joint

    def import_(self):

        data = self.load()
        for skinClusterName, info in data.items():

            influences = list()
            for influenceName, position in info['influences']:
                if cmds.objExists(influenceName):
                    influences.append(influenceName)
                else:
                    closestJoint = self.getClosestJoint(position)
                    influences.append(closestJoint)

            skinCluster, = cmds.skinCluster(influences + info['targets'], name=skinClusterName)

            for vertexIndex, weights in enumerate(info['weights']):
                cmds.skinPercent(
                    skinCluster,
                    '{}.vtx[{}]'.format(info['targets'][0], vertexIndex),
                    transformValue=[(influences[i], w) for i, w in weights],
                )
