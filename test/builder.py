from maya import cmds

import rigBuilderComponents
reload(rigBuilderComponents)

import rigBuilderSteps
reload(rigBuilderSteps)

import rigBuilder
reload(rigBuilder)

from rigBuilderComponents import rigUtils
reload(rigUtils)

# Data path
data_path_split = __file__.split('\\')
data_path = '/'.join(data_path_split[:-1] + ['test'])

# Build steps
rigBuilderSteps.new_scene()

# Import Geo
rigBuilderSteps.import_maya_file(data_path + '/HumanBody.ma')
meshes = ('humanBody',)

# Guides to matrices map
rigBuilderSteps.import_maya_file(data_path + '/guides.ma')
guides_matrices = dict()
for dag in cmds.listRelatives('guides', allDescendents=True, type='transform'):
    guides_matrices[dag] = rigUtils.Matrix.get_from_dag(dag)

# Components
hips_component = rigBuilderComponents.OneCtrl.create(id_='hips', size=30, add_joint=True, matrix=guides_matrices['hips_guide'], color=rigUtils.Color.pink, axis='y')

world_local_component = rigBuilderComponents.WorldLocal.create(size=30, add_joint=True, matrix=guides_matrices['world_guide'])
world_local_component.connect_to_local_ctrl(hips_component.get_ctrl().get_buffer())

spine_matrices = (
    guides_matrices['spine1_guide'],
    guides_matrices['spine2_guide'],
    guides_matrices['spine3_guide'],
    guides_matrices['spine4_guide'],
    guides_matrices['spine5_guide'],
)
spine_component = rigBuilderComponents.FkChain.create(id_='spine', matrices=spine_matrices, size=25, color=rigUtils.Color.yellow)

# Skin mesh
joints = rigBuilderComponents.MyComponent.get_all_skin_joints()
for mesh in meshes:
    cmds.skinCluster(joints, mesh)

# ngSkinTools
rigBuilderSteps.import_ng_skin_layers(data_path + '/skin_layers.json', meshes[0])

# Clean up scene
components = rigBuilderComponents.MyComponent.get_all()
rigBuilderSteps.create_asset_folder(meshes=meshes, components=components)

# Test
print 'components', rigBuilderComponents.MyComponent.get_all()
print 'ctrls', rigBuilderComponents.MyComponent.get_all_ctrls()
print 'skin_joints', rigBuilderComponents.MyComponent.get_all_skin_joints()
