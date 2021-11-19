from . import RParam, RCore


def placeHolder(*arg, **kwargs):
    return None


createTransformFunc = placeHolder
parentTransformFunc = placeHolder


class Transform(RCore.RBaseObject):

    @classmethod
    def create(cls, name=None):
        name = createTransformFunc(name=name)
        return cls(name)

    def parent(self, *children):
        self.parentFunc(children=children, parent=self)


class Controller(Transform):
    createFunc = None

    @classmethod
    def create(cls, name=None, normal=RParam.Vector3(1.0, 0.0, 0.0), radius=1.0):
        name = cls.createFunc(name=name, normal=normal, radius=radius)
        return cls(name)
