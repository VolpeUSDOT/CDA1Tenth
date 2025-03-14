import sys
import numpy as np
from MapWidget.mapwidget import MapWidget
from PySide6.QtCore import QAbstractListModel, Qt, Property, QSortFilterProxyModel, Signal, QPoint, QItemSelectionModel
from PySide6.QtWidgets import (
    QComboBox,
    QMessageBox,
    QApplication,
    QMainWindow,
    QGridLayout,
    QLabel,
    QWidget,
    QStackedWidget,
    QPushButton,
    QAbstractItemView,
    QListView,
    QLineEdit,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QGraphicsItem,
)
from actionPointItem import ActionPoint,  ActionPointModel
from webSocketClient import WebSocketClient
from messageDecoder import MessageDecoder
from bsmItem import BSMItem
from actionItem import ActionItem
from vehicleItem import VehicleItem
from cargoItem import CargoItem
from MysqlDataPull import Database
from config import Config

class APWindow(QWidget):
    '''

    '''

    def __init__(self, loading_signal, unloading_signal, inspection_signal):
        super().__init__()
        self.title = QLabel('''# Action Points''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.apModel = ActionPointModel()
        # self.apListWidget = APListWidget()
        self.apListView = APListView()
        self.apListView.setModel(self.apModel)
        self.apMap = MapWidget()
        self.apMap.setStyleSheet("background-color: grey;")
        self.addAPButton = QPushButton("Add Action Point")
        self.editAPButton = QPushButton("Edit Action Point")
        self.activeEditor = None
        self.loading_signal = loading_signal
        self.unloading_signal = unloading_signal
        self.inspection_signal = inspection_signal

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 5)
        layout.addWidget(self.apMap, 1, 0, 3, 3)
        layout.addWidget(self.apListView, 1, 3, 1, 2)
        layout.addWidget(self.addAPButton, 2, 3, 1, 1)
        layout.addWidget(self.editAPButton, 2, 4, 1, 1)
        self.setLayout(layout)

        self.addAPButton.clicked.connect(self.launchNewAPEditor)
        self.editAPButton.clicked.connect(self.launchAPEditor)

        self.apModel.dataChanged.connect(self.updateView)

        # When a map item is selected, update the selection in the model
        self.apMap.selectionUpdate.connect(self.propagateMapSelection)

        # when list widget is reordered, update model to match
        # self.apListWidget.itemDropped.connect(self.propagateListReorder)
        # self.apListWidget.indexesMoved().connect(self.propagateListReorder)
        self.messageDecoder = MessageDecoder()

        self.webSocketClient = WebSocketClient()
        # Connect signals
        self.webSocketClient.message_received.connect(self.handleIncomingMessage)
        # Start connection
        self.webSocketClient.start_connection()

        # When a list widget item is selected, update the selection
        # self.apListWidget.itemSelectionChanged.connect(self.propagateListSelection)

    def propagateListSelection(self):
        '''
        list selections will be passed to model
        '''
        pass

    # def dropSelection(self):
    #     self.apListWidget.clearSelection()

    # def propagateListReorder(self):
    #     '''
    #     transfer reorder of list widget to model
    #     '''
    #     index_list = [self.apListWidget.item(x).real_index for x in range(self.apListWidget.count())]
    #     print(index_list)
    #     self.apModel.updateItemOrder(index_list)
    #     # self.apListWidget.clearSelection()

    def propagateMapSelection(self, mapItem):
        '''
        map selections will be passed to the list widget
        '''
        i = self.apMap.ap_list.index(mapItem)
        # ap = self.apListWidget.item(i)
        # ap.setSelected(True)
        self.apListView.setCurrentIndex(self.apModel.index(i, 0))

    def updateListView(self):
        '''
        '''
        pass
        # self.apListWidget.clear()
        # for i in range(self.apModel.rowCount(None)):
        #     display_str = self.apModel.data(self.apModel.index(i,0), role=Qt.ItemDataRole.DisplayRole)
        #     ap = ActionPointListItem(display_str, i)
        #     self.apListWidget.addItem(ap)

    def updateMap(self):
        '''
        '''
        self.apMap.clearActionPoints()
        for i in range(self.apModel.rowCount(None)):
            ap_data = self.apModel.data(self.apModel.index(i,0), role=Qt.ItemDataRole.EditRole)
            if hasattr(ap_data, "actionPoint"):
                ap_data = ap_data.actionPoint
            self.apMap.addActionPoint(ap_data.latitude, ap_data.longitude, ap_data.name)

    def updateView(self):
        self.updateMap()
        # self.updateListView()

    def handleIncomingMessage(self, message):
        #print(message)
        decoded_message = self.messageDecoder.decodeMessage(message)
        if type(decoded_message) is BSMItem:
            self.updateVehiclePose(decoded_message)
        elif type(decoded_message) is ActionItem:
            if decoded_message.actionPoint.name == "PICKUP":
                self.loading_signal.emit(decoded_message)
            elif decoded_message.actionPoint.name == "DROPOFF":
                self.unloading_signal.emit(decoded_message)
            elif decoded_message.actionPoint.name == "PORT_CHECKPOINT" or decoded_message.actionPoint.name == "HOLDING_AREA":
                self.inspection_signal.emit(decoded_message)

    def updateVehiclePose(self, bsm):
        self.apMap.clearVehiclePosition()
        self.apMap.addVehiclePosition(bsm.latitude, bsm.longitude)

    def launchNewAPEditor(self):
        index = self.apModel.insertRow(0, ActionPoint())
        self.apListView.selectionModel().clearSelection()
        self.apListView.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectionFlag.Select)
        index = self.apListView.selectedIndexes()[0]

        # self.apListWidget.clearSelection()
        # self.apListWidget.item(0).setSelected()
        self.activeEditor = APItemEditor(index.data(role=Qt.ItemDataRole.EditRole))
        self.activeEditor.pushUpdates.clicked.connect(self.closeEditorAndUpdate)
        self.activeEditor.closeEvent = self.close_editor
        self.activeEditor.show()

    def close_editor(self, event):
        """Closed the editor without creating a new action point, remove the empty point from the list."""
        index = self.apListView.selectedIndexes()[0]
        selectedRow = index.data(role=Qt.ItemDataRole.EditRole)
        if (
            hasattr(selectedRow, "actionID")
            and selectedRow.actionID is None
            and hasattr(selectedRow, "name")
            and selectedRow.name is None
        ):
            # Ensure it only applies to create new action point, but no data is entered
            self.apModel.removeRow(index.row())

    def launchAPEditor(self):
        # i = self.apListWidget.selectedItems()[0].real_index
        if len(self.apListView.selectedIndexes()) < 1:
            return
        index = self.apListView.selectedIndexes()[0]
        self.activeEditor = APItemEditor(index.data(role=Qt.ItemDataRole.EditRole))
        self.activeEditor.pushUpdates.clicked.connect(self.closeEditorAndUpdate)
        self.activeEditor.show()

    def closeEditorAndUpdate(self):
        # i = self.apListWidget.selectedItems()[0].real_index
        # self.apModel.setData(self.apModel.index(i,0), value = self.activeEditor.m_ap, role=Qt.ItemDataRole.EditRole)
        index = self.apListView.selectedIndexes()[0]
        selectedRow = index.data(role=Qt.ItemDataRole.EditRole)
        clickedNewPoint = self.activeEditor.apMap.clickedNewPoint
        SQLdb = Database("PORT_DRAYAGE")
        # Update database
        isDBUpdate = False
        if hasattr(selectedRow, "actionPoint") or selectedRow.actionID is not None:
            """Update existing action point"""
            actionPoint = (
                selectedRow.actionPoint
                if hasattr(selectedRow, "actionPoint")
                else selectedRow
            )
            SQLdb.updateActionNotify(actionPoint.actionID, actionPoint.is_notify)
            SQLdb.updateActionAreaName(actionPoint.actionID, actionPoint.name)
            SQLdb.updateCargoName(actionPoint.actionID, actionPoint.cargo_name)
            SQLdb.updateVehicleId(actionPoint.actionID, actionPoint.vehicle_id)
            isDBUpdate = True
        elif (
            clickedNewPoint is not None
            and hasattr(selectedRow, "name")
            and selectedRow.name is not None
            and hasattr(selectedRow, "vehicle_id")
            and selectedRow.vehicle_id is not None
            and hasattr(selectedRow, "cargo_name")
            and selectedRow.cargo_name is not None
        ):
            """Create new action point"""
            actionPoint = selectedRow
            clickedNewPointLong, clickedNewPointLat = (
                self.activeEditor.apMap.reverseCoordConversion(
                    clickedNewPoint.x(), clickedNewPoint.y()
                )
            )
            actionPoint.latitude = clickedNewPointLat
            actionPoint.longitude = clickedNewPointLong
            SQLdb.insertNewActionPoint(actionPoint)
            # Update the main action point map after it is saved to DB
            self.apMap.addActionPoint(clickedNewPointLat, clickedNewPointLong)
            isDBUpdate = True

        if isDBUpdate:
            self.activeEditor = APItemEditor(selectedRow)
            self.activeEditor.close()
            self.activeEditor = None
            self.updateMap()
        else:
            QMessageBox.warning(
                self,
                "Invalid Action Point",
                "No valid coordinates selected, or area name, vehicle id, cardo name are empty for the new action point.",
            )
            self.apModel.removeRow(index.row())
    def readSQLActionPoints(self, actionData):
        '''
        Pull action points from SQL and add them to map and list
        # TODO: This loads in the ap in reverse order (replace 0 in inser trow with something better)
        '''
        for _, actionPointData in actionData.iterrows():
            ap_dict = actionPointData.to_dict()
            ap = ActionPoint(
                actionID=ap_dict["action_id"],
                next_action=ap_dict["next_action_id"],
                prev_action=ap_dict["prev_action_id"],
                name=ap_dict["area_name"],
                latitude=ap_dict["area_lat"],
                longitude=ap_dict["area_long"],
                vehicle_id=ap_dict["veh_id"],
                cargo_name=ap_dict["cargo_name"],
            )
            ap.setIsNotify(ap_dict["area_is_notify"])
            ap.setStatus(ap_dict["area_status"])
            vehicle = VehicleItem(name=ap_dict['veh_name'], veh_id=ap_dict['veh_id'])
            cargo = CargoItem(name=ap_dict['cargo_name'], cargo_uuid=ap_dict['cargo_uuid'])
            action = ActionItem(vehicle=vehicle, cargo=cargo, actionPoint=ap)
            self.apModel.insertRow(0, action)

