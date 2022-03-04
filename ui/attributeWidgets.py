from functools import partial

from PySide2 import QtWidgets, QtGui
from .utils import size, Signal
from ..components.core import ConnectionPlug, Component
from ..types import File


class AttributeWidget(QtWidgets.QWidget):

    def __init__(self):
        super(AttributeWidget, self).__init__()

        self.valueChanged = Signal()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setMargin(0)
        self.setLayout(self.mainLayout)

    def getValue(self):
        return None

    def setValue(self, value):
        pass

    def emitValueChanged(self, *args, **kwargs):
        self.valueChanged.emit(self.getValue())


class ColorWidget(AttributeWidget):

    def __init__(self):
        super(ColorWidget, self).__init__()

        self.redSpinBox = QtWidgets.QSpinBox()
        self.redSpinBox.setMaximum(255)

        self.greenSpinBox = QtWidgets.QSpinBox()
        self.greenSpinBox.setMaximum(255)

        self.blueSpinBox = QtWidgets.QSpinBox()
        self.blueSpinBox.setMaximum(255)

        self.pickerBtn = QtWidgets.QPushButton()
        self.pickerBtn.setFixedSize(size(14), size(14))
        self.pickerBtn.clicked.connect(self.openColorPickerDialog)

        self.mainLayout.addWidget(self.redSpinBox)
        self.mainLayout.addWidget(self.greenSpinBox)
        self.mainLayout.addWidget(self.blueSpinBox)
        self.mainLayout.addWidget(self.pickerBtn)

        self.redSpinBox.valueChanged.connect(self.emitValueChanged)
        self.redSpinBox.valueChanged.connect(self.updateBtnColor)

        self.greenSpinBox.valueChanged.connect(self.emitValueChanged)
        self.greenSpinBox.valueChanged.connect(self.updateBtnColor)

        self.blueSpinBox.valueChanged.connect(self.emitValueChanged)
        self.blueSpinBox.valueChanged.connect(self.updateBtnColor)

    def updateBtnColor(self):
        color = self.getValue()
        pixmap = QtGui.QPixmap(size(32), size(32))
        pixmap.fill(QtGui.QColor(*color))
        self.pickerBtn.setIcon(QtGui.QIcon(pixmap))

    def setSpinBoxesColor(self, color):
        self.redSpinBox.setValue(color[0])
        self.greenSpinBox.setValue(color[1])
        self.blueSpinBox.setValue(color[2])

    def setValue(self, color):
        self.setSpinBoxesColor(list(color))
        self.updateBtnColor()

    def getValue(self):
        return self.redSpinBox.value(), self.greenSpinBox.value(), self.blueSpinBox.value()

    def openColorPickerDialog(self):
        dialog = QtWidgets.QColorDialog()
        dialog.setCurrentColor(QtGui.QColor(*self.getValue()))
        if dialog.exec_():
            qColor = dialog.currentColor()
            color = qColor.red(), qColor.green(), qColor.blue()
            self.setValue(color)
        return dialog


class ScriptWidget(AttributeWidget):

    def __init__(self):
        super(ScriptWidget, self).__init__()

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.textChanged.connect(self.emitValueChanged)

        self.mainLayout.addWidget(self.textEdit)

    def setValue(self, value):
        self.textEdit.setText(str(value))

    def getValue(self):
        return self.textEdit.toPlainText()


class FileWidget(AttributeWidget):

    def __init__(self):
        flt = ''
        super(FileWidget, self).__init__()

        self.filter = flt

        self.pathEdit = QtWidgets.QLineEdit()
        self.pathEdit.textChanged.connect(self.emitValueChanged)

        openBtn = QtWidgets.QPushButton()
        openBtn.setFixedSize(size(20), size(20))
        openBtn.setIcon(QtGui.QIcon(':openLoadGeneric.png'))
        openBtn.clicked.connect(self.askOpen)

        self.mainLayout.addWidget(self.pathEdit)
        self.mainLayout.addWidget(openBtn)

        self.setLayout(self.mainLayout)

    def setValue(self, value):
        self.pathEdit.setText(File(value))

    def getValue(self):
        return File(self.pathEdit.text())

    def askOpen(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption='Open File', filter=self.filter)
        if not path:
            return

        self.setValue(path)


