import json
import os
import importlib
from rigBuilder.core import MyOrderedDict, Data
from rigBuilder.types import File


def objectFactory(typeStr, kwargs):  # type: (str, dict) -> any
    typeStrSplit = typeStr.split('.')
    module = importlib.import_module('.'.join(typeStrSplit[:-1]))
    t = module.__getattribute__(typeStrSplit[-1])
    return t(**kwargs)


def customEncoder(o):
    if isinstance(o, MyOrderedDict):
        return {'class': 'MyrOrderedDict', 'content': o.items()}

    return {'class': '{}.{}'.format(o.__module__, o.__class__.__name__), 'kwargs': dict(o)}


def customDecoder(o):
    if isinstance(o, dict):
        if 'class' in o.keys() and 'kwargs' in o.keys():
            return objectFactory(o['class'], o['kwargs'])
        elif 'class' in o.keys() and 'content' in o.keys():
            d = MyOrderedDict()
            for k, v in o['content']:
                d[k] = v
            return d
    return o


class JsonFile(File):

    def dump(self, obj, force=False):  # type: (any, bool) -> None
        if os.path.exists(self.absolute) and force is False:
            raise RuntimeError('The path already exists. Use -force to override it -> {}'.format(self))

        self.dumps(obj)  # ensure that data is dump-able before dumping it.

        with open(str(self.absolute), 'w') as f:
            json.dump(obj, f, indent=4, default=customEncoder)

    def load(self):  # type: () -> any
        with open(self.absolute, 'r') as f:
            return json.load(f, object_hook=customDecoder)

    @staticmethod
    def dumps(obj):
        json.dumps(obj, indent=4, default=customEncoder)

    @staticmethod
    def loads(string):
        return json.loads(string, object_hook=customDecoder)
