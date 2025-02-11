
from MapWidget.mapwidget import MapWidget
from PySide6.QtCore import QAbstractListModel, Qt, Property, QSortFilterProxyModel, Signal, QPoint
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QStackedWidget, QPushButton, QAbstractItemView, QListView, QLineEdit, QCheckBox, QListWidget, QGraphicsItem
from actionPointItem import ActionPoint,  ActionPointModel


class APWindow(QWidget):
    '''

    '''

    def __init__(self):
        super().__init__()
        self.title = QLabel('''# Action Points''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.apModel = ActionPointModel()
        self.apItemView = APItemView()
        self.apItemView.setModel(self.apModel)
        self.apMap = MapWidget()
        self.addAPButton = QPushButton("Add Action Point")
        self.editAPButton = QPushButton("Edit Action Point")
        self.activeEditor = None


        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 5)
        layout.addWidget(self.apMap, 1, 0, 3, 3)
        layout.addWidget(self.apItemView, 1, 3, 1, 2)
        layout.addWidget(self.addAPButton, 2, 3, 1, 1)
        layout.addWidget(self.editAPButton, 2, 4, 1, 1)
        self.setLayout(layout)

        self.addAPButton.clicked.connect(self.launchNewAPEditor)
        self.editAPButton.clicked.connect(self.launchAPEditor)

        self.apModel.dataChanged.connect(self.updateMap)

        self.apMap.selectionUpdate.connect(self.propagateMapSelection)

    def propagateMapSelection(self, mapItem):

        i = self.apMap.ap_list.index(mapItem)
        self.apItemView.setCurrentIndex(self.apModel.index(i, 0))

    def updateMap(self):
        self.apMap.clearActionPoints()
        for i in range(self.apModel.rowCount(None)):
            ap_data = self.apModel.data(self.apModel.index(i,0), role=Qt.ItemDataRole.EditRole)
            self.apMap.addActionPoint(ap_data.latitude, ap_data.longitude)

    def launchNewAPEditor(self):
        index = self.apModel.insertRow(0, ActionPoint())
        self.apItemView.setCurrentIndex(index)
        self.activeEditor = APItemEditor(ActionPoint())
        self.activeEditor.pushUpdates.clicked.connect(self.closeEditorAndUpdate)
        self.activeEditor.show()

    def launchAPEditor(self):
        index = self.apItemView.selectedIndexes()[0]
        self.activeEditor = APItemEditor(index.data(role=Qt.ItemDataRole.EditRole))
        self.activeEditor.pushUpdates.clicked.connect(self.closeEditorAndUpdate)
        self.activeEditor.show()

    def closeEditorAndUpdate(self):
        index = self.apItemView.selectedIndexes()[0]
        self.apModel.setData(index, value = self.activeEditor.m_ap, role=Qt.ItemDataRole.EditRole)
        self.activeEditor.close()
        self.activeEditor = None

    def readSQLActionPoints(self, actionData):
        '''
        Pull action points from SQL and add them to map and list
        # TODO: This loads in the ap in reverse order (replace 0 in inser trow with something better)
        '''
        for _, actionPointData in actionData.iterrows():
            ap_dict = actionPointData.to_dict()
            ap = ActionPoint(name=ap_dict['operation'], latitude=ap_dict['destination_lat'], longitude=ap_dict['destination_long'])
            self.apModel.insertRow(0, ap)


class APItemView(QListView):
    '''
    Subclass of list view for showing a list of editable action items
    '''
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformItemSizes(True)
        self.setDragEnabled(True)
        # self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        # self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


class APItemEditor(QWidget):
    '''
    # self.actionID = actionID
    # self.next_action = next_action
    # self.prev_action = prev_action        Set by order of list

    self.latitude = latitude
    self.longitude = longitude              Set by map

    self.name = name
    self.is_notify = False                  Set by fields
    self.status = False                     does not need to be set

    '''

    def __init__(self, actionPoint):
        super().__init__()
        '''

        '''
        self.m_ap = actionPoint
        self.title = QLabel('''## Create Action Point''')
        if self.m_ap.name:
            self.title.setText('''## Edit Action Point''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.notifyLabel = QLabel("Is Notify:")
        self.nameLabel = QLabel("Name:")
        self.isNotify_editor = QCheckBox("")
        self.isNotify_editor.setChecked(self.m_ap.is_notify)
        self.name_editor = QLineEdit()
        self.name_editor.setText(self.m_ap.name)
        self.pushUpdates = QPushButton("Save Action Point")

        self.apMap = MapWidget()
        self.apMap.addActionPoint(self.m_ap.latitude, self.m_ap.longitude)
        self.apMap.ap_list[0].setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.apMap.ap_list[0].setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 5)
        layout.addWidget(self.apMap, 1, 0, 4, 3)
        layout.addWidget(self.notifyLabel, 1, 3, 1, 1)
        layout.addWidget(self.nameLabel, 1, 4, 1, 1)
        layout.addWidget(self.isNotify_editor, 2, 3, 1, 1)
        layout.addWidget(self.name_editor, 2, 4, 1, 1)
        layout.addWidget(self.pushUpdates, 4, 3, 1, 2)

        self.setLayout(layout)

        self.isNotify_editor.stateChanged.connect(self.isNotifyChanged)
        self.name_editor.textEdited.connect(self.nameChanged)

        self.apMap.scene.changed.connect(self.updateLatLong)

    def updateLatLong(self):
        point = self.apMap.ap_list[0].pos()
        x, y = point.x(), point.y()
        long, lat = self.apMap.reverseCoordConversion(x, y)
        self.m_ap.latitude = lat
        self.m_ap.longitude = long

    def nameChanged(self):
        self.m_ap.name = self.name_editor.text()

    def isNotifyChanged(self):
        self.m_ap.is_notify = self.isNotify_editor.isChecked()


if __name__ == "__main__":
    class App(QApplication):
        def __init__(self):
            super().__init__()

    app = App()
    window = APWindow()
    window.show()
    app.exec()
