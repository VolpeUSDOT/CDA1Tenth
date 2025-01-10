# from PySide6.QtCore import
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget
from MapWidget.mapwidget import MapWidget, ActionPoint
from actioninfobox import ActionInfoBoxWidget
from aporderbox import APOrderBoxWidget
from MysqlDataPull import Database

import sys


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Port Drayage UI")
        self.setMinimumSize(800,600)

        self.interactiveMap = MapWidget()
        self.apOrderBox = APOrderBoxWidget("Change order of Action Points")
        self.apInfoBox = ActionInfoBoxWidget("Action Point Info")

        # Get action points from SQL and populate widgets with them
        self.SQLdb = Database('port_drayage')
        self._readSQLActionPoints()

        layout = QGridLayout()

        layout.addWidget(self.apInfoBox, 0, 0)
        layout.addWidget(self.interactiveMap, 0, 1)
        layout.addWidget(self.apOrderBox, 0, 2)

        window = QWidget()
        window.setLayout(layout)

        self.setCentralWidget(window)

        # selection Change Events
        # self.interactiveMap.scene.selectionChanged.connect(self.showAPInfo)
        self.selectionUpdating = False
        self.interactiveMap.selectionUpdate.connect(self.showAPInfo)
        self.apOrderBox.selectionUpdate.connect(self.showAPInfo)

        # Add / remove AP button events
        # self.apOrderBox.addAPButton.clicked.connect()
        self.apOrderBox.removeSelectedAP.clicked.connect(self.deleteActionPoint)
        self.apOrderBox.updateSQLServerButton.clicked.connect(self.updateSQLServer)

    def deleteActionPoint(self):
        '''
        Delete selected action point from both list and map
        '''
        # Get selection
        selected_ap_list = self.interactiveMap.scene.selectedItems()
        if not selected_ap_list: return #List isn't empty
        ap = selected_ap_list[0] # Select 1st item (Only should have 1 item)
        self.interactiveMap.scene.clearSelection()
        self.interactiveMap.scene.removeItem(ap) # Remove it from map
        del ap # Delete from memory

        # Get selection
        selected_ap_list = self.apOrderBox.apOrderList.selectedItems()
        if not selected_ap_list: return #List isn't empty
        ap = selected_ap_list[0] # Select 1st item (Only should have 1 item)
        self.apOrderBox.apOrderList.clearSelection()
        self.apOrderBox.apOrderList.takeItem(self.apOrderBox.apOrderList.row(ap)) #remove it from list
        del ap # Delete from memory (Yes, memory management in python!)


    def showAPInfo(self):
        '''
        Match selection from list and map and send data to apInfoBox
        '''
        # Prevent loop run
        if self.selectionUpdating == True:
            return
        else:
            self.selectionUpdating = True
            # Check which widget had a selection change (returns null if called directly)
            source = self.sender()
            if source == self.interactiveMap:
                selected_ap_list = self.interactiveMap.scene.selectedItems()
                if not selected_ap_list: return #List isn't empty
                # Multiple can be selected, but we should only ever have one selected
                if len(selected_ap_list) >= 1:
                    selected_ap = selected_ap_list[0]
                    # Update the infobox
                    self.apInfoBox.updateAPData(selected_ap.actionPointData)
                    # Match selection change to listbox
                    ap_id = selected_ap.ap_id
                    self.apOrderBox.apOrderList.clearSelection()
                    ap_list = [self.apOrderBox.apOrderList.item(x) for x in range(self.apOrderBox.apOrderList.count())]
                    for ap in ap_list:
                        if ap.ap_id == ap_id:
                            ap.setSelected(True)
            else:
                selected_ap_list = self.apOrderBox.apOrderList.selectedItems()
                if not selected_ap_list: return #List isn't empty
                # Multiple can be selected, but we should only ever have one selected
                if len(selected_ap_list) >= 1:
                    selected_ap = selected_ap_list[0]
                    # Update the infobox
                    self.apInfoBox.updateAPData(selected_ap.actionPointData)
                    # Match selection change to map
                    ap_id = selected_ap.ap_id
                    self.interactiveMap.scene.clearSelection()
                    item_list = self.interactiveMap.scene.items()
                    for item in item_list:
                        # Ignore line items used to draw the roads as they can not be selected
                        if isinstance(item, ActionPoint):
                            ap = item
                            if ap.ap_id == ap_id:
                                ap.setSelected(True)
            # Allow runs again
            self.selectionUpdating = False

    def _readSQLActionPoints(self):
        '''
        Pull action points from SQL and add them to map and list
        '''
        actionData = self.SQLdb.getData()
        for _, actionPointData in actionData.iterrows():
            ap_dict = actionPointData.to_dict()
            self.interactiveMap.addActionPoint(ap_dict)
            self.apOrderBox.addActionPoint(ap_dict)

    def updateSQLServer(self):
        ap_df = self.apOrderBox.convertToDataframe()
        engine = self.SQLdb.createSQLEngine()
        with engine.connect() as connection:
            print('Insert Attempt')
            ap_df.to_sql('freight', con=connection, if_exists='replace', index=False)
            connection.commit()
            connection.close()
            print('Insert Finished')
            #connection.

        # engine = self.SQLdb.dbconn
        # mycursor = engine.cursor()



class App(QApplication):
    def __init__(self, args):
        super().__init__()

app = App(sys.argv)
window = MainWindow()
window.show()
app.exec()
