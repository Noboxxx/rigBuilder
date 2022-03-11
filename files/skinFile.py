from maya import cmds
from rigBuilder.files.core import JsonFile


class SkinFile(JsonFile):

    def export(self, meshes, force=False):
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

    def import_(self):
        data = self.load()
        for skinClusterName, info in data.items():

            influences = list()
            for influenceName, position in info['influences']:
                influences.append(influenceName)

            skinCluster, = cmds.skinCluster(influences + info['targets'], name=skinClusterName)

            for vertexIndex, weights in enumerate(info['weights']):
                cmds.skinPercent(
                    skinCluster,
                    '{}.vtx[{}]'.format(info['targets'][0], vertexIndex),
                    transformValue=[(influences[i], w) for i, w in weights],
                )
