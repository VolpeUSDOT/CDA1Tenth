'''
Widget to contain all port drayage tabs in one item
'''
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QTabBar
from PortDrayageInteractiveTabs.pdLoading import PDLoadingWidget
from PortDrayageInteractiveTabs.pdUnloading import PDUnloadingWidget
from PortDrayageInteractiveTabs.pdInspection import PDInspectionWidget

class PDTabs(QMainWindow):


    def __init__(self):
        super().__init__()

        self.loadingWidget = PDLoadingWidget()
        self.unloadingWidget = PDUnloadingWidget()
        self.inspectionWidget = PDInspectionWidget()

        self.tabBar = QTabBar()
        self.tabBar.addTab('Loading')
        self.tabBar.addTab('Unloading')
        self.tabBar.addTab('Inspection')

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.loadingWidget)
        self.stackedWidget.addWidget(self.unloadingWidget)
        self.stackedWidget.addWidget(self.inspectionWidget)

        self.setCentralWidget(self.stackedWidget)
        self.setMenuWidget(self.tabBar)

        self.tabBar.currentChanged.connect(self.changeTab)

    def changeTab(self):
        '''
        Changes the visible widget in the central stacked widget based on selected tab.

        NOTE: PySide6 Documentation of setCurrentIndex is incorrect. It works as you would expect
        '''
        tabIndex = self.tabBar.currentIndex()
        self.stackedWidget.setCurrentIndex(tabIndex)
