'''
Port Drayage Loading Area Interface:

Intended to represent the actions taking place at the loading station of a port (not vehicle centric)

When a vehicle enters the loading area (maybe not called area anymore), it should add an interactable pending action

Actions contain info on vehicle, cargo(container) status(pending, loading, completed), requested timestamp, completed timestamp

pending and loading actions have a button to interact with and progress the action. Once an action is completed, the interactable object is removed and the info of the action is added to a completed action log
'''
from PySide6.QtCore import QAbstractListModel, Qt, Property, QSortFilterProxyModel, Signal
from PySide6.QtWidgets import QGridLayout, QAbstractItemView, QPushButton, QListView, QLabel, QWidget, QStyledItemDelegate
import datetime as dt


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
        self.timeRequested = dt.datetime.now()
        self.timeCompleted = None

    def completedActionDisplay(self):
        text = 'Vehicle: {} \t\t Cargo: {} \t\t ActionID: {} \t Requested Time: {} \t Completed Time: {}'.format(self.vehicle, self.cargo, self.actionID, self.timeRequested, self.timeCompleted)
        return text


class PDLoadingWidget(QWidget):
    '''
    Main Widget for the loading display to be referenced outside this file
    '''
    def __init__(self):
        super().__init__()
        self.model = LoadingActionList(loadingActions=[ActionItem()])
        self.loadingActionView = PendingActionView()
        self.completedActionView = CompletedActionView()
        self.inProgressFilterProxyModel = InProgressActionListProxyModel()
        self.inProgressFilterProxyModel.setSourceModel(self.model)
        self.completedFilterProxyModel = CompletedActionListProxyModel()
        self.completedFilterProxyModel.setSourceModel(self.model)

        self.loadingActionView.setModel(self.inProgressFilterProxyModel)
        self.completedActionView.setModel(self.completedFilterProxyModel)

        self.loadingActionView.openPersistentEditor(self.inProgressFilterProxyModel.index(0,0)) # TODO: Remove later when items appear based on received MOMs



        self.title = QLabel('''# Port Drayage Loading Area''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.completedResetButton = QPushButton("Clear")

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 1)
        layout.addWidget(self.loadingActionView, 1, 0, 1, 1)
        layout.addWidget(self.completedActionView, 2, 0, 1, 1)
        layout.addWidget(self.completedResetButton, 3, 0, 1, 1)

        self.setLayout(layout)

    def addLoadingAction(self):

        self.model.loadingActions.append(ActionItem())
        i = self.model.rowCount()
        self.loadingActionView.openPersistentEditor(self.model.index(i,0))
        self.model.layoutChanged.emit()

    def deleteLoadingAction(self):
        indexes = self.loadingActionView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model.loadingActions[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.loadingActionView.clearSelection()


class PendingActionView(QListView):
    '''
    Subclass of list view for showing a list of editable action items
    '''
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformItemSizes(True)
        self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)


class CompletedActionView(QListView):
    '''
    Subclass of list view for showing a list of immutable, completed action items
    '''
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setUniformItemSizes(True)
        # self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


class InProgressActionListProxyModel(QSortFilterProxyModel):
    '''
    Filter for model that only allows uncompleted actions through
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


class LoadingActionList(QAbstractListModel):
    '''
    Model that stores data for the project
    '''
    def __init__(self, *args, loadingActions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.loadingActions = loadingActions or []

    def rowCount(self, index):
        return len(self.loadingActions)

    def data(self, index, role):
        action = self.loadingActions[index.row()]

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


        self.loadingActions[index.row()] = value
        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        flags = super().flags(index)
        if self.loadingActions[index.row()].status != "Completed":
            # |= is a special operator required to add a new flag to the list of flags
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags


class ActionDelegate(QStyledItemDelegate):
    '''
    Creates an alternate, interactable and editable view for items in the model and connects the data in the temporary editor with the model
    '''
    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self, option, index):
        editor = ActionEditor(None)
        return editor.sizeHint()

    def createEditor(self, parent, option, index):
        editor = ActionEditor(parent)
        # Connect the dataChanged signal from each item to update the backend model data
        editor.actionDataChanged.connect(self.commit_from_editor) # TODO Might need to lose this line
        return editor

    def setEditorData(self, editor, index):
        editor.action_data = index.data(role=Qt.ItemDataRole.EditRole)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.action_data)

    def commit_from_editor(self):
        '''
        Commits the data to the model and closes the editor
        '''
        editor = self.sender()
        # The commitData signal must be emitted when we've finished editing
        # and need to write our changed back to the model.
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)

    def updateEditorGeometry(self, editor, option, index):
        return super().updateEditorGeometry(editor, option, index)


class ActionEditor(QWidget):
    '''
    Editor widget which is created by the delegate. Contains the interactive elements required to modify the data in the model
    '''
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
            self.m_action_data.status = "Loading"
            self.progressButton.setText("Complete Loading")
        elif self.m_action_data.status == "Loading":
            self.m_action_data.status = "Completed"
            self.m_action_data.timeCompleted = dt.datetime.now()
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
