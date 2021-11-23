def getCheckedValue(value, defaultValue=None, types=None):  # type: (any, any or None, type or (type,) or None) -> any
    """
    If value is None the given default value will be returned.
    Value and default value should be an instance of the given types (if set).
    :param value: any
    :param defaultValue: any
    :param types: type or (type,) or None
    :return: any
    """
    # if value is None:
    #     value = defaultValue
    #
    # if types is not None:
    #     if not isinstance(value, types):
    #         raise TypeError(
    #             '\'{}\' should be of type \'{}\' not \'{}\''.format(
    #                 value,
    #                 types,
    #                 type(value).__name__
    #             )
    #         )

    return value


def mirror(value):  # type: (any) -> any
    """
    Mirror the given value by using its __mirror__ method
    :param value: any
    :return: any
    """
    return value.__mirror__()


class RBaseComponent(object):
    """
    Data structure making creation of a component and mirroring it easier.
    """

    def __init__(self, *args, **kwargs):
        self.controllers = list()  # Objects meant to be controlled by the user
        self.inputs = list()  # Objects meant to be controlled by other components
        self.outputs = list()  # Objects meant to be controlling other components

    def __str__(self):
        return str(self.asdict())

    def __repr__(self):
        return repr(self.asdict())

    def asdict(self):  # type: () -> dict
        """
        Should be re-implemented to return a dict containing all arguments (key, value) passed to __init__()
        :return: dict
        """
        return dict()

    def asmirroreddict(self):  # type: () -> dict
        """
        Return a dict containing each value mirrored from asdict() by calling on each mirror().
        If the value cannot be mirrored then the original value is returned.
        :return: dict
        """
        mirroredData = dict()
        for key, value in self.asdict().items():

            try:
                mirroredData[key] = mirror(value)
            except AttributeError:
                mirroredData[key] = value

        return mirroredData

    def __mirror__(self):  # type: () -> RBaseComponent
        """
        Return a mirrored instance of the component by calling asmirrordict().
        :return: Component
        """
        return self.__class__(**self.asmirroreddict())

    def create(self):  # type: () -> None
        """
        Method that creates the component who needs to be re-implemented.
        :return:
        """
        pass

