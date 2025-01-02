'''

'''

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QGroupBox, QGridLayout, QAbstractItemView, QListWidget, QListWidgetItem, QPushButton

class APOrderBoxWidget(QGroupBox):

    def __init__(self, box_name):
        super().__init__(box_name)
        self.setMinimumSize(QSize(200,400))

        self.apOrderList = APOrderList()
        self.addAPButton = QPushButton("Add Action Point")
        self.removeSelectedAP = QPushButton("Remove Selected Action Point")

        # TODO: Add button to add new point

        # TODO: Add button to remove a point

        # TODO: Allow points to be moved (Bonus if they can only be placed on roadway)

        # TODO: Add icons to list (Bonus if dynamic)

        # TODO: Load initial items

        layout = QGridLayout()
        layout.addWidget(self.apOrderList, 0, 0, 1, 2)
        layout.addWidget(self.addAPButton, 1, 0)
        layout.addWidget(self.removeSelectedAP, 1, 1)
        # layout.addWidget(self.apOrderList, 0, 0)


        self.setLayout(layout)

    def addActionPoint(self, ap_dict):
        '''
        Takes an action point dictionary and adds the action point to the map
        '''
        ap = ActionPointListItem(ap_dict, self.apOrderList)
        # TODO: Check if this line is redundant
        self.apOrderList.addItem(ap)

    def addActionPointList(self, ap_list):
        '''
        Add multiple action points
        '''
        for ap_dict in ap_list:
            self.addActionPoint(ap_dict)


class APOrderList(QListWidget):

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.InternalMove)

class ActionPointListItem(QListWidgetItem):

    def __init__(self, actionPointData, listWidget):
        super().__init__(listWidget)
        self.actionPointData = actionPointData

        self.ap_id = actionPointData['action_id']
        # TODO: Add a unique, human readable name for each action point
        self.setText(actionPointData['operation'])
