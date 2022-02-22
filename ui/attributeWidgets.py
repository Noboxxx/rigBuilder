from PySide2 import QtWidgets, QtGui
from .utils import size, Signal
from rigBuilder.components.core import Attribute, Component


class ColorWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(ColorWidget, self).__init__(parent)
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


class AttributeWidget(QtWidgets.QWidget):

    def __init__(self, parent, componentDict):  # type: (QtWidgets.QWidget, dict) -> None
        super(AttributeWidget, self).__init__(parent)

        self.componentDict = componentDict

        self.attributeChanged = Signal()

        self.keyCombo = QtWidgets.QComboBox()
        for k, v in componentDict.items():
            self.keyCombo.addItem(k)
        self.attributeCombo = QtWidgets.QComboBox()
        self.indexSpin = QtWidgets.QSpinBox()

        self.keyCombo.currentTextChanged.connect(self.keyChanged)
        self.keyChanged(self.keyCombo.currentText())

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.keyCombo)
        mainLayout.addWidget(self.attributeCombo)
        mainLayout.addWidget(self.indexSpin)

        self.setLayout(mainLayout)

        self.keyCombo.currentTextChanged.connect(self.emitAttributeChanged)
        self.attributeCombo.currentTextChanged.connect(self.emitAttributeChanged)
        self.indexSpin.valueChanged.connect(self.emitAttributeChanged)

    def setAttr(self, attribute):  # type: (Attribute) -> None

        index = self.keyCombo.findText(attribute.key)
        self.keyCombo.setCurrentIndex(index)

        index = self.attributeCombo.findText(attribute.attribute)
        self.attributeCombo.setCurrentIndex(index)

        self.indexSpin.setValue(attribute.index)

    def keyChanged(self, key):
        currentComponent = self.componentDict[key]  # type: Component

        self.attributeCombo.clear()
        for k, v in currentComponent.getPlugDict().items():
            self.attributeCombo.addItem(k)

        self.indexSpin.setValue(0)

    def getAttr(self):  # type: () -> Attribute
        key = self.keyCombo.currentText()
        attribute = self.attributeCombo.currentText()
        index = self.indexSpin.value()

        return Attribute(key, attribute, index)

    def emitAttributeChanged(self):
        self.attributeChanged.emit(self.getAttr())


