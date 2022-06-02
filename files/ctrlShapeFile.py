from maya import cmds
from rigBuilder.files.core import JsonFile


class CtrlShapeFile(JsonFile):

    def export(self, ctrls=None, force=False):
        data = dict()

        if ctrls is None:
            ctrls = cmds.ls(sl=True, type='transform')

        for ctrl in ctrls:
            shapes = cmds.listRelatives(ctrl, shapes=True, type='nurbsCurve')

            if not shapes:
                continue

            shapesData = dict()
            for shape in shapes:
                degree = cmds.getAttr('{}.degree'.format(shape))
                spans = cmds.getAttr('{}.spans'.format(shape))
                periodic = cmds.getAttr('{}.form'.format(shape)) == 2

                points = list()

                r = range(spans) if periodic else range(spans + degree)

                for index in r:
                    point = cmds.pointPosition('{}.cv[{}]'.format(shape, index), local=True)
                    points.append(point)

                shapesData[shape] = {
                    'isRgb': cmds.getAttr('{}.overrideRGBColors'.format(shape)),
                    'rgbColor': cmds.getAttr('{}.overrideColorRGB'.format(shape))[0],
                    'indexColor': cmds.getAttr('{}.overrideColor'.format(shape)),
                    'points': points,
                    'degree': degree,
                    'periodic': periodic
                }

            data[ctrl] = {
                'isRgb': cmds.getAttr('{}.overrideRGBColors'.format(ctrl)),
                'rgbColor': cmds.getAttr('{}.overrideColorRGB'.format(ctrl))[0],
                'indexColor': cmds.getAttr('{}.overrideColor'.format(ctrl)),
                'shapes': shapesData,
            }

        self.dump(data, force=force)

    def import_(self, scale=1.0):
        data = self.load()

        for ctrl, shapesData in data.items():
            if not cmds.objExists(ctrl):
                continue

            cmds.delete(cmds.listRelatives(ctrl, shapes=True, type='nurbsCurve'))

            for shape, shapeData in shapesData.get('shapes', dict()).items():
                periodic = shapeData.get('periodic', False)
                points = [tuple(v * scale for v in point) for point in shapeData.get('points', list())]
                degree = shapeData.get('degree', 1)
                isRgb = shapeData.get('isRgb', False)
                indexColor = shapeData.get('indexColor', 0)
                rgbColor = shapeData.get('rgbColor', (0, 0, 0))

                if not periodic:
                    knots = range(len(points) - degree + 1)

                    for i in range(degree - 1):
                        knots.append(knots[-1])
                        knots.insert(0, knots[0])
                else:
                    for i in range(degree):
                        points.append(points[i])
                    knots = range(len(points) + degree - 1)

                curve = cmds.curve(point=points, degree=degree, knot=knots, periodic=periodic)
                s = cmds.listRelatives(curve, shapes=True)[0]
                s = cmds.rename(s, shape)

                cmds.setAttr('{}.overrideEnabled'.format(s), True)
                cmds.setAttr('{}.overrideRGBColors'.format(s), isRgb)
                cmds.setAttr('{}.overrideColor'.format(s), indexColor)
                cmds.setAttr('{}.overrideColorRGB'.format(s), *rgbColor)

                cmds.parent(s, ctrl, r=True, s=True)
                cmds.delete(curve)
