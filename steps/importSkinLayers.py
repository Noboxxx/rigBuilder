from ..files.core import JsonFile
from .core import Step
from maya import cmds


class SkinLayersFile(JsonFile):
    pass


class Node(str):
    pass


class Mesh(Node):
    pass


class ImportSkinLayers(Step):

    def __init__(self, mesh=str(), file=str(), **kwargs):
        super(ImportSkinLayers, self).__init__(**kwargs)
        self.mesh = Mesh(mesh)
        self.file = SkinLayersFile(file)

    def build(self):
        from maya import OpenMayaUI

        class Duck(object):
            @staticmethod
            def mainWindow(*args, **kwargs):
                return 0

            @staticmethod
            def dpiScale(*args, **kwargs):
                return 1

        store = OpenMayaUI.MQtUtil
        OpenMayaUI.MQtUtil = Duck

        ###
        from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode
        from ngSkinTools2 import api as ngst_api

        cmds.loadPlugin('ngSkinTools2')

        config = InfluenceMappingConfig()
        config.use_distance_matching = True
        config.use_name_matching = True

        data = self.file.load()

        joints = [d['path'] for d in data.get('influences', list())]  # long names
        joints = [j.split('|')[-1] for j in joints]  # short names

        existingJoints = [j for j in joints if cmds.objExists(j)]

        cmds.skinCluster(self.mesh, *existingJoints)

        ngst_api.import_json(
            self.mesh,
            file=self.file,
            vertex_transfer_mode=VertexTransferMode.vertexId,
            influences_mapping_config=config,
        )
        ###

        OpenMayaUI.MQtUtil = store
