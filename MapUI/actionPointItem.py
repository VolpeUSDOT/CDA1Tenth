from PySide6.QtCore import (
    QAbstractListModel,
    Qt,
    QMimeData,
    QMimeType,
    QMimeDatabase,
    QDataStream,
    QByteArray,
    QIODevice,
    QModelIndex,
)
import json


class ActionPoint:
    """
    Class to store data for individual items in model
    This allows for in place data modification, and display functions to be attached to the data item
    """

    def __init__(
        self,
        actionID=None,
        next_action=None,
        prev_action=None,
        name=None,
        latitude=None,
        longitude=None,
        vehicle_id=None,
        cargo_name=None,
    ):
        self.actionID = actionID
        self.next_action = next_action
        self.prev_action = prev_action
        self.name = name
        self.vehicle_id = vehicle_id
        self.cargo_name = cargo_name
        self.latitude = latitude
        self.longitude = longitude
        self.status = True
        self.is_notify = False

    def actionItemDataFilter(self):
        return AreaData(
            self.name, self.latitude, self.longitude, self.status, self.is_notify
        )

    def completedActionPointDisplay(self):
        return f"Name: {self.name} \t\t "

    def convertToJSON(self):
        json_dict = {
            "actionID": self.actionID,
            "next_action": self.next_action,
            "prev_action": self.prev_action,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "vehicle_id": self.vehicle_id,
            "cargo_name": self.cargo_name,
            "is_notify": self.is_notify,
        }
        json_str = json.dumps(json_dict)
        return json_str

    def setIsNotify(self, is_notify):
        self.is_notify = is_notify

    def setStatus(self, status):
        self.status = status


class AreaData:

    def __init__(self, name, latitude, longitude, status, is_notify):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.status = status
        self.is_notify = is_notify


class ActionPointModel(QAbstractListModel):
    """
    Model that stores Action Point data for the project
    """

    def __init__(self, *args, actions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions = actions or []

    def rowCount(self, index):
        return len(self.actions)

    def data(self, index, role):
        ap = self.actions[index.row()]

        if role == Qt.ItemDataRole.EditRole:
            return ap

        if role == Qt.ItemDataRole.DisplayRole:  # Completed list display
            if hasattr(ap, "actionPoint"):
                text = ap.actionPoint.completedActionPointDisplay()
            else:
                text = ap.completedActionPointDisplay()
            return text

    def setData(self, index, value, role):
        """
        TODO: update?
        """
        # if role != Qt.ItemDataRole.EditRole:
        #     print("Not editable")
        #     return False

        self.actions[index.row()] = value
        self.dataChanged.emit(index, index)

        return True

    def insertRow(self, row, value):
        self.actions.insert(row, value)
        index = self.index(row, 0)
        self.dataChanged.emit(index, index)
        return index

    def insertRows(self, row, count, parent=...):
        if parent.isValid():
            return False
        for i in range(count):
            self.actions.insert(row + i, ActionPoint())
        return True

    def removeRows(self, row, count, parent=...):
        if parent.isValid():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            self.actions.pop(row)
        return True

    # TODO: See if this is correct and how it syncs with database etc.
    def updateItemOrder(self, index_list):
        """
        Reorder elements in model based off index_list
        """
        if len(index_list) != self.rowCount(None):
            return False
        self.actions = [self.actions[i] for i in index_list]
        return True

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        types = ["application/vnd.text.list"]
        return types

    def dropMimeData(self, data, action, row, column, parent):
        if action != Qt.DropAction.MoveAction:
            return False

        if column > 0:
            return False

        if row != -1:
            beginRow = row
        elif parent.isValid():
            beginRow = parent.row()
        else:
            beginRow = self.rowCount(QModelIndex())

        encodedData = data.data("application/vnd.text.list")
        stream = QDataStream(encodedData, QIODevice.OpenModeFlag.ReadOnly)

        temp_list = []
        for json_str in stream.readQStringList():
            ap_data = json.loads(json_str)
            ap = ActionPoint()

            ap.actionID = ap_data["MobilityOperationMessage"]["action_id"]
            # ap.next_action = ap_data["MobilityOperationMessage"]["next_action"]
            # ap.prev_action = ap_data["MobilityOperationMessage"]["prev_action"]
            ap.name = ap_data["MobilityOperationMessage"]["operation"]
            ap.latitude = ap_data["MobilityOperationMessage"]["destination"]["latitude"]
            ap.longitude = ap_data["MobilityOperationMessage"]["destination"][
                "longitude"
            ]
            # ap.status = ap_data["status"]
            # ap.is_notify = ap_data["is_notify"]

            temp_list.append(ap)

        # Insert the dropped item at the correct position
        self.beginInsertRows(QModelIndex(), beginRow, beginRow)
        self.actions.insert(beginRow, temp_list[0])
        self.endInsertRows()

        return True
        # return super().dropMimeData(data, action, row, column, parent)

    def convertToDataframe(self):
        """
        Converts list to pandas df, generating columns required for linked list calls later
        """
        #  TODO :Rewrite for new structure and SQL layout
        pass
        # ap_list = [self.apOrderList.item(x).actionPointData for x in range(self.apOrderList.count())]
        # ap_df = pd.DataFrame(ap_list)
        # ap_df['action_id'] = ap_df.index

        # # NOTE: List of ap info (updated SQL data columns) "id", "vehicle_name", "cargo_name", "action_id", "prev_action_id", "next_action_id", "action_name", "action_status", "longitude", "latitude", "is_notify", "created_at", "updated_at"

        # isLooping = self.loopCheckBox.checkState()
        # if isLooping:
        #     ap_df['next_action_id'] = ap_df['action_id'].shift(1, fill_value=ap_df['action_id'].iloc[-1])
        #     ap_df['prev_action_id'] = ap_df["action_id"].shift(-1,fill_value=ap_df['action_id'].iloc[0] )
        # else:
        #     #TODO: Fill vlaues -1
        #     ap_df['next_action'] = ap_df['action_id'].shift(1)
        #     ap_df['prev_action_id'] = ap_df["action_id"].shift(-1)
        # return ap_df

    def flags(self, index):
        flags = super().flags(index)
        # if self.loadingActions[index.row()].status != "Completed":
        # |= is a special operator required to add a new flag to the list of flags
        flags |= Qt.ItemFlag.ItemIsEditable

        if index.isValid():
            flags |= Qt.ItemFlag.ItemIsDragEnabled

        flags |= Qt.ItemFlag.ItemIsDropEnabled
        return flags

    def removeRow(self, row, parent=QModelIndex()):
        """Safely remove a single row from the model."""
        if 0 <= row < len(self.actions):
            self.beginRemoveRows(parent, row, row)
            del self.actions[row]
            self.endRemoveRows()
            return True
        return False

    def clear(self):
        self.actions = []
        self.layoutChanged.emit()
        return True