class ComponentBuilderWidget(FileWidget):

    def __init__(self):
        super(ComponentBuilderWidget, self).__init__()

        editBtn = QtWidgets.QPushButton()
        editBtn.setFixedSize(size(20), size(20))
        editBtn.setIcon(QtGui.QIcon(':toolSettings.png'))
        editBtn.clicked.connect(self.openEdit)

        self.mainLayout.addWidget(editBtn)

    def openEdit(self):
        from .componentBuilderWindow import ComponentBuilderWindow
        ui = ComponentBuilderWindow(self)
        path = self.getValue()
        if path:
            ui.open(path)
        ui.show()


class NodeWidget(AttributeWidget):

    def __init__(self):
        super(NodeWidget, self).__init__()

        self.nodeEdit = QtWidgets.QLineEdit()

        pickBtn = QtWidgets.QPushButton()
        pickBtn.setIcon(QtGui.QIcon(':arrowLeft.png'))
        pickBtn.setFixedSize(size(20), size(20))
        pickBtn.clicked.connect(self.pick)

        self.mainLayout.addWidget(self.nodeEdit)
        self.mainLayout.addWidget(pickBtn)

        self.nodeEdit.textChanged.connect(self.emitValueChanged)

    def setValue(self, node):
        self.nodeEdit.setText(str(node))

    def getValue(self):
        return self.nodeEdit.text()

    def pick(self):
        from maya import cmds
        selection = cmds.ls(sl=True, long=True)

        if not selection:
            return

        self.setValue(selection[-1])


class BoolWidget(AttributeWidget):
    def __init__(self):
        super(BoolWidget, self).__init__()

        self.check = QtWidgets.QCheckBox()
        self.check.stateChanged.connect(self.emitValueChanged)

        self.mainLayout.addWidget(self.check)

    def getValue(self):
        return self.check.isChecked()

    def setValue(self, value):
        self.check.setChecked(bool(value))


class StringWidget(AttributeWidget):
    def __init__(self):
        super(StringWidget, self).__init__()

        self.line = QtWidgets.QLineEdit()
        self.line.textChanged.connect(self.emitValueChanged)

        self.mainLayout.addWidget(self.line)

    def getValue(self):
        return self.line.text()

    def setValue(self, value):
        self.line.setText(str(value))


class DefaultWidget(AttributeWidget):

    def __init__(self):
        super(DefaultWidget, self).__init__()

        self.line = QtWidgets.QLineEdit()
        self.line.setEnabled(False)

        self.mainLayout.addWidget(self.line)

    def getValue(self):
        return self.line.text()

    def setValue(self, value):
        self.line.setText(str(value))


class FloatWidget(AttributeWidget):
    def __init__(self):
        super(FloatWidget, self).__init__()

        self.spin = QtWidgets.QDoubleSpinBox()
        self.spin.setMinimum(-10000.0)
        self.spin.setMaximum(10000.0)
        self.spin.valueChanged.connect(self.emitValueChanged)

        self.mainLayout.addWidget(self.spin)

    def getValue(self):
        return self.spin.value()

    def setValue(self, value):
        self.spin.setValue(float(value))


class IntWidget(AttributeWidget):
    def __init__(self):
        super(IntWidget, self).__init__()

        self.spin = QtWidgets.QSpinBox()
        self.spin.setMinimum(-10000)
        self.spin.setMaximum(10000)
        self.spin.valueChanged.connect(self.emitValueChanged)

        self.mainLayout.addWidget(self.spin)

    def getValue(self):
        return self.spin.value()

    def setValue(self, value):
        self.spin.setValue(int(value))


class ComboWidget(AttributeWidget):

    def __init__(self, choices=None):
        super(ComboWidget, self).__init__()
        self.combo = QtWidgets.QComboBox()
        for choice in choices or list():
            self.combo.addItem(choice)

        self.combo.currentTextChanged.connect(self.emitValueChanged)

        self.mainLayout.addWidget(self.combo)

    def setValue(self, value):
        index = self.combo.findText(str(value))
        self.combo.setCurrentIndex(index)

    def getValue(self):
        return self.combo.currentText()


