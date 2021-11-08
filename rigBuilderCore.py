class Guides(object):
    pass


class Parameters(object):
    pass


class Side(object):

    def __init__(self, shortName, longName, primaryColor, secondaryColor, tertiaryColor):
        self.shortName = shortName
        self.longName = longName
        self.primaryColor = primaryColor
        self.secondaryColor = secondaryColor
        self.tertiaryColor = tertiaryColor
        self.mirrorSide = None

    def __str__(self):
        return self.shortName

    def setMirrorSide(self, side):
        self.mirrorSide = side


class Component(object):
    leftSide = Side('L', 'left', 'lime', 'green', 'green')
    rightSide = Side('R', 'right', 'red', 'red', 'red')
    centerSide = Side('C', 'center', 'yellow', 'yellow', 'yellow')

    leftSide.setMirrorSide(rightSide)
    rightSide.setMirrorSide(leftSide)

    def __init__(self, name, side, index, guides=None, parameters=None):
        self.name = name
        self.side = side
        self.index = index
        self.guides = guides
        self.parameters = parameters

        self.ctrls = list()
        self.folder = None

    def create(self):
        raise NotImplementedError

    def finalizeCreation(self, ctrls):
        self.ctrls = ctrls

    def formatObjectName(self, type, prefix=None):
        parts = [self.name, self.side, self.index, type]

        if prefix is not None:
            parts.insert(0, prefix)

        strParts = [str(part) for part in parts]
        return '_'.join(strParts)

    def mirror(self):
        mirrorSide = self.side.mirrorSide
        if mirrorSide is None:
            return None
        return self.__class__(self.name, mirrorSide, self.index, self.guides.mirror(), self.parameters.mirror())
