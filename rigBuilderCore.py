class Mirrorable(object):

    def __init__(self):
        self.__mirror = None

    def getMirror(self):
        return self if self.__mirror is None else self.__mirror

    def setMirror(self, obj):
        self.__mirror = obj


class Palette(Mirrorable):

    def __init__(self, primary, secondary, tertiary, bonus):
        super(Palette, self).__init__()

        self.primary = primary
        self.secondary = secondary
        self.tertiary = tertiary
        self.bonus = bonus


leftPalette = Palette('lime', 'green', 'green', 'blue')
rightPalette = Palette('red', 'red', 'red', 'blue')
centerPalette = Palette('yellow', 'yellow', 'yellow', 'blue')

leftPalette.setMirror(rightPalette)
rightPalette.setMirror(leftPalette)


class Side(Mirrorable):

    def __init__(self, name):
        super(Side, self).__init__()

        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Side):
            return other.name == self.name
        return False


leftSide = Side('L')
rightSide = Side('R')
centerSide = Side('C')

leftSide.setMirror(rightSide)
rightSide.setMirror(leftSide)


class Component(object):

    def __init__(self, name, side, index):
        self.name = name
        self.side = side
        self.index = index

        self.ctrls = list()
        self.folder = None

    def create(self):
        raise NotImplementedError

    def setCtrls(self, ctrls):
        self.ctrls = ctrls

    def createFolder(self, name):
        self.folder = name

    def formatObjectName(self, type, prefix=None):
        parts = [self.name, self.side, self.index, type]

        if prefix is not None:
            parts.insert(0, prefix)

        strParts = [str(part) for part in parts]
        return '_'.join(strParts)

    def getMirror(self):
        mirrorSide = self.side.mirrorSide
        if mirrorSide is None:
            return None
        mirrorPalette = None if self.palette is None else self.palette.mirror
        return self.__class__(self.name, mirrorSide, self.index)
