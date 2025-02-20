# from PySide6.QtCore import
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QStackedWidget
from actioninfobox import ActionInfoBoxWidget
from aporderbox import APOrderBoxWidget
from apWindow import APWindow
from PortDrayageInteractiveTabs.pdTabs import PDTabs
from tabBar import TabBar
from MysqlDataPull import Database
from cargoWindow import CargoWindow
from sqlalchemy import text
import json
import sys


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Port Drayage UI")
        self.setMinimumSize(800,600)
        self.tabBar = TabBar()

        self.apWindow = APWindow()
        # Prep action Point Widget
        # Get action points from SQL and populate widgets with them
        self.SQLdb = Database('PORT_DRAYAGE')
        actionData = self.SQLdb.getData()
        self.apWindow.readSQLActionPoints(actionData)

        # create and stack widgets
        self.pdTabs = PDTabs()
        self.cargoWindow = CargoWindow()
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.apWindow)
        self.stackedWidget.addWidget(self.cargoWindow)
        self.stackedWidget.addWidget(self.pdTabs)
        # self.stackedWidget.addWidget()

        self.setCentralWidget(self.stackedWidget)
        self.setMenuWidget(self.tabBar)

        # selection Change Events
        # self.interactiveMap.scene.selectionChanged.connect(self.showAPInfo)
        self.selectionUpdating = False
        # self.interactiveMap.selectionUpdate.connect(self.showAPInfo)
        # self.apOrderBox.selectionUpdate.connect(self.showAPInfo)

        # Add / remove AP button events
        # self.apOrderBox.addAPButton.clicked.connect()
        # self.apOrderBox.removeSelectedAP.clicked.connect(self.deleteActionPoint)
        # self.apOrderBox.updateSQLServerButton.clicked.connect(self.updateSQLServer)
        self.tabBar.currentChanged.connect(self.changeTab)

    def changeTab(self):
        '''
        Changes the visible widget in the central stacked widget based on selected tab.

        NOTE: PySide6 Documentation of setCurrentIndex is incorrect. It works as you would expect
        '''
        tabIndex = self.tabBar.currentIndex()
        self.stackedWidget.setCurrentIndex(tabIndex)

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
    
        

    # def updateSQLServer(self):
    #     '''
    #     Connect to sql server and update with new action point information
    #     TODO: Connect to sql in docker container of v2x hub
    #     '''
    #     ap_df = self.apOrderBox.convertToDataframe()
    #     # engine = self.SQLdb.dbconn
    #     ap_df.to_sql('freight', con=self.SQLdb.engine, if_exists='replace', index=False, schema='port_drayage',)

class App(QApplication):
    def __init__(self, args):
        super().__init__()

app = App(sys.argv)
window = MainWindow()
window.show()
app.exec()
