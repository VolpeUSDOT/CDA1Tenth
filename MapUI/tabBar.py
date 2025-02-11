# from PySide6.QtCore import
from PySide6.QtWidgets import QTabBar

class TabBar(QTabBar):

    def __init__(self):
        super().__init__()
        self.addTab("Map")
        self.addTab("Cargo Items")
        self.addTab("Port Interactions")

        #self.setShape(QTabBar.RoundedNorth)
