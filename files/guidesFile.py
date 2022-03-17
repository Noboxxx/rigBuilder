from collections import OrderedDict

from maya import cmds
from rigBuilder.components.core import Guide
from rigBuilder.files.core import JsonFile


class GuidesFile(JsonFile):

    guideFolder = 'guides'

    def export(self, guidesFolder='', force=False):
        data = OrderedDict()

        for guide in reversed(cmds.listRelatives(guidesFolder or self.guideFolder, allDescendents=True, type='transform')):
            data[guide] = {
                'parent': cmds.listRelatives(guide, parent=True)[0],
                'matrix': cmds.xform(guide, q=True, matrix=True, worldSpace=True),
                'locked': cmds.listAttr(guide, locked=True) or list(),
            }

        self.dump(data, force=force)

    def import_(self):
        data = self.load()
        namingMap = dict()

        guidesFolder = cmds.group(empty=True, name=self.guideFolder)
        namingMap[self.guideFolder] = guidesFolder

        # Create guides
        parenting = list()
        for name, info in data.items():
            guide = Guide.create(name)

            for attr in info['locked']:
                cmds.setAttr('{}.{}'.format(guide, attr), lock=True)

            cmds.xform(guide, matrix=info['matrix'])
            namingMap[name] = str(guide)

            if info['parent'] != self.guideFolder:
                parenting.insert(0, (guide, info['parent']))

        # parent stuff
        for child, parent in parenting:
            print child, namingMap[parent]
            cmds.parent(child, namingMap[parent])
