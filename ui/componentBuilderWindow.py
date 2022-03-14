from functools import partial
from PySide2 import QtWidgets
from .attributeWidgets import ColorWidget, AttributeWidget, NodeWidget, ComboWidget, ListAttributeWidget, \
    ConnectionPlugWidget
from .dataDictEditor import DataDictEditor, DataDictList, DataAttributeEditor
from .jsonFileWindow import JsonFileWindow
from ..components.arm import Arm
from ..components.base import Base
from ..components.clavicle import Clavicle
from ..components.core import ComponentBuilder, ConnectionPlug, ConnectionPlugArray, Connection, Guide, GuideDict, GuideArray
from ..components.fkChain import FkChain
from ..components.hand import Hand
from ..components.leg import Leg
from ..components.oneCtrl import OneCtrl
from ..types import Color, Side


class ConnectionAttributeEditor(DataAttributeEditor):

    def __init__(self, getComponentDictFunc):
        super(ConnectionAttributeEditor, self).__init__()
        self.getComponentDictFunc = getComponentDictFunc

        self.typeWidgetMap = [
            (ConnectionPlug, partial(ConnectionPlugWidget, self.getComponentDictFunc)),
            (ConnectionPlugArray, partial(ListAttributeWidget, partial(ConnectionPlugWidget, self.getComponentDictFunc))),
        ] + self.typeWidgetMap


class ComponentAttributeEditor(DataAttributeEditor):

    def __init__(self):
        super(ComponentAttributeEditor, self).__init__()
        self.typeWidgetMap = [
            (Color, ColorWidget),
            (Guide, NodeWidget),
            (Side, partial(ComboWidget, Side.mirrorTable.keys())),
            (GuideArray, partial(ListAttributeWidget, NodeWidget))
        ] + self.typeWidgetMap


class ComponentDictList(DataDictList):

    types = (
        OneCtrl,
        Base,
        FkChain,
        Arm,
        Hand,
        Leg,
        Clavicle,
    )

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
        Connection,
    ]


class ComponentBuilderWindow(JsonFileWindow):

    def __init__(self, parent=None):
        super(ComponentBuilderWindow, self).__init__(parent=parent, title='Component Builder')

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

    def refresh(self, data=None):  # type: (ComponentBuilder) -> None
        data = ComponentBuilder() if data is None else data
        self.componentEditor.refresh(data.componentDict)
        self.connectionEditor.refresh(data.connectionDict)

    def getData(self):  # type: () -> ComponentBuilder
        componentDict = self.componentEditor.getDataDict()
        connectionDict = self.connectionEditor.getDataDict()
        return ComponentBuilder(componentDict, connectionDict)

    def build(self):
        self.getData().build()
