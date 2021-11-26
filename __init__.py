class RBaseComponent(object):

    def __init__(self, *args, **kwargs):
        self.controllers = list()  # Objects meant to be controlled by the user
        self.inputs = list()  # Objects meant to be controlled by other components
        self.outputs = list()  # Objects meant to be controlling other components

    def __repr__(self):
        return '<{}.{}: {}>'.format(self.__class__.__module__, self.__class__.__name__, self.asdict())

    def __iter__(self):
        return iter(self.asdict())

    def items(self):
        return self.asdict().items()

    def values(self):
        return self.asdict().values()

    def keys(self):
        return self.asdict().keys()

    def asdict(self):  # type: () -> dict
        return dict()

    def asmirroreddict(self, *args, **kwargs):  # type: (...) -> dict
        return self.asdict()

    def mirrored(self, *args, **kwargs):  # type: (...) -> RBaseComponent
        return self.__class__(**self.asmirroreddict(*args, **kwargs))

    def create(self):  # type: () -> None
        pass


class RBaseRig(object):

    def __init__(self):
        self.components = list()

    def __iter__(self):
        return iter(self.components)

    def __repr__(self):
        return '<{}.{}: {}>'.format(self.__class__.__module__, self.__class__.__name__, self.aslist())

    def aslist(self):
        return self.components

    def create(self):
        for component in self.components:
            component.create()
