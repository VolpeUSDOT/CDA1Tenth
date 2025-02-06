from PySide6.QtCore import QAbstractListModel, Qt

class ActionPoint():
    '''
    Class to store data for individual items in model
    This allows for in place data modification, and display functions to be attached to the data item
    '''

    def __init__(self, actionID=None, next_action=None, prev_action=None, name=None, latitude=None, longitude=None):
        self.actionID = actionID
        self.next_action = next_action
        self.prev_action = prev_action
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.status = False
        self.is_notify = False

    def actionItemDataFilter(self):
        return AreaData(self.name, self.latitude, self.longitude, self.status, self.is_notify)

    def completedActionPointDisplay(self):
        # TODO: Implement
        return "Display function not yet implemented"


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

    def setData(self, index, value, role):
        '''
        TODO: update?
        '''
        if role != Qt.ItemDataRole.EditRole:
            print("Not editable")
            return False


        self.actionPoints[index.row()] = value
        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        flags = super().flags(index)
        # if self.loadingActions[index.row()].status != "Completed":
            # |= is a special operator required to add a new flag to the list of flags
        flags |= Qt.ItemFlag.ItemIsEditable
        return flags
