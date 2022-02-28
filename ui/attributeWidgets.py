import os

from PySide2 import QtWidgets, QtGui
from .utils import size, Signal
from rigBuilder.components.core import Attribute, Component, Attributes, Guide
from ..types import File


class AttributeWidget(QtWidgets.QWidget):

    def __init__(self):
        super(AttributeWidget, self).__init__()

        self.valueChanged = Signal()

    @property
    def value(self):
        return None

    @value.setter
    def value(self, value):
        pass


class ColorWidget(QtWidgets.QWidget):

    def __init__(self):
        super(ColorWidget, self).__init__()
        self.colorChanged = Signal()

        self.redSpinBox = QtWidgets.QSpinBox()
        self.redSpinBox.setMaximum(255)

        self.greenSpinBox = QtWidgets.QSpinBox()
        self.greenSpinBox.setMaximum(255)

        self.blueSpinBox = QtWidgets.QSpinBox()
        self.blueSpinBox.setMaximum(255)

        self.pickerBtn = QtWidgets.QPushButton()
        self.pickerBtn.setFixedSize(size(14), size(14))
        self.pickerBtn.clicked.connect(self.openColorPickerDialog)

        layout = QtWidgets.QHBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.redSpinBox)
        layout.addWidget(self.greenSpinBox)
        layout.addWidget(self.blueSpinBox)
        layout.addWidget(self.pickerBtn)

        self.redSpinBox.valueChanged.connect(self.emitColorChanged)
        self.redSpinBox.valueChanged.connect(self.updateBtnColor)

        self.greenSpinBox.valueChanged.connect(self.emitColorChanged)
        self.greenSpinBox.valueChanged.connect(self.updateBtnColor)

        self.blueSpinBox.valueChanged.connect(self.emitColorChanged)
        self.blueSpinBox.valueChanged.connect(self.updateBtnColor)

        self.setLayout(layout)

    def emitColorChanged(self):
        self.colorChanged.emit(self.color())

    def updateBtnColor(self):
        color = self.color()
        pixmap = QtGui.QPixmap(size(32), size(32))
        pixmap.fill(QtGui.QColor(*color))
        self.pickerBtn.setIcon(QtGui.QIcon(pixmap))

    def setSpinBoxesColor(self, color):
        self.redSpinBox.setValue(color[0])
        self.greenSpinBox.setValue(color[1])
        self.blueSpinBox.setValue(color[2])

    def setColor(self, color):
        self.setSpinBoxesColor(color)
        self.updateBtnColor()

    def color(self):
        return self.redSpinBox.value(), self.greenSpinBox.value(), self.blueSpinBox.value()

    def openColorPickerDialog(self):
        dialog = QtWidgets.QColorDialog()
        dialog.setCurrentColor(QtGui.QColor(*self.color()))
        if dialog.exec_():
            qColor = dialog.currentColor()
            color = qColor.red(), qColor.green(), qColor.blue()
            self.setColor(color)
        return dialog


class AttributesWidget(QtWidgets.QWidget):

    def __init__(self):
        super(AttributesWidget, self).__init__()

        addBtn = QtWidgets.QPushButton('+')
        addBtn.setFixedSize(size(15), size(15))

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.addWidget(addBtn)

        self.setLayout(self.mainLayout)

    def setAttrs(self, attributes, componentDict):  # type: (Attributes, dict[str: Component]) -> None
        for attr in attributes:
            wid = AttributeWidget(self, componentDict)
            wid.setAttr(attr)

            removeBtn = QtWidgets.QPushButton('x')
            removeBtn.setFixedSize(size(15), size(15))

            lay = QtWidgets.QHBoxLayout()
            lay.setMargin(0)
            lay.addWidget(wid)
            lay.addWidget(removeBtn)

            self.mainLayout.addLayout(lay)


class AttributeWidget(QtWidgets.QWidget):

    def __init__(self, parent, componentDict):  # type: (QtWidgets.QWidget, dict[str: Component]) -> None
        super(AttributeWidget, self).__init__(parent)

        self.componentDict = componentDict

        self.attributeChanged = Signal()

        self.keyCombo = QtWidgets.QComboBox()
        for k, v in componentDict.items():
            self.keyCombo.addItem(k)
        self.attributeCombo = QtWidgets.QComboBox()
        self.indexSpin = QtWidgets.QSpinBox()
        self.indexSpin.setMaximum(10000)
        self.indexSpin.setMinimum(-10000)

        self.keyCombo.currentTextChanged.connect(self.keyChanged)
        self.keyChanged(self.keyCombo.currentText())

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setMargin(0)
        mainLayout.addWidget(self.keyCombo)
        mainLayout.addWidget(self.attributeCombo)
        mainLayout.addWidget(self.indexSpin)

        self.setLayout(mainLayout)

        self.keyCombo.currentTextChanged.connect(self.emitAttributeChanged)
        self.attributeCombo.currentTextChanged.connect(self.emitAttributeChanged)
        self.indexSpin.valueChanged.connect(self.emitAttributeChanged)

    def setAttr(self, attribute):  # type: (Attribute) -> None

        if attribute.key == '':
            self.keyCombo.setCurrentIndex(-1)
        else:
            index = self.keyCombo.findText(attribute.key)
            if index == -1:
                self.keyCombo.addItem(attribute.key)
                index = self.keyCombo.findText(attribute.key)

            self.keyCombo.setCurrentIndex(index)

        if attribute.attribute == '':
            self.attributeCombo.setCurrentIndex(-1)
        else:
            index = self.attributeCombo.findText(attribute.attribute)
            if index == -1:
                self.attributeCombo.addItem(attribute.attribute)
                index = self.attributeCombo.findText(attribute.attribute)

            self.attributeCombo.setCurrentIndex(index)

        self.indexSpin.setValue(attribute.index)

    def keyChanged(self, key):
        currentComponent = self.componentDict.get(key)

        self.attributeCombo.clear()
        if not isinstance(currentComponent, Component):
            return

        for k, v in currentComponent.getPlugDict().items():
            self.attributeCombo.addItem(k)

    def getAttr(self):  # type: () -> Attribute
        key = self.keyCombo.currentText()
        attribute = self.attributeCombo.currentText()
        index = self.indexSpin.value()

        return Attribute(key, attribute, index)

    def emitAttributeChanged(self):
        self.attributeChanged.emit(self.getAttr())


