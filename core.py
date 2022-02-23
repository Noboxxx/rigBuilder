from inspect import getargspec


class MyOrderedDict(object):
    def __init__(self):
        self._ls = list()

    def keys(self):
        keys = list()
        for k, _ in self._ls:
            keys.append(k)
        return tuple(keys)

    def values(self):
        values = list()
        for k, v in self._ls:
            values.append(v)
        return tuple(values)

    def items(self):
        return tuple(self._ls)

    def get(self, key, default=None):
        if key in self.keys():
            return self[key]
        return default

    def __iter__(self):
        return iter(self.items())

    def __getitem__(self, item):
        for k, v in self.items():
            if item == k:
                return v
        raise KeyError('Key \'{}\' not found.'.format(item))

    def __setitem__(self, key, value):
        if key in self.keys():
            ls = list()
            for k, v in self.items():
                if key == k:
                    v = value
                ls.append((k, v))
            self._ls = ls
        else:
            self._ls.append((key, value))


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

        for cl in list(self.__class__.__bases__) + [self.__class__]:
            if cl is object:
                continue
            argSpec = getargspec(cl.__init__).args
            args += argSpec[1:]

        return args

    def values(self):
        return [self.__getattribute__(k) for k in self.keys()]

    def items(self):
        return zip(self.keys(), self.values())

    def copy(self):
        return self.__class__(**dict(self))