'''
Port Drayage Unloading Area Interface:

Intended to represent the actions taking place at the unloading station of a port (not vehicle centric)

When a vehicle enters the unloading area (maybe not called area anymore), it should add an interactable pending action

Actions contain info on vehicle, cargo(container) status(pending, unloading, completed), requested timestamp, completed timestamp

pending and unloading actions have a button to interact with and progress the action. Once an action is completed, the interactable object is removed and the info of the action is added to a completed action log
'''
import time
from PySide6.QtCore import QAbstractListModel, Qt, Property
from PySide6.QtWidgets import QGroupBox, QGridLayout, QAbstractItemView, QListWidget, QListWidgetItem, QPushButton, QListView, QLabel, QWidget, QItemDelegate, QStyledItemDelegate, QLineEdit


class PDUnloadingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.model = UnloadingActionList(unloadingActions=[ActionItem()])
        self.unloadingActionView = PendingActionView()
        self.unloadingActionView.setModel(self.model)

        self.title = QLabel('''# Port Drayage Unloading Area''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.completedResetButton = QPushButton("Clear")

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 1)
        layout.addWidget(self.unloadingActionView, 1, 0, 1, 1)
        # layout.addWidget(self.completedActionList, 2, 0, 1, 1)
        layout.addWidget(self.completedResetButton, 3, 0, 1, 1)

        self.setLayout(layout)


    def addLoadingAction(self):

        self.model.unloadingActions.append(ActionItem())
        self.model.layoutChanged.emit()

    def deleteLoadingAction(self):
        indexes = self.unloadingActionView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model.unloadingActions[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.unloadingActionView.clearSelection()



class ActionItem():
    '''
    Class to store data for individual items in model
    This allows for in place data modification, and display functions to be attached to the data item
    '''

    def __init__(self, vehicle=None, cargo=None, actionID=None):
        super().__init__()
        self.vehicle = vehicle
        self.cargo = cargo
        self.actionID = actionID
        self.status = "Pending"
        self.timeRequested = time.time()
        self.timeCompleted = None

    # def pendingActionDisplay(self):
    #     '''TODO: Update'''
    #     return "EDITABLE: Vehicle: " + str(self.vehicle)  + " | Cargo: " + str(self.cargo) + " | Action ID: " + str(self.actionID) + " | Time Requested: " + str(self.timeRequested)



    # def completedActionDisplay(self):
    #     '''TODO: Update'''
    #     return "Vehicle: " + str(self.vehicle)  + " | Cargo: " + str(self.cargo) + " | Action ID: " + str(self.actionID) + " | Time Requested: " + str(self.timeRequested)




class PendingActionView(QListView):

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformItemSizes(True)
        self.setItemDelegate(ActionDelegate())
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        # self.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)

class UnloadingActionList(QAbstractListModel):

    def __init__(self, *args, unloadingActions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.unloadingActions = unloadingActions or []

        # self.flags(Qt.ItemFlag.ItemIsEditable)

    def rowCount(self, index):
        return len(self.unloadingActions)

    def data(self, index, role):
        action = self.unloadingActions[index.row()]

        return action
        # if role == Qt.ItemDataRole.EditRole: # Pending List
        #     text = unloadingAction.pendingActionDisplay()
        #     return text

        # if role == Qt.ItemDataRole.DisplayRole: # Completed list display
        #     text = unloadingAction.completedActionDisplay()
        #     return text


    def setData(self, index, value, role):
        '''
        TODO: update?
        '''
        if role != Qt.ItemDataRole.EditRole:
            print("Not editable")
            return False

        self.unloadingActions[index.row()] = value

        self.dataChanged.emit(index)
        return True

    def flags(self, index):
        flags = super().flags(index)
        if self.unloadingActions[index.row()].status == "Completed":
            # Special operator required to add a new flag to the list of flags
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags


class ActionDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Delegate Created")

    # Paint?

    def sizeHint(self, option, index):
        editor = ActionEditor()
        return editor.sizeHint()

    def createEditor(self, parent, option, index):
        print("Creating Editor")
        editor = ActionEditor(parent)
        editor.editing_finished.connect(self.commit_and_close_editor) # TODO Might need to lose this line
        return editor

    def setEditorData(self, editor, index):
        print(index.data())
        editor.action_data = ActionItem(index.data())

    def setModelData(self, editor, model, index):
        model.setData(index, editor.action_data)

    def commit_and_close_editor(self):
        '''
        Commits the data to the model and closes the editor
        '''
        editor = self.sender()

        # The commitData signal must be emitted when we've finished editing
        # and need to write our changed back to the model.
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)


    def updateEditorGeometry(self, editor, option, index):
        return super().updateEditorGeometry(editor, option, index)





class ActionEditor(QWidget):
    # actionCompleted = Signal()

    def __init__(self):
        super().__init__()



        self.m_action_data = ActionItem()

        # Internal widgets
        self.progressButton = QPushButton("Start Loading")
        self.portArea = QWidget() # Placeholder b/c I have no clue what is intended to be in that box
        self.vehicleLabel = QLabel("Vehicle: ")
        self.cargoLabel = QLabel("With Cargo: ")
        self.statusLabel = QLabel("Status: ")

        # Layout widgets
        layout = QGridLayout()
        layout.addWidget(self.vehicleLabel, 0, 0, 1, 1)
        layout.addWidget(self.cargoLabel, 0, 1, 1, 1)
        layout.addWidget(self.statusLabel, 1, 0, 1, 1)
        layout.addWidget(self.progressButton, 2, 0, 1, 2)
        layout.addWidget(self.portArea, 0, 2, 3, 2)
        self.setLayout(layout)

    def setValue(self, value):
        self.m_action_data = value

    def value(self):
        return self.m_action_data

    # Creates both QT and Python properties (I should have just done this in c++)
    action_data = Property(type=ActionItem, fget=value, fset=setValue)
