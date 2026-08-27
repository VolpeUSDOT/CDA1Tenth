""" """

import pandas as pd
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QCheckBox,
)


class APOrderBoxWidget(QGroupBox):
    selectionUpdate = Signal()

    def __init__(self, box_name):
        super().__init__(box_name)
        self.setMinimumSize(QSize(200, 400))

        self.apOrderList = APOrderList()
        self.loopCheckBox = QCheckBox("Loop Actions")
        self.addAPButton = QPushButton("Add Action Point")
        self.removeSelectedAP = QPushButton("Remove Selected Action Point")
        self.updateSQLServerButton = QPushButton("Push Action List")

        # TODO: Add button to add new point

        # TODO: Allow points to be moved (Bonus if they can only be placed on roadway)
        self.moveUpButton = QPushButton("Move Up")
        self.moveDownButton = QPushButton("Move Down")

        # TODO: Add icons to list (Bonus if dynamic)

        layout = QGridLayout()
        layout.addWidget(self.apOrderList, 0, 0, 1, 2)
        layout.addWidget(self.loopCheckBox, 1, 0, 1, 2)
        layout.addWidget(self.addAPButton, 2, 0)
        layout.addWidget(self.removeSelectedAP, 2, 1)
        layout.addWidget(self.updateSQLServerButton, 3, 0, 1, 2)

        # Arrow Buttons
        layout.addWidget(self.moveUpButton, 4, 0)
        layout.addWidget(self.moveDownButton, 4, 1)

        self.setLayout(layout)

        # Call for custom event
        self.apOrderList.itemSelectionChanged.connect(self._compactedSignal)

        # Connect move buttons
        self.moveUpButton.clicked.connect(self.moveItemUp)
        self.moveDownButton.clicked.connect(self.moveItemDown)

    def _compactedSignal(self):
        """
        Send custom signal that selection has changed only when new item is selected, ignore when selection is cleared to prevent other code from running multiple times
        """
        selected_ap_list = self.apOrderList.selectedItems()
        if not selected_ap_list:
            return  # List isn't empty
        # Multiple can be selected, but we should only ever have one selected
        if len(selected_ap_list) == 1:
            self.selectionUpdate.emit()
        else:
            print("Error, multiple ap were selected in map which shouldn't be possible")

    def addActionPoint(self, ap_dict):
        """
        Takes an action point dictionary and adds the action point to the map
        """
        ap = ActionPointListItem(ap_dict, self.apOrderList)
        # TODO: Check if this line is redundant
        self.apOrderList.addItem(ap)

    def addActionPointList(self, ap_list):
        """
        Add multiple action points
        """
        for ap_dict in ap_list:
            self.addActionPoint(ap_dict)

    def convertToDataframe(self):
        """
        Converts list to pandas df, generating columns required for linked list calls later
        """
        ap_list = [
            self.apOrderList.item(x).actionPointData
            for x in range(self.apOrderList.count())
        ]
        ap_df = pd.DataFrame(ap_list)
        ap_df["action_id"] = ap_df.index

        # NOTE: List of ap info (updated SQL data columns) "id", "vehicle_name", "cargo_name", "action_id", "prev_action_id", "next_action_id", "action_name", "action_status", "longitude", "latitude", "is_notify", "created_at", "updated_at"

        isLooping = self.loopCheckBox.checkState()
        if isLooping:
            ap_df["next_action_id"] = ap_df["action_id"].shift(
                1, fill_value=ap_df["action_id"].iloc[-1]
            )
            ap_df["prev_action_id"] = ap_df["action_id"].shift(
                -1, fill_value=ap_df["action_id"].iloc[0]
            )
        else:
            # TODO: Fill vlaues -1
            ap_df["next_action"] = ap_df["action_id"].shift(1)
            ap_df["prev_action_id"] = ap_df["action_id"].shift(-1)
        return ap_df

    def moveItemUp(self):
        """Moves item up when move up button clicked."""
        self.moveItem(-1)

    def moveItemDown(self):
        """Moves item down when move down button clicked."""
        self.moveItem(1)

    def moveItem(self, direction):
        """Selects the item to move and swaps with the item above or below it. Handles
        errors in the case of going out of bounds or not selecting an item.

        Args:
            direction (int): 1 == up, -1 == down
        """
        selectedItems = self.apOrderList.selectedItems()
        if not selectedItems:
            return

        current_index = self.apOrderList.row(selectedItems[0])
        new_index = current_index + direction

        if new_index < 0 or new_index >= self.apOrderList.count():
            return

        item_to_move = self.apOrderList.takeItem(current_index)
        self.apOrderList.insertItem(new_index, item_to_move)
        self.apOrderList.setCurrentItem(item_to_move)


class APOrderList(QListWidget):

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.InternalMove)  # Possibly remove?


class ActionPointListItem(QListWidgetItem):

    def __init__(self, actionPointData, listWidget):
        super().__init__(listWidget)
        self.actionPointData = actionPointData
        self.ap_id = actionPointData["action_id"]
        # TODO: Add a unique, human readable name for each action point
        self.setText(actionPointData["operation"])
