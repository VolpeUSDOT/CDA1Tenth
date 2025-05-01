from PySide6.QtCore import QAbstractListModel, Qt


class ActionListModel(QAbstractListModel):
    '''
    Model that stores ActionItems for an interactive tab
    '''
    def __init__(self, *args, actions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions = actions or []

    def rowCount(self, index=None):
        return len(self.actions)

    def data(self, index, role):
        action = self.actions[index.row()]

        if role == Qt.ItemDataRole.EditRole:
            return action

        if role == Qt.ItemDataRole.DisplayRole: # Completed list display
            text = action.completedActionDisplay()
            return text

    def setData(self, index, value, role):
        '''
        TODO: update?
        '''
        if role != Qt.ItemDataRole.EditRole:
            print("Not editable")
            return False


        self.actions[index.row()] = value
        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        flags = super().flags(index)
        if self.actions[index.row()].status != "Completed":
            # |= is a special operator required to add a new flag to the list of flags
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags
