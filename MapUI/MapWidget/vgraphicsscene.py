from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt

class ViewGraphicsScene (QGraphicsScene):

    def __init__(self, map_window):
        super().__init__()
        self.map_window = map_window

    ## Code to handle CTRL & Scroll Wheel for zoom
    def wheelEvent(self, event):
        # If control key not pressed then use wheelEvent for normal window scroll
        if not event.modifiers() & Qt.ControlModifier:
            event.ignore()
            return

        num_pixels = event.delta()

        if num_pixels > 0 :
            self.map_window.zoom_in()

        if num_pixels < 0 :
            self.map_window.zoom_out()

        event.accept()