class ListAttributeWidget(AttributeWidget):

    def __init__(self, t):
        super(ListAttributeWidget, self).__init__()

        self.t = t

        self.widgets = list()

        addBtn = QtWidgets.QPushButton('+')
        addBtn.setFixedSize(size(20), size(20))
        addBtn.clicked.connect(self.addItem)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(addBtn)

        self.mainLayout.addLayout(self.layout)

    def addItem(self):
        wid = self.t()  # type: AttributeWidget
        wid.valueChanged.connect(self.emitValueChanged)
        self.widgets.append(wid)

        self.emitValueChanged()

        removeBtn = QtWidgets.QPushButton('x')
        removeBtn.setFixedSize(size(20), size(20))

        lay = QtWidgets.QHBoxLayout()
        lay.setMargin(0)
        lay.addWidget(wid)
        lay.addWidget(removeBtn)

        removeBtn.clicked.connect(partial(self.removeItem, lay, wid, removeBtn))

        self.layout.addLayout(lay)

        return wid

    def removeItem(self, layout, widget, removeBtn):
        self.widgets.remove(widget)
        self.emitValueChanged()
        layout.deleteLater()
        widget.deleteLater()
        removeBtn.deleteLater()

    def getValue(self):
        return [wid.getValue() for wid in self.widgets]

    def setValue(self, value):  # type: (list or tuple) -> None
        for v in value:
            wid = self.addItem()
            wid.setValue(v)


class ConnectionPlugWidget(AttributeWidget):

    def __init__(self, func=None):  # type: (dict[str: Component]) -> None
        super(ConnectionPlugWidget, self).__init__()

        self.componentDict = dict() if func is None else func()

        self.keyCombo = QtWidgets.QComboBox()
        for k, v in self.componentDict.items():
            self.keyCombo.addItem(k)
        self.attributeCombo = QtWidgets.QComboBox()
        self.indexSpin = QtWidgets.QSpinBox()
        self.indexSpin.setMaximum(10000)
        self.indexSpin.setMinimum(-10000)

        self.keyCombo.currentTextChanged.connect(self.keyChanged)
        self.keyChanged(self.keyCombo.currentText())

        # mainLayout = QtWidgets.QHBoxLayout()
        # mainLayout.setMargin(0)
        self.mainLayout.addWidget(self.keyCombo)
        self.mainLayout.addWidget(self.attributeCombo)
        self.mainLayout.addWidget(self.indexSpin)

        # self.setLayout(mainLayout)

        self.keyCombo.currentTextChanged.connect(self.emitValueChanged)
        self.attributeCombo.currentTextChanged.connect(self.emitValueChanged)
        self.indexSpin.valueChanged.connect(self.emitValueChanged)

    def setValue(self, value):  # type: (ConnectionPlug) -> None

        if value.key == '':
            self.keyCombo.setCurrentIndex(-1)
        else:
            index = self.keyCombo.findText(value.key)
            if index == -1:
                self.keyCombo.addItem(value.key)
                index = self.keyCombo.findText(value.key)

            self.keyCombo.setCurrentIndex(index)

        if value.attribute == '':
            self.attributeCombo.setCurrentIndex(-1)
        else:
            index = self.attributeCombo.findText(value.attribute)
            if index == -1:
                self.attributeCombo.addItem(value.attribute)
                index = self.attributeCombo.findText(value.attribute)

            self.attributeCombo.setCurrentIndex(index)

        self.indexSpin.setValue(value.index)

    def keyChanged(self, key):
        currentComponent = self.componentDict.get(key)

        self.attributeCombo.clear()
        if not isinstance(currentComponent, Component):
            return

        for k, v in currentComponent.getStorageDict().items():
            self.attributeCombo.addItem(k)

    def getValue(self):  # type: () -> ConnectionPlug
        key = self.keyCombo.currentText()
        attribute = self.attributeCombo.currentText()
        index = self.indexSpin.value()

        return ConnectionPlug((key, attribute, index))
