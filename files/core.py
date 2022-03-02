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
    cl = '{}.{}'.format(o.__module__, o.__class__.__name__)
    return {'class': cl, 'kwargs': dict(o)}


def customDecoder(pairs):
    d = MyOrderedDict(pairs)

    if 'class' in d.keys() and 'kwargs' in d.keys():
        return objectFactory(d['class'], d['kwargs'])

    return d


class JsonFile(File):

    def dump(self, obj, force=False):  # type: (any, bool) -> None
        if os.path.exists(self) and force is False:
            raise RuntimeError('The path already exists. Use -force to override it -> {}'.format(self))

        self.dumps(obj)  # ensure that data is dump-able before dumping it.

        with open(str(self), 'w') as f:
            json.dump(obj, f, indent=4, default=customEncoder)

    def load(self):  # type: () -> any
        with open(str(self), 'r') as f:
            return json.load(f, object_pairs_hook=customDecoder)

    @staticmethod
    def dumps(obj):
        json.dumps(obj, indent=4, default=customEncoder)

    @staticmethod
    def loads(string):
        return json.loads(string, object_pairs_hook=customDecoder)
