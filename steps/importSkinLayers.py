from ..files.core import JsonFile
from .core import Step
from maya import cmds
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode
from ngSkinTools2 import api as ngst_api


class SkinLayersFile(JsonFile):
    pass


class Mesh(str):
    pass


class ImportSkinLayers(Step):

    def __init__(self, mesh=str(), file=str(), **kwargs):
        super(ImportSkinLayers, self).__init__(**kwargs)
        self.mesh = Mesh(mesh)
        self.file = SkinLayersFile(file)

    def build(self):
        cmds.loadPlugin('ngSkinTools2')

        config = InfluenceMappingConfig()
        config.use_distance_matching = True
        config.use_name_matching = True

        data = self.file.load()
        joints = [d['path'] for d in data.get('influences', list())]
        existingJoints = [j for j in joints if cmds.objExists(j)]

        cmds.skinCluster(self.mesh, *existingJoints)

        ngst_api.import_json(
            self.mesh,
            file=self.file,
            vertex_transfer_mode=VertexTransferMode.vertexId,
            influences_mapping_config=config,
        )