from functools import partial
from PySide2 import QtWidgets
from .utils import size, Signal
from ..core import Data, MyOrderedDict


class DataAttributeEditor(QtWidgets.QTreeWidget):

    def __init__(self):
        super(DataAttributeEditor, self).__init__()

        self.setHeaderLabels(('name', 'value', 'type'))
        self.setColumnWidth(1, size(200))

        self.attributeValueChanged = Signal()

    def refresh(self, data):  # type: (Data) -> None
        self.clear()
        for k, v in data.items():
            self.addAttribute(k, v)

    def addAttribute(self, key, value, parent=None, shortAttr=None):
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, str(shortAttr) if shortAttr is not None else str(key))
        item.setText(2, value.__class__.__name__)

        if parent is None:
            self.addTopLevelItem(item)
        else:
            parent.addChild(item)

        widget = self.getAttributeWidget(key, value)

        layout = QtWidgets.QVBoxLayout()
        layout.setMargin(size(6))
        layout.addWidget(widget)

        itemWidget = QtWidgets.QWidget(self)
        itemWidget.setLayout(layout)

        self.setItemWidget(item, 1, itemWidget)

        item.setExpanded(True)

    def getAttributeWidget(self, key, value):
        t = type(value)

        if isinstance(value, bool):
            check = QtWidgets.QCheckBox()
            check.setChecked(value)
            check.stateChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return check

        elif isinstance(value, basestring):
            line = QtWidgets.QLineEdit()
            line.setText(value)
            line.textChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return line

        elif isinstance(value, int):
            spin = QtWidgets.QSpinBox()
            spin.setMinimum(-10000)
            spin.setMaximum(10000)
            spin.setValue(value)
            spin.valueChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return spin

        elif isinstance(value, float):
            spin = QtWidgets.QDoubleSpinBox()
            spin.setMinimum(-10000.0)
            spin.setMaximum(10000.0)
            spin.setValue(value)
            spin.valueChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return spin

        else:
            line = QtWidgets.QLineEdit()
            line.setText(str(value))
            line.setEnabled(False)
            return line


class DataDictList(QtWidgets.QTreeWidget):

    types = list()

    def __init__(self):
        super(DataDictList, self).__init__()
        self.setHeaderLabels(('key', 'type'))
        self.setColumnWidth(1, size(50))

        self.currentDataChanged = Signal()
        self.currentItemChanged.connect(self.emitCurrentDataChanged)

    def setAttributeValue(self, key, t, value):
        item = self.currentItem()

        if isinstance(value, (tuple, list)):
            value = t(*value)
        elif isinstance(value, dict):
            value = t(**value)
        else:
            value = t(value)

        try:
            cmd = 'item.d.{} = value'.format(key)
            exec cmd
        except:
            print('Pas content')

    def emitCurrentDataChanged(self, item):
        self.currentDataChanged.emit(item.d)

    def refresh(self, dataDict):  # type: (dict[str: Data]) -> None
        self.clear()

        for key, data in dataDict.items():
            item = QtWidgets.QTreeWidgetItem((key, data.__class__.__name__))
            item.d = data
            self.addTopLevelItem(item)

    def getDataDict(self):  # type: () -> MyOrderedDict[str: Data]
        iterator = QtWidgets.QTreeWidgetItemIterator(self)

        dataDict = MyOrderedDict()
        while True:
            item = iterator.value()
            if item is None:
                break
            dataDict[item.text(0)] = item.d
            iterator.next()

        return dataDict

    def populateContextMenu(self):
        addMenu = QtWidgets.QMenu('Add')
        for t in self.types:
            act = QtWidgets.QAction(t.__name__, self)
            addMenu.addAction(act)

        selectedItems = self.selectedItems()

        removeAction = QtWidgets.QAction('Remove', self)
        if not selectedItems:
            removeAction.setEnabled(False)

        duplicateAction = QtWidgets.QAction('Duplicate', self)
        if not selectedItems:
            duplicateAction.setEnabled(False)

        moveUpAction = QtWidgets.QAction('Move Up', self)
        if not len(selectedItems) == 1:
            moveUpAction.setEnabled(False)

        moveDownAction = QtWidgets.QAction('Move Down', self)
        if not len(selectedItems) == 1:
            moveDownAction.setEnabled(False)

        renameAction = QtWidgets.QAction('Rename', self)
        if not len(selectedItems) == 1:
            renameAction.setEnabled(False)

        menu = QtWidgets.QMenu()
        menu.addMenu(addMenu)
        menu.addAction(duplicateAction)
        menu.addSeparator()
        menu.addAction(renameAction)
        menu.addSeparator()
        menu.addAction(moveUpAction)
        menu.addAction(moveDownAction)
        menu.addSeparator()
        menu.addAction(removeAction)

        return menu

    def contextMenuEvent(self, event):

        menu = self.populateContextMenu()
        menu.exec_(self.viewport().mapToGlobal(event.pos()))


class DataDictEditor(QtWidgets.QWidget):

    def __init__(self, dataDictList, dataAttributeEditor):  # type: (DataDictList, DataAttributeEditor) -> None
        super(DataDictEditor, self).__init__()

        self.dataDictList = dataDictList
        self.dataAttributeEditor = dataAttributeEditor

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.dataDictList)
        splitter.addWidget(self.dataAttributeEditor)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(splitter)

        self.setLayout(mainLayout)

        self.dataDictList.currentDataChanged.connect(self.dataAttributeEditor.refresh)
        self.dataAttributeEditor.attributeValueChanged.connect(self.dataDictList.setAttributeValue)

    def refresh(self, dataDict):  # type: (dict[str: Data]) -> None
        self.dataDictList.refresh(dataDict)

    def getDataDict(self):  # type: () -> MyOrderedDict[str: Data]
        return self.dataDictList.getDataDict()
