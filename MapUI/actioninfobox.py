from PySide6.QtCore import QSize
from PySide6.QtWidgets import QGroupBox, QGridLayout, QLabel, QWidget


class ActionInfoBoxWidget(QGroupBox):

    def __init__(self, box_name):
        super().__init__(box_name)
        self.setMinimumSize(QSize(200,400))

        self.cmv_id_label = QLabel('cmv_id')
        self.cargo_id_label = QLabel('cargo_id')
        self.destination_lat_label = QLabel('destination_lat')
        self.destination_long_label = QLabel('destination_long')
        self.operation_label = QLabel('operation')
        self.action_id_label = QLabel('action_id')
        self.next_action_label = QLabel('next_action')

        self.cmv_id_info = QLabel()
        self.cargo_id_info = QLabel()
        self.destination_lat_info = QLabel()
        self.destination_long_info = QLabel()
        self.operation_info = QLabel()
        self.action_id_info = QLabel()
        self.next_action_info = QLabel()

        layout = QGridLayout()

        layout.addWidget(self.cmv_id_label, 0, 0)
        layout.addWidget(self.cargo_id_label, 1, 0)
        layout.addWidget(self.destination_lat_label, 2, 0)
        layout.addWidget(self.destination_long_label, 3, 0)
        layout.addWidget(self.operation_label, 4, 0)
        layout.addWidget(self.action_id_label, 5, 0)
        layout.addWidget(self.next_action_label, 6, 0)

        layout.addWidget(self.cmv_id_info, 0, 1)
        layout.addWidget(self.cargo_id_info, 1, 1)
        layout.addWidget(self.destination_lat_info, 2, 1)
        layout.addWidget(self.destination_long_info, 3, 1)
        layout.addWidget(self.operation_info, 4, 1)
        layout.addWidget(self.action_id_info, 5, 1)
        layout.addWidget(self.next_action_info, 6, 1)

        self.setLayout(layout)

    def updateAPData(self, ap_data):
        self.cmv_id_info.setText(str(ap_data['cmv_id']))
        self.cargo_id_info.setText(str(ap_data['cargo_id']))
        self.destination_lat_info.setText(str(ap_data['destination_lat']))
        self.destination_long_info.setText(str(ap_data['destination_long']))
        self.operation_info.setText(str(ap_data['operation']))
        self.action_id_info.setText(str(ap_data['action_id']))
        self.next_action_info.setText(str(ap_data['next_action']))


# class apTextLayout(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.cmv_id = ap_data['cmv_id']
#         self.cargo_id = ap_data['cargo_id']
#         self.destination_lat = ap_data['destination_lat']
#         self.destination_long = ap_data['destination_long']
#         self.operation = ap_data['operation']
#         self.action_id = ap_data['action_id']
#         self.next_action = ap_data['next_action']
