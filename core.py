from inspect import getargspec


def getAllAncestors(cl, data=None):
    data = list() if data is None else data

    parents = cl.__bases__
    for parent in parents:
        data.append(parent)
        getAllAncestors(parent, data)

    return data


class Data(object):

    def __init__(self, *args, **kwargs):
        super(Data, self).__init__()

    def __iter__(self):
        return iter(self.items())

    def __getitem__(self, item):
        if item in self.keys():
            return getattr(self, item)
        else:
            raise ValueError('No item found for \'{}\''.format(item))

    def __repr__(self):
        kwargsStr = ', '.join(['{}={}'.format(k, repr(v)) for k, v in self.items()])
        return '{}({})'.format(self.__class__.__name__, kwargsStr)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.items() == other.items()

    def __ne__(self, other):
        return self.__eq__(other)

    def keys(self):
        args = list()

        for cl in getAllAncestors(self.__class__) + [self.__class__]:
            if cl is object:
                continue
            argSpec = getargspec(cl.__init__).args
            for arg in argSpec[1:]:
                if arg not in args:
                    args.append(arg)

        return args

    def values(self):
        return [self.__getattribute__(k) for k in self.keys()]

    def items(self):
        return zip(self.keys(), self.values())

    def copy(self):
        return self.__class__(**dict(self))
