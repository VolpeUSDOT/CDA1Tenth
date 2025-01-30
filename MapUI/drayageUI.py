# from PySide6.QtCore import
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QStackedWidget
from MapWidget.mapwidget import MapWidget, ActionPoint
from actioninfobox import ActionInfoBoxWidget
from aporderbox import APOrderBoxWidget
from PortDrayageInteractiveTabs.pdTabs import PDTabs
from tabBar import TabBar
from MysqlDataPull import Database
from sqlalchemy import text
import json
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
        self.tabBar = TabBar()

        # Get action points from SQL and populate widgets with them
        self.SQLdb = Database('port_drayage')
        self._readSQLActionPoints()

        layout = QGridLayout()

        layout.addWidget(self.apInfoBox, 0, 0)
        layout.addWidget(self.interactiveMap, 0, 1)
        layout.addWidget(self.apOrderBox, 0, 2)

        self.window = QWidget()
        self.window.setLayout(layout)

        #
        self.pdTabs = PDTabs()
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.window)
        self.stackedWidget.addWidget(self.pdTabs)


        self.setCentralWidget(self.stackedWidget)
        self.setMenuWidget(self.tabBar)

        # selection Change Events
        # self.interactiveMap.scene.selectionChanged.connect(self.showAPInfo)
        self.selectionUpdating = False
        self.interactiveMap.selectionUpdate.connect(self.showAPInfo)
        self.apOrderBox.selectionUpdate.connect(self.showAPInfo)

        # Add / remove AP button events
        # self.apOrderBox.addAPButton.clicked.connect()
        self.apOrderBox.removeSelectedAP.clicked.connect(self.deleteActionPoint)
        self.apOrderBox.updateSQLServerButton.clicked.connect(self.updateSQLServer)
        self.tabBar.currentChanged.connect(self.changeTab)

    def changeTab(self):
        '''
        Changes the visible widget in the central stacked widget based on selected tab.

        NOTE: PySide6 Documentation of setCurrentIndex is incorrect. It works as you would expect
        '''
        tabIndex = self.tabBar.currentIndex()
        if tabIndex == 0:
            self.stackedWidget.setCurrentIndex(0)
        elif tabIndex == 1:
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(0)

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
        '''
        Connect to sql server and update with new action point information
        TODO: Connect to sql in docker container of v2x hub
        '''
        ap_df = self.apOrderBox.convertToDataframe()
        # engine = self.SQLdb.dbconn
        ap_df.to_sql('freight', con=self.SQLdb.engine, if_exists='replace', index=False, schema='port_drayage',)

    def momJSONCreator(self):
        '''
        collect data for mobility operation message
        Returns:
            JSON string in MOM format #TODO: This is not finalized
        '''
        # NOTE area is likely going to be changed to action point or site
        area = {"latitude": self.apOrderBox.apOrderList.item(index).actionPointData["latitude"],
                "longitude": self.apOrderBox.apOrderList.item(index).actionPointData["longitude"],
                "name": self.apOrderBox.apOrderList.item(index).actionPointData["name"],
                "status": self.apOrderBox.apOrderList.item(index).actionPointData["status"],
                "is_notify": self.apOrderBox.apOrderList.item(index).actionPointData["is_notify"]}
        json_to_be = {"action_id": 1,
                      "area": area}

        return json.dumps(json_to_be)

class App(QApplication):
    def __init__(self, args):
        super().__init__()

app = App(sys.argv)
window = MainWindow()
window.show()
app.exec()
