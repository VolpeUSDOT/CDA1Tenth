from PySide6.QtCore import QAbstractListModel, Qt


class CargoItem():

    def __init__(self, name=None, cargo_uuid=None):
        self.name = name
        self.cargo_uuid = cargo_uuid

    def textDisplay(self):
        return "Display function not yet implemented"


class CargoItemModel(QAbstractListModel):
    '''
    Model that stores Action Point data for the project
    '''
    def __init__(self, *args, cargoItems=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cargoItems = cargoItems or []

    def rowCount(self, index):
        return len(self.cargoItems)

    def data(self, index, role):
        cargoItem = self.cargoItems[index.row()]

        if role == Qt.ItemDataRole.EditRole:
            return cargoItem

        if role == Qt.ItemDataRole.DisplayRole: # Completed list display
            text = cargoItem.textDisplay()
            return text

    def setData(self, index, value, role):
        '''
        TODO: update?
        '''
        if role != Qt.ItemDataRole.EditRole:
            print("Not editable")
            return False


        self.cargoItems[index.row()] = value
        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        flags = super().flags(index)
        # flags |= Qt.ItemFlag.ItemIsEditable
        return flags
