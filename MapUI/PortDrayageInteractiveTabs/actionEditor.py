from actionItem import ActionItem
from PySide6.QtCore import Qt, Property, Signal
from PySide6.QtWidgets import QGridLayout, QPushButton, QLabel, QWidget
import datetime as dt
from webSocketClient import WebSocketClient
from typing import Literal


class ActionEditor(QWidget):
    '''
    Editor widget which is created by the delegate. Contains the interactive elements required to modify the data in the model
    '''
    actionDataChanged = Signal()

    def __init__(self, parent, holding_signal = None):
        super().__init__(parent)
        self.m_action_data = ActionItem()
        self.holding_signal = holding_signal
        self.pb_text = ["Start Action", "Complete Action"]
        self.in_progress_message = "In Progress"

        # Internal widgets
        if self.m_action_data.status == self.in_progress_message:
            self.progressButton.setText(self.pb_text[1])
        else:
            self.progressButton = QPushButton(self.pb_text[0])
        self.requestInspectionButton = QPushButton("Request Further Inspection")
        self.completeInspectionButton = QPushButton("Complete Inspection")
        self.portArea = QWidget() # Placeholder b/c I have no clue what is intended to be in that box
        self.vehicleLabel = QLabel(f"Vehicle: {self.m_action_data.vehicle.veh_id}")
        self.cargoLabel = QLabel(f"With Cargo: {self.m_action_data.cargo.cargo_uuid}")
        self.statusLabel = QLabel(f"Status: {self.m_action_data.status}")

        # Layout widgets
        self.layout = QGridLayout()
        self.layout.addWidget(self.vehicleLabel, 0, 0, 1, 1)
        self.layout.addWidget(self.cargoLabel, 0, 1, 1, 1)
        self.layout.addWidget(self.statusLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.portArea, 0, 2, 3, 2)
        self.setLayout(self.layout)

        self.setAutoFillBackground(True)

        self.progressButton.clicked.connect(self.progressStatus)
        self.completeInspectionButton.clicked.connect(self.completeInspection)
        self.requestInspectionButton.clicked.connect(self.requestInspection)

        self.webSocketClient = WebSocketClient()
        self.webSocketClient.start_connection()

    def completeInspection(self):
        self.m_action_data.status = "Completed"
        self.m_action_data.timeCompleted = dt.datetime.now()
        m_action_json = self.m_action_data.convertToJSON()
        self.webSocketClient.send_message(m_action_json)
        self.statusLabel.setText(f"Status: {self.m_action_data.status}")
        self.actionDataChanged.emit()

    def requestInspection(self):
        self.m_action_data.status = "Completed"
        self.m_action_data.timeCompleted = dt.datetime.now()
        self.statusLabel.setText(f"Status: {self.m_action_data.status}")
        self.holding_signal.emit(self.m_action_data)
        self.actionDataChanged.emit()

    def progressStatus(self):
        if self.m_action_data.status == "Pending":
            self.m_action_data.status = self.in_progress_message
            self.progressButton.setText(self.pb_text[1])
        elif self.m_action_data.status == self.in_progress_message:
            self.m_action_data.status = "Completed"
            self.m_action_data.timeCompleted = dt.datetime.now()
            m_action_json = self.m_action_data.convertToJSON()
            self.webSocketClient.send_message(m_action_json)
        else:
            print("Action Already Completed")
        self.statusLabel.setText(f"Status: {self.m_action_data.status}")
        self.actionDataChanged.emit()

    def setValue(self, value):
        self.m_action_data = value
        if value is not None:
            self.vehicleLabel.setText(f"Vehicle: {value.vehicle.veh_id}")
            self.cargoLabel.setText(f"Cargo: {value.cargo.cargo_uuid}")
            self.statusLabel.setText(f"Status: {value.status}")

            # NOTE Python Switch statement does not have fall-through like other languages
            match self.m_action_data.actionPoint.name:
                case "PORT_CHECKPOINT":
                    self.layout.addWidget(self.completeInspectionButton, 2, 0, 1, 2)
                    self.layout.addWidget(self.requestInspectionButton, 2, 2, 1, 2)
                case "HOLDING_AREA":
                    self.pb_text = ["Start Inspection", "Complete Inspection"]
                    self.in_progress_message = "In Inspection"
                    self.layout.addWidget(self.progressButton, 2, 0, 1, 2)
                case "PICKUP":
                    self.pb_text = ["Start Loading", "Complete Loading"]
                    self.in_progress_message = "Loading"
                    self.layout.addWidget(self.progressButton, 2, 0, 1, 2)
                case "DROPOFF":
                    self.pb_text = ["Start Unloading", "Complete Unloading"]
                    self.in_progress_message = "Unloading"
                    self.layout.addWidget(self.progressButton, 2, 0, 1, 2)
                case _:
                    self.pb_text = ["Start Action", "Complete Action"]
                    self.in_progress_message = "In Progress"
                    self.layout.addWidget(self.progressButton, 2, 0, 1, 2)


    def value(self):
        return self.m_action_data

    # Creates both QT and Python properties (I should have just done this in c++)
    action_data = Property(type=ActionItem, fget=value, fset=setValue)
