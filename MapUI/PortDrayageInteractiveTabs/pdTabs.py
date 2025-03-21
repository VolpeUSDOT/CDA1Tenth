'''
Widget to contain all port drayage tabs in one item
'''
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QTabBar, QPushButton, QVBoxLayout, QWidget
from PortDrayageInteractiveTabs.pdLoading import PDLoadingWidget
from PortDrayageInteractiveTabs.pdUnloading import PDUnloadingWidget
from PortDrayageInteractiveTabs.pdInspection import PDInspectionWidget

class PDTabs(QMainWindow):


    def __init__(self, loading_signal, unloading_signal, inspection_signal, holding_signal):
        super().__init__()

        self.loadingWidget = PDLoadingWidget(loading_signal)
        self.unloadingWidget = PDUnloadingWidget(unloading_signal)
        self.inspectionWidget = PDInspectionWidget(inspection_signal, holding_signal)
        self.completedResetButton = QPushButton("Clear")

        self.tabBar = QTabBar()
        self.tabBar.addTab('Loading')
        self.tabBar.addTab('Unloading')
        self.tabBar.addTab('Inspection')

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.loadingWidget)
        self.stackedWidget.addWidget(self.unloadingWidget)
        self.stackedWidget.addWidget(self.inspectionWidget)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tabBar)
        layout.addWidget(self.stackedWidget)
        layout.addWidget(self.completedResetButton)
        self.setCentralWidget(central_widget)
        self.setMenuWidget(self.tabBar)

        self.tabBar.currentChanged.connect(self.changeTab)
        self.completedResetButton.clicked.connect(self.clearActions)

    def changeTab(self):
        '''
        Changes the visible widget in the central stacked widget based on selected tab.

        NOTE: PySide6 Documentation of setCurrentIndex is incorrect. It works as you would expect
        '''
        tabIndex = self.tabBar.currentIndex()
        self.stackedWidget.setCurrentIndex(tabIndex)
    
    def clearActions(self):
        '''
        Clear all actions from all tabs
        '''
        self.loadingWidget.deleteLoadingActions()
        self.unloadingWidget.deleteUnloadingActions()
        self.inspectionWidget.deleteInspectionActions()
