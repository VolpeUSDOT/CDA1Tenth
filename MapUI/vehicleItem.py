from PySide6.QtCore import QAbstractListModel, Qt


class VehicleItem():

    def __init__(self, name=None, veh_id=None):
        self.name = name
        self.veh_id = veh_id

    def textDisplay(self):
        return "Display function not yet implemented"


class VehicleModel(QAbstractListModel):
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
