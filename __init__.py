import json
import os


def get(value, defaultValue):
    if value is None:
        return defaultValue
    return value


class RBaseComponent(object):

    def __init__(self, *args, **kwargs):
        self.controllers = list()  # Objects meant to be controlled by the user
        self.inputs = list()  # Objects meant to be controlled by other components
        self.outputs = list()  # Objects meant to be controlling other components

    def __repr__(self):
        return '<{}.{}: {}>'.format(self.__class__.__module__, self.__class__.__name__, self.asdict())

    def asdict(self):  # type: () -> dict
        return dict()

    def asmirroreddict(self, *args, **kwargs):  # type: (...) -> dict
        return self.asdict()

    def mirrored(self, *args, **kwargs):  # type: (...) -> RBaseComponent
        return self.__class__(**self.asmirroreddict(*args, **kwargs))

    def create(self):  # type: () -> None
        pass


class JsonFile(object):
    """
    A simple interface to dump and load a json file safely.
    """

    def __init__(self, path):
        self.path = str(path)

    def __repr__(self):
        return '<{}.{}: {}>'.format(self.__class__.__module__, self.__class__.__name__, self.path)

    def dump(self, data, force=False, indent=4):
        if os.path.exists(self.path) and force is False:
            raise RuntimeError('The path already exists. Use -force to override it -> {}'.format(self.path))

        json.dumps(data, indent=indent)  # ensure that the data is dump-able before dumping it.

        with open(self.path, 'w') as f:
            json.dump(data, f, indent=indent)

    def load(self):
        with open(self.path, 'r') as f:
            return json.load(f)
