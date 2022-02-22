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
        self.setItemWidget(item, 1, widget)

        item.setExpanded(True)

    def getAttributeWidget(self, key, value):
        t = type(value)

        if isinstance(value, bool):
            check = QtWidgets.QCheckBox(self)
            check.setChecked(value)
            check.stateChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return check

        elif isinstance(value, basestring):
            line = QtWidgets.QLineEdit(self)
            line.setText(value)
            line.textChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return line

        elif isinstance(value, int):
            spin = QtWidgets.QSpinBox(self)
            spin.setMinimum(-10000)
            spin.setMaximum(10000)
            spin.setValue(value)
            spin.valueChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return spin

        elif isinstance(value, float):
            spin = QtWidgets.QDoubleSpinBox(self)
            spin.setMinimum(-10000.0)
            spin.setMaximum(10000.0)
            spin.setValue(value)
            spin.valueChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return spin

        else:
            line = QtWidgets.QLineEdit(self)
            line.setText(str(value))
            line.setEnabled(False)
            return line


class DataDictList(QtWidgets.QTreeWidget):

    def __init__(self):
        super(DataDictList, self).__init__()
        self.setHeaderLabels(('key', 'type'))
        self.setColumnWidth(2, size(50))

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


class DataDictEditor(QtWidgets.QWidget):

    def __init__(self, dataDictList, dataAttributeEditor):  # type: (DataDictList, DataAttributeEditor) -> None
        super(DataDictEditor, self).__init__()

        self.dataDictList = dataDictList
        self.dataAttributeEditor = dataAttributeEditor

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.dataDictList)
        splitter.addWidget(self.dataAttributeEditor)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(splitter)

        self.setLayout(mainLayout)

        self.dataDictList.currentDataChanged.connect(self.dataAttributeEditor.refresh)
        self.dataAttributeEditor.attributeValueChanged.connect(self.dataDictList.setAttributeValue)

    def refresh(self, dataDict):  # type: (dict[str: Data]) -> None
        self.dataDictList.refresh(dataDict)

    def getDataDict(self):  # type: () -> MyOrderedDict[str: Data]
        return self.dataDictList.getDataDict()
