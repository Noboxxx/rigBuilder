from imath import clamp
import math
import os


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
        r = int(clamp(int(r), 0, 255))
        g = int(clamp(int(g), 0, 255))
        b = int(clamp(int(b), 0, 255))
        super(Color, self).__init__((r, g, b))

    @property
    def r(self):
        return self[0]

    @r.setter
    def r(self, v):
        self[0] = int(clamp(int(v), 0, 255))

    @property
    def g(self):
        return self[0]

    @g.setter
    def g(self, v):
        self[0] = int(clamp(int(v), 0, 255))

    @property
    def b(self):
        return self[0]

    @b.setter
    def b(self, v):
        self[0] = int(clamp(int(v), 0, 255))

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


class Vector(list):

    def __init__(self, *args):
        args = map(float, args)

        super(Vector, self).__init__(args)

        magnitude = self.magnitude()
        if magnitude <= 0.0:
            raise ValueError('magnitude is equal or less than 0.0 -> {}'.format(magnitude))

    def copy(self):
        return self.__class__(*self)

    def mirrored(self, mirrorAxis='x'):
        vectorCopy = self.copy()
        vectorCopy.mirror(mirrorAxis)
        return vectorCopy

    def mirror(self, mirrorAxis='x'):
        if mirrorAxis == 'x':
            self[0] *= -1
        elif mirrorAxis == 'y':
            self[1] *= -1
        elif mirrorAxis == 'z':
            self[2] *= -1
        else:
            raise ValueError('Unrecognized axis -> {}'.format(mirrorAxis))

    def magnitude(self):
        result = 0
        for scalar in self:
            result += scalar ** 2.0
        return math.sqrt(result)

    def normalized(self):
        vectorCopy = self.copy()
        vectorCopy.normalize()
        return vectorCopy

    def normalize(self):
        magnitude = self.magnitude()
        for index in range(len(self)):
            self[index] /= magnitude


class Matrix(list):

    def __init__(
            self,
            xx=1.0, xy=0.0, xz=0.0, xw=0.0,
            yx=0.0, yy=1.0, yz=0.0, yw=0.0,
            zx=0.0, zy=0.0, zz=1.0, zw=0.0,
            px=0.0, py=0.0, pz=0.0, pw=1.0,
    ):
        super(Matrix, self).__init__(
            (
                float(xx), float(xy), float(xz), float(xw),
                float(yx), float(yy), float(yz), float(yw),
                float(zx), float(zy), float(zz), float(zw),
                float(px), float(py), float(pz), float(pw),
            )
        )

    def rows(self):
        return (
            (self[0], self[1], self[2], self[3]),
            (self[4], self[5], self[6], self[7]),
            (self[8], self[9], self[10], self[11]),
            (self[12], self[13], self[14], self[15]),
        )

    def columns(self):
        return (
            (self[0], self[4], self[8], self[12]),
            (self[1], self[5], self[9], self[13]),
            (self[2], self[6], self[10], self[14]),
            (self[3], self[7], self[11], self[15]),
        )

    def copy(self):
        return self.__class__(*self)

    def mirrored(self, mirrorAxis='x'):
        matrixCopy = self.copy()
        matrixCopy.mirror(mirrorAxis)
        return matrixCopy

    def mirror(self, mirrorAxis='x', compensateNegativeScale=True):
        if mirrorAxis == 'x':
            self[0] *= -1
            self[4] *= -1
            self[8] *= -1
            self[12] *= -1

        elif mirrorAxis == 'y':
            self[1] *= -1
            self[5] *= -1
            self[9] *= -1
            self[13] *= -1

        elif mirrorAxis == 'z':
            self[2] *= -1
            self[6] *= -1
            self[10] *= -1
            self[14] *= -1

        else:
            raise ValueError('Unrecognized mirror axis -> {}'.format(mirrorAxis))

        if compensateNegativeScale:
            self[0] *= -1
            self[1] *= -1
            self[2] *= -1

            self[4] *= -1
            self[5] *= -1
            self[6] *= -1

            self[8] *= -1
            self[9] *= -1
            self[10] *= -1

    def normalize(self):
        vectorX = Vector(self[0], self[1], self[2])
        vectorX.normalize()
        self[0] = vectorX[0]
        self[1] = vectorX[1]
        self[2] = vectorX[2]

        vectorY = Vector(self[4], self[5], self[6])
        vectorY.normalize()
        self[4] = vectorY[0]
        self[5] = vectorY[1]
        self[6] = vectorY[2]

        vectorZ = Vector(self[8], self[9], self[10])
        vectorZ.normalize()
        self[8] = vectorZ[0]
        self[9] = vectorZ[1]
        self[10] = vectorZ[2]

    def normalized(self):
        matrixCopy = self.copy()
        matrixCopy.normalize()
        return matrixCopy

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            newMatrix = list()
            for column in self.rows()[:3]:
                for row in other.columns()[:3]:
                    result = 0
                    for c, r in zip(column, row):
                        result += c * r
                    newMatrix.append(result)
                newMatrix.append(0.0)
            newMatrix.append(self[12] + other[12])
            newMatrix.append(self[13] + other[13])
            newMatrix.append(self[14] + other[14])
            newMatrix.append(1.0)
            return self.__class__(*newMatrix)
        raise TypeError(
            'cannot do \'{}\' * \'{}\''.format(
                str(self.__class__),
                str(type(other)),
            )
        )


class File(str):

    def __init__(self, path=''):
        path = os.path.normpath(path)
        super(File, self).__init__(path)

    @classmethod
    def join(cls, *args):
        path = os.path.normpath('\\'.format(*[str(arg) for arg in args]))
        return cls(path)

    @property
    def absolute(self):
        if self.startswith('...'):
            return self.__class__.join(os.getcwd(), self.replace('...', ''))
        return self
