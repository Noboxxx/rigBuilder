def __reload__():
    print('--- Reload Module ---')
    import sys

    modules = sys.modules
    for moduleName, moduleObj in modules.items():
        if moduleObj is None:
            continue
        if moduleName != 'rigBuilder' and not moduleName.startswith('rigBuilder.'):
            continue

        print('Removing Module -> {}'.format(moduleName))
        del modules[moduleName]


def test():
    from rigBuilder import RComp, RMObj
    RComp.RObj = RMObj

    from maya import cmds
    cmds.file(new=True, force=True)
    component = RComp.OneCtrl()
    component.create()
    print component
