'''

'''
import pandas as pd
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QGroupBox, QGridLayout, QAbstractItemView, QListWidget, QListWidgetItem, QPushButton, QCheckBox

class APOrderBoxWidget(QGroupBox):
    selectionUpdate = Signal()

    def __init__(self, box_name):
        super().__init__(box_name)
        self.setMinimumSize(QSize(200,400))

        self.apOrderList = APOrderList()
        self.loopCheckBox = QCheckBox("Loop Actions")
        self.addAPButton = QPushButton("Add Action Point")
        self.removeSelectedAP = QPushButton("Remove Selected Action Point")
        self.updateSQLServerButton = QPushButton("Push Action List")

        # TODO: Add button to add new point

        # TODO: Allow points to be moved (Bonus if they can only be placed on roadway)

        # TODO: Add icons to list (Bonus if dynamic)

        layout = QGridLayout()
        layout.addWidget(self.apOrderList, 0, 0, 1, 2)
        layout.addWidget(self.loopCheckBox, 1, 0, 1, 2)
        layout.addWidget(self.addAPButton, 2, 0)
        layout.addWidget(self.removeSelectedAP, 2, 1)
        layout.addWidget(self.updateSQLServerButton, 3, 0, 1, 2)

        self.setLayout(layout)

        # Call for custom event
        self.apOrderList.itemSelectionChanged.connect(self._compactedSignal)

    def _compactedSignal(self):
        '''
        Send custom signal that selection has changed only when new item is selected, ignore when selection is cleared to prevent other code from running multiple times
        '''
        selected_ap_list = self.apOrderList.selectedItems()
        if not selected_ap_list: return #List isn't empty
        # Multiple can be selected, but we should only ever have one selected
        if len(selected_ap_list) == 1:
            self.selectionUpdate.emit()
        else:
            print("Error, multiple ap were selected in map which shouldn't be possible")

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

    def convertToDataframe(self):
        '''
        Converts list to pandas df, generating columns required for linked list calls later
        '''
        ap_list = [self.apOrderList.item(x).actionPointData for x in range(self.apOrderList.count())]
        ap_df = pd.DataFrame(ap_list)
        ap_df['action_id'] = ap_df.index

        # NOTE: List of ap info (updated SQL data columns) "id", "vehicle_name", "cargo_name", "action_id", "prev_action_id", "next_action_id", "action_name", "action_status", "longitude", "latitude", "is_notify", "created_at", "updated_at"

        isLooping = self.loopCheckBox.checkState()
        if isLooping:
            ap_df['next_action_id'] = ap_df['action_id'].shift(1, fill_value=ap_df['action_id'].iloc[-1])
            ap_df['prev_action_id'] = ap_df["action_id"].shift(-1,fill_value=ap_df['action_id'].iloc[0] )
        else:
            #TODO: Fill vlaues -1
            ap_df['next_action'] = ap_df['action_id'].shift(1)
            ap_df['prev_action_id'] = ap_df["action_id"].shift(-1)
        return ap_df

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
