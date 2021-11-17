def mirror(value):
    if hasattr(value, '__mirror__'):
        return value.__mirror__()
    return None


class PseudoDict(object):
    """
    Pseudo dict act exactly like a dict but it is possible to get keys as a field:
        >>> pseudoDict = PseudoDict(firstName='Pierre', lastName='Laurent')
        >>>
        >>> # getting
        >>> print pseudoDict['firstName']
        >>> print pseudoDict.firstName

    Flaws:
        - auto-completion doesn't work properly
        - adding a field from outside the class will not be properly handeled:
            >>> pseudoDict.plop = None
    """

    def __init__(self, *args, **kwargs):
        self.attributes = list()
        for key, value in kwargs.items():
            self.__setattr__(key, value)
            self.attributes.append(key)

    def __iter__(self):
        return iter(self.asdict())

    def __str__(self):
        return str(self.asdict())

    def __repr__(self):
        return repr(self.asdict())

    def __setitem__(self, key, value):
        self.__setattr__(key, value)
        if key not in self.attributes:
            self.attributes.append(key)

    def __getitem__(self, item):
        return self.asdict()[item]

    def __eq__(self, other):
        if isinstance(other, PseudoDict):
            return other.asdict() == self.asdict()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.asdict())

    def copy(self):
        return self.__class__(**self.asdict())

    def asdict(self):
        data = dict()

        for attr in self.attributes:
            value = self.__getattribute__(attr)
            data[attr] = value

        return data

    def items(self):
        return self.asdict().items()

    def keys(self):
        return self.asdict().keys()

    def values(self):
        return self.asdict().keys()


class BaseComponent(PseudoDict):

    def __init__(self, **kwargs):
        super(BaseComponent, self).__init__(**kwargs)

        self.folder = None

        self.inputs = list()
        self.outputs = list()
        self.controllers = list()

    def __mirror__(self):
        mirroredData = dict()

        for key, value in self.items():
            mirroredValue = mirror(value)
            mirroredData[key] = value if mirroredValue is None else mirroredValue

        return self.__class__(**mirroredData)

    def create(self):
        self._initializeCreation()
        self._doCreation()
        self._finalizeCreation()

    def _initializeCreation(self):
        pass

    def _doCreation(self):
        raise NotImplementedError

    def _finalizeCreation(self):
        pass

########
# TEST #
########


from collections import namedtuple

Plop = namedtuple('Plop', ('red', 'fuck'))
plop = Plop(1, 2)
print plop.red


class Component(BaseComponent):

    # name = basestring
    # side = basestring
    # index = long, int

    def _doCreation(self):
        print '_doCreation', self


def test():
    component1 = Component(name='untitled', side='L', index=1)
    print 'name', component1['name']
    component1['plop'] = 10
    component1.plip = 11
    # print dir(component1)
    print dict(component1)
