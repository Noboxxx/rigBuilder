from collections import OrderedDict

from maya import cmds
from rigBuilder.files.core import JsonFile


class SkinLayersFile(JsonFile):

    def export(self, meshes=None, force=False):
        from ngSkinTools2 import api

        meshes = meshes if meshes is not None else cmds.listRelatives(
            cmds.ls(sl=True, type='transform'), type='mesh', allDescendents=True
        )
        meshes = [m for m in meshes if not cmds.getAttr('{}.intermediateObject'.format(m))]

        data = dict()
        for mesh in meshes:
            layers = api.Layers(mesh)

            influences = [(i.logicalIndex, i.path.split('|')[-1]) for i in layers.list_influences()]

            layersData = OrderedDict()
            for layer in layers.list():

                parent = layer.parent.name if layer.parent else None

                weights = dict()
                for index, name in influences:
                    weights[name] = layer.get_weights(index)

                layersData[layer.name] = {
                    'parent': parent,
                    'weights': weights,
                    'mask': layer.get_weights(api.NamedPaintTarget.MASK),
                    'dualQuaternion': layer.get_weights(api.NamedPaintTarget.DUAL_QUATERNION),
                }

            data[mesh] = {
                'layers': layersData,
            }

        self.dump(data, force=force)

    def import_(self):
        from ngSkinTools2 import api

        data = self.load()

        for mesh, meshData in data.items():
            layers = api.init_layers(mesh)

            for layerName, layerData in meshData.get('layers', dict()).items():
                layer = layers.add(layerName)

