from functools import partial
from PySide2 import QtWidgets
from .attributeWidgets import ColorWidget, AttributeWidget, AttributesWidget
from .dataDictEditor import DataDictEditor, DataDictList, DataAttributeEditor
from .jsonFileWindow import JsonFileWindow
from ..components.core import ComponentBuilder, Attribute, Attributes, Connection
from ..components.oneCtrl import OneCtrl
from ..types import Color, Side, UnsignedInt, UnsignedFloat


class ConnectionAttributeEditor(DataAttributeEditor):

    def __init__(self, getComponentDictFunc):
        super(ConnectionAttributeEditor, self).__init__()
        self.getComponentDictFunc = getComponentDictFunc

    def getAttributeWidget(self, key, value):

        t = type(value)

        if isinstance(value, Attribute):
            widget = AttributeWidget(self, self.getComponentDictFunc())
            widget.setAttr(value)
            widget.attributeChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        if isinstance(value, Attributes):
            widget = AttributesWidget()
            widget.setAttrs(value, self.getComponentDictFunc())
            return widget

        return super(ConnectionAttributeEditor, self).getAttributeWidget(key, value)


class ComponentAttributeEditor(DataAttributeEditor):

    def getAttributeWidget(self, key, value):

        t = type(value)

        if isinstance(value, Color):
            widget = ColorWidget()
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


class ComponentDictList(DataDictList):

    types = [
        OneCtrl
    ]

    def populateContextMenu(self):

        createGuidesAction = QtWidgets.QAction('Create Guides', self)
        createGuidesAction.triggered.connect(self.createGuides)
        if not self.selectedItems():
            createGuidesAction.setEnabled(False)

        menu = super(ComponentDictList, self).populateContextMenu()
        menu.addSeparator()
        menu.addAction(createGuidesAction)

        return menu

    def createGuides(self):
        for item in self.selectedItems():
            item.d.createGuides(item.text(0))

        self.emitCurrentDataChanged(self.currentItem())


class ConnectionDictList(DataDictList):

    types = [
        Connection
    ]


class ComponentBuilderWindow(JsonFileWindow):

    def __init__(self):
        super(ComponentBuilderWindow, self).__init__(title='Component Builder')

        self.componentEditor = DataDictEditor(
            dataDictList=ComponentDictList(),
            dataAttributeEditor=ComponentAttributeEditor()
        )

        self.connectionEditor = DataDictEditor(
            dataDictList=ConnectionDictList(),
            dataAttributeEditor=ConnectionAttributeEditor(self.componentEditor.getDataDict),
        )

        tab = QtWidgets.QTabWidget()
        tab.addTab(self.componentEditor, 'components')
        tab.addTab(self.connectionEditor, 'connections')

        buildBtn = QtWidgets.QPushButton('Build')
        buildBtn.clicked.connect(self.build)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tab)
        layout.addWidget(buildBtn)

        self.mainLayout.addLayout(layout)

    def refresh(self, obj):  # type: (ComponentBuilder) -> None
        self.componentEditor.refresh(obj.componentDict)
        self.connectionEditor.refresh(obj.connectionDict)

    def getData(self):  # type: () -> ComponentBuilder
        componentDict = self.componentEditor.getDataDict()
        connectionDict = self.connectionEditor.getDataDict()
        return ComponentBuilder(componentDict, connectionDict)

    def build(self):
        self.getData().build()