# class APListWidget(QListWidget):
#     itemSelectionDropped = Signal()
#     itemDropped = Signal()
#     '''
#     Subclass of list view for showing a list of editable action items
#     '''
#     def __init__(self):
#         super().__init__()
#         self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
#         self.setUniformItemSizes(True)
#         self.setDragEnabled(True)
#         # self.viewport().setAcceptDrops(True)
#         # self.setDropIndicatorShown(True)
#         self.setAcceptDrops(True)
#         # self.setDragDropOverwriteMode(False)
#         self.setDefaultDropAction(Qt.DropAction.MoveAction)
#         self.setDragDropMode(QAbstractItemView.InternalMove)
#         # self.setItemDelegate(ActionDelegate())
#         # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
#         self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
#         self.itemSelectionChanged.connect(self.itemSelectionSignalTrigger)

#     def itemSelectionSignalTrigger(self):
#         if len(self.selectedItems()) == 0:
#             self.itemSelectionDropped.emit()

#     def dropEvent(self, event): # TODO this might not be the correct event
#         self.itemDropped.emit()
#         event.accept()
#         # return super().moveEvent(event)

class APListView(QListView):
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformItemSizes(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


class ActionPointListItem(QListWidgetItem):

    def __init__(self, display_str, real_index):
        super().__init__()
        # self.display_str = display_str
        self.real_index = real_index
        self.setText(display_str)


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
        if hasattr(self.m_ap, "actionPoint") and self.m_ap.actionPoint is not None:
            self.title.setText('''## Edit Action Point''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.notifyLabel = QLabel("Is Notify:")
        self.nameLabel = QLabel("Area Name:")
        self.vehicleIdLabel = QLabel("Vehicle Id:")
        self.cargoNameLabel = QLabel("Cargo Name:")
        self.isNotify_editor = QCheckBox("")
        self.m_ap = (
            self.m_ap.actionPoint if hasattr(self.m_ap, "actionPoint") else self.m_ap
        )
        self.isNotify_editor.setChecked(self.m_ap.is_notify)
        self.name_editor = QLineEdit()
        self.name_editor.setText(self.m_ap.name)

        vehicle_ids = [vehicle["id"] for vehicle in Config().get("vehicles")]
        self.vehicle_dropdown = QComboBox()
        self.vehicle_dropdown.addItems(vehicle_ids)
        cargo_names = [cargo["name"] for cargo in Config().get("cargos")]
        self.cargo_dropdown = QComboBox()
        self.cargo_dropdown.addItems(cargo_names)
        self.vehicle_dropdown.currentTextChanged.connect(self.vehicleChanged)
        self.cargo_dropdown.currentTextChanged.connect(self.cargoChanged)
        if hasattr(self.m_ap, "vehicle") and self.m_ap.vehicle is not None:
            self.vehicle_dropdown.setCurrentText(self.m_ap.vehicle.id)
        elif hasattr(self.m_ap, "vehicle_id") and self.m_ap.vehicle_id is not None:
            self.vehicle_dropdown.setCurrentText(self.m_ap.vehicle_id)
        else:
            self.vehicle_dropdown.setCurrentText(vehicle_ids[0])
            self.m_ap.vehicle_id = vehicle_ids[0]
        if hasattr(self.m_ap, "cargo") and self.m_ap.cargo is not None:
            self.cargo_dropdown.setCurrentText(self.m_ap.cargo.name)
        elif hasattr(self.m_ap, "cargo_name") and self.m_ap.cargo_name is not None:
            self.cargo_dropdown.setCurrentText(self.m_ap.cargo_name)
        else:
            self.cargo_dropdown.setCurrentText(cargo_names[0])
            self.m_ap.cargo_name = cargo_names[0]

        self.pushUpdates = QPushButton("Save Action Point")

        self.apMap = MapWidget()
        self.apMap.setStyleSheet("background-color: grey;")
        self.apMap.addActionPoint(self.m_ap.latitude, self.m_ap.longitude)
        if len(self.apMap.ap_list) > 0:
            self.apMap.ap_list[0].setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.apMap.ap_list[0].setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            )

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 5)
        layout.addWidget(self.apMap, 1, 0, 5, 3)
        layout.addWidget(self.notifyLabel, 1, 3, 1, 1)
        layout.addWidget(self.isNotify_editor, 1, 4, 1, 1)
        layout.addWidget(self.nameLabel, 2, 3, 1, 1)
        layout.addWidget(self.name_editor, 2, 4, 1, 1)
        layout.addWidget(self.vehicleIdLabel, 3, 3, 1, 1)
        layout.addWidget(self.vehicle_dropdown, 3, 4, 1, 1)
        layout.addWidget(self.cargoNameLabel, 4, 3, 1, 1)
        layout.addWidget(self.cargo_dropdown, 4, 4, 1, 1)
        layout.addWidget(self.pushUpdates, 5, 3, 1, 2)

        self.setLayout(layout)

        self.isNotify_editor.stateChanged.connect(self.isNotifyChanged)
        self.name_editor.textEdited.connect(self.nameChanged)

        self.apMap.scene.changed.connect(self.updateLatLong)

    def vehicleChanged(self):
        self.m_ap.vehicle_id = self.vehicle_dropdown.currentText()

    def cargoChanged(self):
        self.m_ap.cargo_name = self.cargo_dropdown.currentText()

    def updateLatLong(self):
        if len(self.apMap.ap_list) < 1:
            return
        point = self.apMap.ap_list[0].pos()
        x, y = point.x(), point.y()

        min_dist = sys.maxsize
        closest_item = None
        for i, point in self.apMap.points.iterrows():
            distance = Distance_Formula((x, y), (point['adjusted_x'], point['adjusted_y']))

            if distance < min_dist:
                min_dist = distance
                closest_item = i
        x = self.apMap.points.loc[closest_item, 'adjusted_x']
        y = self.apMap.points.loc[closest_item, 'adjusted_y']
        self.apMap.ap_list[0].setPos(x, y)
        long, lat = self.apMap.reverseCoordConversion(x, y)
        self.m_ap.latitude = lat
        self.m_ap.longitude = long

    def nameChanged(self):
        self.m_ap.name = self.name_editor.text()

    def isNotifyChanged(self):
        self.m_ap.is_notify = self.isNotify_editor.isChecked()

def Distance_Formula(point1, point2):
    x1 = point1[0]
    x2 = point2[0]
    y1 = point1[1]
    y2 = point2[1]
    x_diff = (x2 - x1)**2
    y_diff = (y2 - y1)**2
    distance = np.sqrt(x_diff + y_diff)
    return distance


if __name__ == "__main__":
    class App(QApplication):
        def __init__(self):
            super().__init__()

    app = App()
    window = APWindow()
    window.show()
    app.exec()
