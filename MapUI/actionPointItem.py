from PySide6.QtCore import QAbstractListModel, Qt, QMimeData

class ActionPoint():
    '''
    Class to store data for individual items in model
    This allows for in place data modification, and display functions to be attached to the data item
    '''

    def __init__(self, name=None, latitude=0, longitude=0):
        self.actionID = None
        self.next_action = None
        self.prev_action = None
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.status = False
        self.is_notify = False

    def actionItemDataFilter(self):
        return AreaData(self.name, self.latitude, self.longitude, self.status, self.is_notify)

    def completedActionPointDisplay(self):
        return f"Name: {self.name} \t\t "


class AreaData():

    def __init__(self, name, latitude, longitude, status, is_notify):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.status = status
        self.is_notify = is_notify


class ActionPointModel(QAbstractListModel):
    '''
    Model that stores Action Point data for the project
    '''
    def __init__(self, *args, actionPoints=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actionPoints = actionPoints or []

    def rowCount(self, index):
        return len(self.actionPoints)

    def data(self, index, role):
        ap = self.actionPoints[index.row()]

        if role == Qt.ItemDataRole.EditRole:
            return ap

        if role == Qt.ItemDataRole.DisplayRole: # Completed list display
            text = ap.completedActionPointDisplay()
            return text

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        '''
        TODO: update?
        '''
        if role != Qt.ItemDataRole.EditRole:
            print("Not editable")
            return False


        self.actionPoints[index.row()] = value
        self.dataChanged.emit(index, index)

        return True

    def insertRow(self, row, value):
        self.actionPoints.insert(row, value)
        index = self.index(row, 0)
        self.dataChanged.emit(index, index)
        return index

    def insertRows(self, row, count, parent = ...):
        if parent.isValid():
            return False
        for i in range(count):
            self.actionPoints.insert(row+i, ActionPoint())
        return True

    def removeRows(self, row, count, parent = ...):
        if parent.isValid():
            return False
        self.beginRemoveRows(parent, row, row+count-1)
        for i in range(count):
            self.actionPoints.pop(row)
        return True

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ActionPoint

    def mimeData(self, indexes):
        mimeData = QMimeData()
        for index in indexes:
            if index.isValid():
                self.data(index, role=Qt.ItemDataRole.EditRole)
        return super().mimeData(indexes)

    def convertToDataframe(self):
        '''
        Converts list to pandas df, generating columns required for linked list calls later
        '''
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
        flags |= Qt.ItemFlag.ItemIsDragEnabled
        flags |= Qt.ItemFlag.ItemIsDropEnabled

        return flags