class ScriptWidget(QtWidgets.QWidget):

    def __init__(self):
        super(ScriptWidget, self).__init__()

        self.textChanged = Signal()

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.textChanged.connect(self.emitTextChanged)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setMargin(0)
        mainLayout.addWidget(self.textEdit)

    def setText(self, text):
        self.textEdit.setText(text)

    def emitTextChanged(self):
        self.textChanged.emit(self.textEdit.toPlainText())


class FileWidget(QtWidgets.QWidget):

    def __init__(self, flt):
        super(FileWidget, self).__init__()

        self.filter = flt

        self.pathChanged = Signal()

        self.pathEdit = QtWidgets.QLineEdit()
        self.pathEdit.textChanged.connect(self.emitPathChanged)

        openBtn = QtWidgets.QPushButton()
        openBtn.setFixedSize(size(20), size(20))
        openBtn.setIcon(QtGui.QIcon(':openLoadGeneric.png'))
        openBtn.clicked.connect(self.askOpen)

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.addWidget(self.pathEdit)
        self.mainLayout.addWidget(openBtn)

        self.setLayout(self.mainLayout)

    def setPath(self, path):
        self.pathEdit.setText(os.path.normpath(path))

    def askOpen(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption='Open File', filter=self.filter)
        if not path:
            return

        self.setPath(File(path))

    def emitPathChanged(self):
        self.pathChanged.emit(os.path.normpath(self.pathEdit.text()))


class ComponentBuilderWidget(FileWidget):

    def __init__(self, flt):
        super(ComponentBuilderWidget, self).__init__(flt)

        editBtn = QtWidgets.QPushButton()
        editBtn.setFixedSize(size(20), size(20))
        editBtn.setIcon(QtGui.QIcon(':toolSettings.png'))
        editBtn.clicked.connect(self.openEdit)

        self.mainLayout.addWidget(editBtn)

    def openEdit(self):
        from .componentBuilderWindow import ComponentBuilderWindow
        ui = ComponentBuilderWindow()
        ui.open(self.pathEdit.text())
        ui.show()


class NodeWidget(QtWidgets.QWidget):

    def __init__(self):
        super(NodeWidget, self).__init__()

        self.nodeChanged = Signal()

        self.nodeEdit = QtWidgets.QLineEdit()
        self.nodeEdit.textChanged.connect(self.nodeChanged.emit)

        pickBtn = QtWidgets.QPushButton()
        pickBtn.setIcon(QtGui.QIcon(':arrowLeft.png'))
        pickBtn.setFixedSize(size(20), size(20))
        pickBtn.clicked.connect(self.pick)

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.addWidget(self.nodeEdit)
        self.mainLayout.addWidget(pickBtn)

        self.setLayout(self.mainLayout)

    def setNode(self, node):
        self.nodeEdit.setText(node)

    def pick(self):
        from maya import cmds
        selection = cmds.ls(sl=True, long=True)

        if not selection:
            return

        self.setNode(selection[-1])


class ListWidget(QtWidgets.QWidget):

    def __init__(self, widgetType):
        super(ListWidget, self).__init__()

        self.widgetType = widgetType

        addBtn = QtWidgets.QPushButton('+')
        addBtn.setFixedSize(size(15), size(15))

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.addWidget(addBtn)

        self.setLayout(self.mainLayout)

    def setValues(self, values):  # type: (list or tuple) -> None
        for v in values:
            wid = self.addItem(v)

            removeBtn = QtWidgets.QPushButton('x')
            removeBtn.setFixedSize(size(15), size(15))

            lay = QtWidgets.QHBoxLayout()
            lay.setMargin(0)
            lay.addWidget(wid)
            lay.addWidget(removeBtn)

            self.mainLayout.addLayout(lay)

    def addItem(self, value):
        wid = self.widgetType(self)
        wid.setAttr(value)

        return wid
