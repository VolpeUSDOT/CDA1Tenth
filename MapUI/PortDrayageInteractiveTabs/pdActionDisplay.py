from PortDrayageInteractiveTabs.actionListTypeFilter import ActionListTypeFilter
from PortDrayageInteractiveTabs.actionListStatusFilter import ActionListStatusFilter
from PortDrayageInteractiveTabs.actionListViews import PendingActionView, CompletedActionView
from PySide6.QtCore import Qt, Property, QSortFilterProxyModel, Signal, Slot
from PySide6.QtWidgets import QGridLayout, QPushButton, QLabel, QWidget

TAB_DICT = {"Loading": ["PICKUP"],
            "Unloading": ["DROPOFF"],
            "Inspection": ["HOLDING_AREA", "PORT_CHECKPOINT"]}

TAB_LABELS = {"Loading": ['''# Port Drayage Loading Area''', '''## Pending Loading Actions''', '''## Completed Loading Actions'''],
              "Unloading": ['''# Port Drayage Unloading Area''', '''## Pending Unloading Actions''', '''## Completed Unloading Actions'''],
              "Inspection": ['''# Port Drayage Inspection Area''', '''## Pending Inspection Actions''', '''## Completed Inspection Actions''']}

class PDActionDisplay(QWidget):
    '''
    Main Widget for the loading display to be referenced outside this file
    '''
    deleteList = Signal(list)

    def __init__(self, model):
        super().__init__()
        # Filter list to correct Action Types
        self.model = model
        self.type = None
        self.typeModel = ActionListTypeFilter()
        self.typeModel.setSourceModel(self.model)

        self.inProgressModel = ActionListStatusFilter("Does Not Equal", "Completed")
        self.inProgressModel.setSourceModel(self.typeModel)
        self.completedModel = ActionListStatusFilter("Equals", "Completed")
        self.completedModel.setSourceModel(self.typeModel)

        self.pendingActionView = PendingActionView()
        self.completedActionView = CompletedActionView()

        self.pendingActionView.setModel(self.inProgressModel)
        self.completedActionView.setModel(self.completedModel)

        self.title = QLabel("TAB_LABELS")
        self.title.setTextFormat(Qt.TextFormat.MarkdownText)

        self.pendingLabel = QLabel("TAB")
        self.pendingLabel.setTextFormat(Qt.TextFormat.MarkdownText)

        self.completeLabel = QLabel("T")
        self.completeLabel.setTextFormat(Qt.TextFormat.MarkdownText)

        self.completedResetButton = QPushButton("Clear Completed Actions")

        layout = QGridLayout()
        layout.addWidget(self.title, 0, 0, 1, 1)
        layout.addWidget(self.pendingLabel, 1, 0, 1, 1)
        layout.addWidget(self.pendingActionView, 2, 0, 1, 1)
        layout.addWidget(self.completeLabel, 3, 0, 1, 1)
        layout.addWidget(self.completedActionView, 4, 0, 1, 1)
        layout.addWidget(self.completedResetButton, 5, 0, 1, 1)

        self.setLayout(layout)

        self.completedResetButton.clicked.connect(self.deleteListFromModel)

    def deleteListFromModel(self):
        self.completedActionView.selectAll()
        index_list = self.completedActionView.selectedIndexes()
        print(index_list)
        print("=" *80)
        self.deleteList.emit(index_list)

    def updateActionType(self, type):
        self.type = type
        self.typeModel.updateFilterItems(TAB_DICT[self.type])
        self.title.setText(TAB_LABELS[self.type][0])
        self.pendingLabel.setText(TAB_LABELS[self.type][1])
        self.completeLabel.setText(TAB_LABELS[self.type][2])
