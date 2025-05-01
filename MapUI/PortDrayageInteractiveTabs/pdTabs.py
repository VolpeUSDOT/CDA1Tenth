'''
Widget to contain all port drayage tabs in one item
'''
from PortDrayageInteractiveTabs.actionListModel import ActionListModel
from PortDrayageInteractiveTabs.pdActionDisplay import PDActionDisplay
from PySide6.QtCore import Qt, Property, QSortFilterProxyModel, Signal, Slot
from PySide6.QtWidgets import QGridLayout, QPushButton, QLabel, QWidget, QMainWindow, QStackedWidget, QTabBar

TAB_LIST = ["Loading", "Unloading", "Inspection"]



class PDTabs(QMainWindow):

    def __init__(self, loading_signal, unloading_signal, inspection_signal, holding_signal):
        super().__init__()

        self.model = ActionListModel()
        # self.loadingWidget = PDLoadingWidget(loading_signal)
        # self.unloadingWidget = PDUnloadingWidget(unloading_signal)
        # self.inspectionWidget = PDInspectionWidget(inspection_signal, holding_signal)

        self.tabBar = QTabBar()
        for tab in TAB_LIST:
            self.tabBar.addTab(tab)

        self.actionDisplay = PDActionDisplay(self.model)
        self.changeTab()

        # self.stackedWidget = QStackedWidget()
        # self.stackedWidget.addWidget(self.loadingWidget)
        # self.stackedWidget.addWidget(self.unloadingWidget)
        # self.stackedWidget.addWidget(self.inspectionWidget)

        self.setCentralWidget(self.actionDisplay)
        self.setMenuWidget(self.tabBar)

        self.tabBar.currentChanged.connect(self.changeTab)

        loading_signal.connect(self.addAction)
        unloading_signal.connect(self.addAction)
        inspection_signal.connect(self.addAction)

        self.actionDisplay.deleteList.connect(self.deleteMultipleItems)

    def changeTab(self):
        '''
        Changes the visible widget in the central stacked widget based on selected tab.
        NOTE: PySide6 Documentation of setCurrentIndex is incorrect. It works as you would expect
        '''
        tab_index = self.tabBar.currentIndex()
        tab_name = TAB_LIST[tab_index]
        self.actionDisplay.updateActionType(tab_name)
        # self.stackedWidget.setCurrentIndex(tabIndex)

    @Slot()
    def addAction(self, action):
        self.model.actions.append(action)
        print(self.model.actions)
        i = self.model.rowCount()
        self.actionDisplay.pendingActionView.openPersistentEditor(self.model.index(i,0))
        self.model.layoutChanged.emit()

    # def deleteAction(self):
    #     indexes = self.pendingActionView.selectedIndexes()
    #     if indexes:
    #         # Indexes is a list of a single item in single-select mode.
    #         index = indexes[0]
    #         # Remove the item and refresh.
    #         del self.model.actions[index.row()]
    #         self.model.layoutChanged.emit()
    #         # Clear the selection (as it is no longer valid).
    #         self.pendingActionView.clearSelection()

    def deleteMultipleItems(self, index_list):
        print(index_list)
        for index in index_list:
            del self.model.actions[index.row()]
        self.model.layoutChanged.emit()
