from maya import cmds

import rigBuilderComponents
reload(rigBuilderComponents)

import rigBuilderSteps
reload(rigBuilderSteps)

import rigBuilder
reload(rigBuilder)

from rigBuilderComponents import componentUtils
reload(componentUtils)

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
    guides_matrices[dag] = componentUtils.Matrix.get_from_dag(dag)

# Components
# World Local
world_local_component = rigBuilderComponents.WorldLocal.create(
    size=30,
    add_joint=True,
    matrix=guides_matrices['world_guide']
)

# Hips
hips_component = rigBuilderComponents.OneCtrl.create(
    id_='hips',
    size=30,
    add_joint=True,
    matrix=guides_matrices['hips_guide'],
    color=componentUtils.Color.pink,
    axis='y'
)

# Spine
spine_matrices = (
    guides_matrices['spine1_guide'],
    guides_matrices['spine2_guide'],
    guides_matrices['spine3_guide'],
    guides_matrices['spine4_guide'],
    guides_matrices['spine5_guide'],
)
spine_component = rigBuilderComponents.HybridChain.create(
    id_='spine',
    matrices=spine_matrices,
    size=25,
    ik_color=componentUtils.Color.dark_yellow,
    fk_color=componentUtils.Color.yellow
)

# Arms
left_arm_matrices = (
    guides_matrices['shoulder_guide'],
    guides_matrices['elbow_guide'],
    guides_matrices['wrist_guide'],
)

left_arm_component = rigBuilderComponents.TwoSegmentsLimb.create(
    id_='arm',
    side='L',
    matrices=left_arm_matrices,
    size=10,
)

right_arm_matrices = [matrix.get_mirror() for matrix in left_arm_matrices]

right_arm_component = rigBuilderComponents.TwoSegmentsLimb.create(
    id_='arm',
    side='R',
    matrices=right_arm_matrices,
    size=10,
)

# Connect components
connect_map = (
    (world_local_component.get_ends()[0], hips_component.get_roots()[0]),
    (hips_component.get_ends()[0], spine_component.get_roots()[0]),
    (spine_component.get_ends()[0], left_arm_component.get_roots()[1]),
    (spine_component.get_ends()[0], right_arm_component.get_roots()[1]),
)

for end, root in connect_map:
    rigBuilderComponents.MyComponent.connect(end, root)


# Skin meshes
joints = rigBuilderComponents.MyComponent.get_all_skin_joints()
for mesh in meshes:
    cmds.skinCluster(joints, mesh, skinMethod=1)

# ngSkinTools
rigBuilderSteps.import_ng_skin_layers(data_path + '/skin_layers.json', meshes[0])

# Clean up scene
components = rigBuilderComponents.MyComponent.get_all()
rigBuilderSteps.create_asset_folder(meshes=meshes, components=components)

# Test
print left_arm_component.get_roots()
print 'components', rigBuilderComponents.MyComponent.get_all()
print 'ctrls', rigBuilderComponents.MyComponent.get_all_ctrls()
print 'skin_joints', rigBuilderComponents.MyComponent.get_all_skin_joints()
