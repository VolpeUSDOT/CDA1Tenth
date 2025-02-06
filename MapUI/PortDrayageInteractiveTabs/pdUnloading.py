'''
Port Drayage Unloading Area Interface:

Intended to represent the actions taking place at the unloading station of a port (not vehicle centric)

When a vehicle enters the unloading area (maybe not called area anymore), it should add an interactable pending action

Actions contain info on vehicle, cargo(container) status(pending, unloading, completed), requested timestamp, completed timestamp

pending and unloading actions have a button to interact with and progress the action. Once an action is completed, the interactable object is removed and the info of the action is added to a completed action log
'''
from PySide6.QtCore import QAbstractListModel, Qt, Property, QSortFilterProxyModel, Signal
from PySide6.QtWidgets import QGroupBox, QGridLayout, QAbstractItemView, QListWidget, QListWidgetItem, QPushButton, QListView, QLabel, QWidget, QItemDelegate, QStyledItemDelegate, QLineEdit
import time


class ActionItem():
    '''
    Class to store data for individual items in model
    This allows for in place data modification, and display functions to be attached to the data item
    '''

    def __init__(self, vehicle=None, cargo=None, actionPoint=None):
        super().__init__()
        self.vehicle = vehicle
        self.cargo = cargo
        self.actionPoint = actionPoint
        self.actionID = None # actionID
        self.next_action = None
        self.prev_action = None

        self.status = "Pending"
        self.timeRequested = time.time()
        self.timeCompleted = None

    def completedActionDisplay(self):
        text = 'Vehicle: {} \t Cargo: {} \t ActionID: {} \t Requested Time: {} \t Completed Time: {}'.format(self.vehicle, self.cargo, self.actionID, self.timeRequested, self.timeCompleted)
        return text


class PDUnloadingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.model = UnloadingActionList(unloadingActions=[ActionItem()])
        self.unloadingActionView = PendingActionView()
        self.completedActionView = CompletedActionView()
        self.inProgressFilterProxyModel = InProgressActionListProxyModel()
        self.inProgressFilterProxyModel.setSourceModel(self.model)
        self.completedFilterProxyModel = CompletedActionListProxyModel()
        self.completedFilterProxyModel.setSourceModel(self.model)

        self.unloadingActionView.setModel(self.inProgressFilterProxyModel)
        self.completedActionView.setModel(self.completedFilterProxyModel)

        self.unloadingActionView.openPersistentEditor(self.inProgressFilterProxyModel.index(0,0)) # TODO: Remove later when items appear based on received MOMs



        self.title = QLabel('''# Port Drayage Unloading Area''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.completedResetButton = QPushButton("Clear")

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 1)
        layout.addWidget(self.unloadingActionView, 1, 0, 1, 1)
        layout.addWidget(self.completedActionView, 2, 0, 1, 1)
        layout.addWidget(self.completedResetButton, 3, 0, 1, 1)

        self.setLayout(layout)

        # self.model.dataChanged.connect(self.updateFilters)

    # def updateFilters(self, index):
        #if index.data().status == "Completed":
        #    self.unloadingActionView.closePersistentEditor(index)
        # self.inProgressFilterProxyModel.invalidateFilter()
        # self.completedFilterProxyModel.invalidateFilter()

    def addLoadingAction(self):

        self.model.unloadingActions.append(ActionItem())
        i = self.model.rowCount()
        self.unloadingActionView.openPersistentEditor(self.model.index(i,0))
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


class PendingActionView(QListView):

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformItemSizes(True)
        self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)

class CompletedActionView(QListView):

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setUniformItemSizes(True)
        # self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

class InProgressActionListProxyModel(QSortFilterProxyModel):
    filterEnabledChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_filterEnabled = True
        # NOTE must use setSourceModel on object when created

    def filterAcceptsRow(self, source_row, source_parent):
        '''
        Filter
        '''
        print("Filter is updated")
        index = self.sourceModel().index(source_row, 0, source_parent)

        actionStatus = index.data(role=Qt.ItemDataRole.EditRole).status # index.data() calls the model data function at the given index

        return (actionStatus != "Completed")

    def filterEnabled(self):
        return self.m_filterEnabled

    def setFilterEnabled(self, enabled):
        if self.m_filterEnabled == enabled:
            return

        self.m_filterEnabled = enabled
        self.filterEnabledChanged.emit()
        self.invalidateFilter()

    filterEnabled = Property(type=bool, fget=filterEnabled, fset=setFilterEnabled, notify=filterEnabledChanged)


class CompletedActionListProxyModel(QSortFilterProxyModel):
    '''
    Seperate filter from above, does the opposite job for completed list
    '''
    filterEnabledChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_filterEnabled = True
        # NOTE must use setSourceModel on object when created

    def filterAcceptsRow(self, source_row, source_parent):
        '''
        Filter
        '''
        print("completed Filter is updated")
        index = self.sourceModel().index(source_row, 0, source_parent)

        actionStatus = index.data(role=Qt.ItemDataRole.EditRole).status # index.data() calls the model data function at the given index

        return (actionStatus == "Completed")

    def filterEnabled(self):
        return self.m_filterEnabled

    def setFilterEnabled(self, enabled):
        if self.m_filterEnabled == enabled:
            return

        self.m_filterEnabled = enabled
        self.filterEnabledChanged.emit()
        self.invalidateFilter()

    filterEnabled = Property(type=bool, fget=filterEnabled, fset=setFilterEnabled, notify=filterEnabledChanged)


class UnloadingActionList(QAbstractListModel):

    def __init__(self, *args, unloadingActions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.unloadingActions = unloadingActions or []

        # self.flags(Qt.ItemFlag.ItemIsEditable)

    def rowCount(self, index):
        return len(self.unloadingActions)

    def data(self, index, role):
        action = self.unloadingActions[index.row()]

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


        self.unloadingActions[index.row()] = value
        print(value)
        print("Model Data Updated")
        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        flags = super().flags(index)
        if self.unloadingActions[index.row()].status != "Completed":
            # |= is a special operator required to add a new flag to the list of flags
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags


class ActionDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Delegate Created")

    def sizeHint(self, option, index):
        editor = ActionEditor(None)
        return editor.sizeHint()

    def createEditor(self, parent, option, index):
        print("Creating Editor")
        editor = ActionEditor(parent)
        # Connect the dataChanged signal from each item to update the backend model data
        editor.actionDataChanged.connect(self.commit_from_editor) # TODO Might need to lose this line
        return editor

    def setEditorData(self, editor, index):
        print("Setting editor data")
        print(index)
        print(index.data(role=Qt.ItemDataRole.EditRole).status)
        editor.action_data = index.data(role=Qt.ItemDataRole.EditRole)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.action_data)

    def commit_from_editor(self):
        '''
        Commits the data to the model and closes the editor
        '''
        editor = self.sender()
        print("Editor:")
        print(editor)
        print(editor.m_action_data)
        # The commitData signal must be emitted when we've finished editing
        # and need to write our changed back to the model.
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)

    def updateEditorGeometry(self, editor, option, index):
        return super().updateEditorGeometry(editor, option, index)




class ActionEditor(QWidget):
    actionDataChanged = Signal()

    def __init__(self, parent):
        super().__init__(parent)



        self.m_action_data = ActionItem()

        # Internal widgets
        self.progressButton = QPushButton("Start Loading")
        self.portArea = QWidget() # Placeholder b/c I have no clue what is intended to be in that box
        self.vehicleLabel = QLabel("Vehicle: ")
        self.cargoLabel = QLabel("With Cargo: ")
        self.statusLabel = QLabel(f"Status: {self.m_action_data.status}")

        # Layout widgets
        layout = QGridLayout()
        layout.addWidget(self.vehicleLabel, 0, 0, 1, 1)
        layout.addWidget(self.cargoLabel, 0, 1, 1, 1)
        layout.addWidget(self.statusLabel, 1, 0, 1, 1)
        layout.addWidget(self.progressButton, 2, 0, 1, 2)
        layout.addWidget(self.portArea, 0, 2, 3, 2)
        self.setLayout(layout)

        self.progressButton.clicked.connect(self.progressStatus)

    def progressStatus(self):
        if self.m_action_data.status == "Pending":
            self.m_action_data.status = "Unloading"
            self.progressButton.setText("Complete Unloading")
        elif self.m_action_data.status == "Unloading":
            self.m_action_data.status = "Completed"
            # self.actionCompleted.emit()
        else:
            print("Action Already Completed")
        self.statusLabel.setText(f"Status: {self.m_action_data.status}")
        self.actionDataChanged.emit()

    def setValue(self, value):
        self.m_action_data = value

    def value(self):
        return self.m_action_data

    # Creates both QT and Python properties (I should have just done this in c++)
    action_data = Property(type=ActionItem, fget=value, fset=setValue)
