'''
Port Drayage Loading Area Interface:

Intended to represent the actions taking place at the loading station of a port (not vehicle centric)

When a vehicle enters the loading area (maybe not called area anymore), it should add an interactable pending action

Actions contain info on vehicle, cargo(container) status(pending, loading, completed), requested timestamp, completed timestamp

pending and loading actions have a button to interact with and progress the action. Once an action is completed, the interactable object is removed and the info of the action is added to a completed action log
'''
import time
from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtWidgets import QGroupBox, QGridLayout, QAbstractItemView, QListWidget, QListWidgetItem, QPushButton, QCheckBox, QLabel, QWidget



class PDLoadingWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.title = QLabel('''# Port Drayage Loading Area''')
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.pendingActionList = PendingActionList()
        self.completedActionList = QListWidget()
        self.completedResetButton = QPushButton("Clear")

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 1)
        layout.addWidget(self.pendingActionList, 1, 0, 1, 1)
        layout.addWidget(self.completedActionList, 2, 0, 1, 1)
        layout.addWidget(self.completedResetButton, 3, 0, 1, 1)

        self.setLayout(layout)

        self.addLoadingAction()

    def addLoadingAction(self):
        '''
        Add a new LoadingActionWidget to the pending actions list
        '''
        listWidgetItem = LoadingActionListItem(self.pendingActionList)

        self.pendingActionList.addItem(listWidgetItem)

        loadingActionWidget = LoadingActionWidget()

        listWidgetItem.setSizeHint(loadingActionWidget.sizeHint())
        self.pendingActionList.setItemWidget(listWidgetItem, loadingActionWidget)


class PendingActionList(QListWidget):
    def __init__(self):
        super().__init__()

        self.itemClicked.connect(self.onItemClick)

    def onItemClick(self, item):
        if item.status == "Completed":
            del item


class LoadingActionWidget(QWidget):
    # actionCompleted = Signal()

    def __init__(self):
        super().__init__()

        # Right when action is created, get time for action request
        self.requestedTime = time.time()

        # Internal widgets
        self.progressButton = QPushButton("Start Loading")
        self.portArea = QWidget() # Placeholder b/c I have no clue what is intended to be in that box
        self.vehicleLabel = QLabel("Vehicle: ")
        self.cargoLabel = QLabel("With Cargo: ")
        self.statusLabel = QLabel("Status: ")
        self.status = "Pending"

        # Layout widgets
        layout = QGridLayout()
        layout.addWidget(self.vehicleLabel, 0, 0, 1, 1)
        layout.addWidget(self.cargoLabel, 0, 1, 1, 1)
        layout.addWidget(self.statusLabel, 1, 0, 1, 1)
        layout.addWidget(self.progressButton, 2, 0, 1, 2)
        layout.addWidget(self.portArea, 0, 2, 3, 2)
        self.setLayout(layout)

        # Connections
        # self.progressButton.clicked.connect(self.progressState)

    def progressState(self):
        if self.status == "Pending":
            self.status = "Loading"
            self.progressButton.setText("Complete Loading")
        elif self.status == "Loading":
            self.status = "Completed"
            # self.actionCompleted.emit()

        else:
            print("Action Already Completed")


class LoadingActionListItem(QListWidgetItem):

    def __init__(self, listWidget):
        super().__init__(listWidget)
