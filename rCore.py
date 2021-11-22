def mirror(value):
    """
    Mirror the given value by using its __mirror__ method
    :param value: any
    :return: any
    """
    return value.__mirror__()


class RComponent(object):
    """
    Data structure making creation of a component and mirroring it easier.

    asdict():
        Should be re-implemented to return a dict containing all arguments (key, value) passed to __init__()
    """

    def __init__(self, *args, **kwargs):
        pass

    def asdict(self):  # type: () -> dict
        """
        Should be re-implemented to return a dict containing all arguments (key, value) passed to __init__()
        :return: dict
        """
        return dict()

    def asmirroreddict(self):  # type: () -> dict
        """
        Return a dict containing the mirror() method every value of asdict() method.
        :return: dict
        """
        mirroredData = dict()
        for key, value in self.asdict():
            try:
                mirroredData[key] = mirror(value)
            except:
                mirroredData[key] = value

        return mirroredData

    def __mirror__(self):  # type: () -> Component
        """
        Return a new mirrored instance based on asmirroreddict()
        :return: Component
        """
        return self.__class__(**self.asmirroreddict())
