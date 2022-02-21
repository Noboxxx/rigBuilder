from functools import partial
from PySide2 import QtWidgets
from .attributeWidgets import ColorWidget
from .dataDictEditor import DataDictEditor, DataList, DataAttributeEditor
from .jsonFileWindow import JsonFileWindow
from ..components.core import ComponentBuilder
from ..types import Color, Side, UnsignedInt, UnsignedFloat


class ComponentAttributeEditor(DataAttributeEditor):

    def getAttributeWidget(self, key, value):

        t = type(value)

        if isinstance(value, Color):
            widget = ColorWidget(self)
            widget.setColor(value)
            widget.colorChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        elif isinstance(value, Side):
            widget = QtWidgets.QComboBox(self)
            for side in Side.mirrorTable:
                widget.addItem(side)
            widget.currentTextChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            index = widget.findText(value)
            widget.setCurrentIndex(index)
            return widget

        elif isinstance(value, UnsignedInt):
            widget = QtWidgets.QSpinBox(self)
            widget.setValue(value)
            widget.valueChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        elif isinstance(value, UnsignedFloat):
            widget = QtWidgets.QDoubleSpinBox(self)
            widget.setValue(value)
            widget.valueChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        return super(ComponentAttributeEditor, self).getAttributeWidget(key, value)


class ComponentBuilderWindow(JsonFileWindow):

    def __init__(self):
        super(ComponentBuilderWindow, self).__init__(title='Component Builder')

        self.editor = DataDictEditor(dataList=DataList(), dataAttributeEditor=ComponentAttributeEditor())

        tab = QtWidgets.QTabWidget()
        tab.addTab(self.editor, 'components')
        tab.addTab(QtWidgets.QWidget(), 'connections')

        self.mainLayout.addWidget(tab)

    def refresh(self, obj):  # type: (ComponentBuilder) -> None
        print obj.componentDict
        self.editor.refresh(obj.componentDict)

    def getData(self):  # type: () -> ComponentBuilder
        componentDict = self.editor.getDataDict()
        connectionList = list()
        return ComponentBuilder(componentDict, connectionList)
