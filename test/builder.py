import rigBuilderComponents
reload(rigBuilderComponents)

import rigBuilderSteps
reload(rigBuilderSteps)

import rigBuilder
reload(rigBuilder)

from rigBuilderComponents import rigUtils
reload(rigUtils)

data_path_split = __file__.split('\\')
data_path = '/'.join(data_path_split[:-1] + ['test'])

rigBuilderSteps.new_scene()
rigBuilderSteps.import_maya_file(data_path + '/HumanBody.ma')
rigBuilderComponents.WorldLocal.create(size=30)