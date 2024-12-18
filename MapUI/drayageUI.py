from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget
from MapWidget.mapwidget import MapWidget
from actioninfobox import ActionInfoBoxWidget
import sys


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Port Drayage UI")
        self.setMinimumSize(800,600)

        self.interactiveMap = MapWidget()
        # self.interactiveMap.show()

        self.ap_box = ActionInfoBoxWidget("Action Point Info")



        layout = QGridLayout()

        layout.addWidget(self.ap_box, 0, 0)
        layout.addWidget(self.interactiveMap, 0, 1)

        window = QWidget()
        window.setLayout(layout)

        self.setCentralWidget(window)


        self.interactiveMap.scene.selectionChanged.connect(self.showAPInfo)

    def showAPInfo(self):
        selected_ap = self.interactiveMap.scene.selectedItems()
        if len(selected_ap) >= 1:
            self.ap_box.updateAPData(selected_ap[0].actionPointData)






class App(QApplication):
    def __init__(self, args):
        super().__init__()


app = App(sys.argv)
window = MainWindow()
window.show()
app.exec()
