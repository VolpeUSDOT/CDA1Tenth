from PySide6.QtCore import QAbstractListModel, Qt, Property, QSortFilterProxyModel, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QStackedWidget, QPushButton, QAbstractItemView, QListView, QLineEdit
from cargoItem import CargoItem,  CargoItemModel

class CargoWindow(QWidget):
    '''

    '''

    def __init__(self):
        super().__init__()
        self.title = QLabel('''# Cargo Items''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.cargoItemModel = CargoItemModel()
        self.cargoItemView = CargoItemView()
        self.cargoItemView.setModel(self.cargoItemModel)
        self.addCargoButton = QPushButton("Add Cargo Item")
        self.editCargoButton = QPushButton("Edit Cargo Item")
        self.activeEditor = None


        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 2)
        layout.addWidget(self.cargoItemView, 1, 0, 1, 2)
        layout.addWidget(self.addCargoButton, 2, 0, 1, 1)
        layout.addWidget(self.editCargoButton, 2, 1, 1, 1)

        self.setLayout(layout)

        self.addCargoButton.clicked.connect(self.launchNewCargoEditor)
        self.editCargoButton.clicked.connect(self.launchCargoEditor)


    def launchNewCargoEditor(self):
        index = self.cargoItemModel.insertRow(0, CargoItem())
        self.cargoItemView.setCurrentIndex(index)
        self.activeEditor = CargoItemEditor(CargoItem())
        self.activeEditor.pushUpdates.clicked.connect(self.closeEditorAndUpdate)
        self.activeEditor.show()

    def launchCargoEditor(self):
        index = self.cargoItemView.selectedIndexes()[0]
        self.activeEditor = CargoItemEditor(index.data(role=Qt.ItemDataRole.EditRole))
        self.activeEditor.pushUpdates.clicked.connect(self.closeEditorAndUpdate)
        self.activeEditor.show()

    def closeEditorAndUpdate(self):
        index = self.cargoItemView.selectedIndexes()[0]
        self.cargoItemModel.setData(index, value = self.activeEditor.m_cargo, role=Qt.ItemDataRole.EditRole)
        self.activeEditor.close()
        self.activeEditor = None


class CargoItemView(QListView):
    '''
    Subclass of list view for showing a list of editable action items
    '''
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformItemSizes(True)
        # self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)


class CargoItemEditor(QWidget):
    '''

    '''

    def __init__(self, cargo):
        super().__init__()
        self.m_cargo = cargo
        self.title = QLabel('''### Create Cargo Item''')
        if self.m_cargo.name:
            self.title.setText('''### Edit Cargo Item''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.uuidLabel = QLabel("UUID:")
        self.nameLabel = QLabel("Cargo Name:")
        self.uuid_editor = QLineEdit()
        self.uuid_editor.setText(self.m_cargo.cargo_uuid)
        self.name_editor = QLineEdit()
        self.name_editor.setText(self.m_cargo.name)
        self.pushUpdates = QPushButton("Save Cargo Item")


        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 2)
        layout.addWidget(self.uuidLabel, 1, 0, 1, 1)
        layout.addWidget(self.nameLabel, 1, 1, 1, 1)
        layout.addWidget(self.uuid_editor, 2, 0, 1, 1)
        layout.addWidget(self.name_editor, 2, 1, 1, 1)
        layout.addWidget(self.pushUpdates, 3, 0, 1, 2)

        self.setLayout(layout)

        self.uuid_editor.textEdited.connect(self.uuidChanged)
        self.name_editor.textEdited.connect(self.nameChanged)

    def nameChanged(self):
        self.m_cargo.name = self.name_editor.text()

    def uuidChanged(self):
        self.m_cargo.cargo_uuid = self.uuid_editor.text()




if __name__ == "__main__":
    class App(QApplication):
        def __init__(self):
            super().__init__()

    app = App()
    window = CargoWindow()
    window.show()
    app.exec()
