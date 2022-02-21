from imath import clamp


class Side(str):

    mirrorTable = {
        'L': 'R',
        'R': 'L',
        'C': 'C',
    }

    def __init__(self, side):  # type: (str) -> None
        if side not in self.mirrorTable:
            raise ValueError('Unrecognized Side \'{}\'.'.format(side))
        super(Side, self).__init__(side)

    def mirrored(self):
        return self.__class__(self.mirrorTable[self])


class Color(list):

    def __init__(self, r, g, b):  # type: (int, int, int) -> None
        r = clamp(int(r), 0, 255)
        g = clamp(int(g), 0, 255)
        b = clamp(int(b), 0, 255)
        super(Color, self).__init__((r, g, b))

    @property
    def r(self):
        return self[0]

    @r.setter
    def r(self, v):
        self[0] = clamp(int(v), 0, 255)

    @property
    def g(self):
        return self[0]

    @g.setter
    def g(self, v):
        self[0] = clamp(int(v), 0, 255)

    @property
    def b(self):
        return self[0]

    @b.setter
    def b(self, v):
        self[0] = clamp(int(v), 0, 255)

    def mirrored(self):
        mirroredColor = list()
        for v in self:
            distance = 127.5 - v
            r = distance * 2 + v
            mirroredColor.append(int(r))
        return self.__class__(*mirroredColor)


class UnsignedInt(int):

    def __init__(self, value):  # type: (int) -> None
        if value < 0:
            raise ValueError('Value should be positive.')
        super(UnsignedInt, self).__init__(value)


class UnsignedFloat(float):

    def __init__(self, value):  # type: (float) -> None
        if value < 0.0:
            raise ValueError('Value should be positive.')
        super(UnsignedFloat, self).__init__(value)
