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

rigBuilderSteps.import_maya_file(data_path + '/HumanBody.ma')
rigBuilderSteps.import_maya_file(data_path + '/guides.ma')

rigBuilderComponents.WorldLocal.create(size=30, add_joint=True, matrix=rigUtils.Matrix.get_from_transforms('world_guide'))

# Test
print 'components', rigBuilderComponents.MyComponent.get_all()
print 'ctrls', rigBuilderComponents.MyComponent.get_all_ctrls()
print 'skin_joints', rigBuilderComponents.MyComponent.get_all_skin_joints()
