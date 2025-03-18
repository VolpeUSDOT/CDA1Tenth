from PySide6.QtCore import Qt, QRectF, QEvent, QPointF
from PySide6.QtGui import QPen, QColor, QBrush
from PySide6.QtWidgets import QApplication, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsRectItem


actionPointPen = QPen(Qt.red, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
vehiclePen = QPen(Qt.blue, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

class ActionPointGI(QGraphicsItem):
    def __init__(self, x, y, name, mapScene):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Set the position of the action point (for placement in the scene)
        self.setPos(x, y)

        # Fixed offset position for the text and background rectangle
        self.fixed_x = -25
        self.fixed_y = 5
        
        # Create text for the action point
        self.text = QGraphicsTextItem(f"Action Point: \"{name}\"", parent=self)
        self.text.setDefaultTextColor(Qt.black)  # Set text color to black
        self.text.setScale(.3)  # Change text scaling
        self.text.setPos(self.fixed_x, self.fixed_y)  # Set offset position for text

        # Create a background rectangle for the text
        self.background = QGraphicsRectItem(parent=self)
        self.background.setBrush(QBrush(Qt.white))  # Set background to white
        self.background.setZValue(-1)  # Send the rectangle layer back

        # Set the initial position and size of the background rectangle
        self.set_background_size()
        
        # Initially hide the background rect and text
        self.text.setVisible(False)
        self.background.setVisible(False)
        
        self.mapScene = mapScene

    def set_background_size(self):
        """Adjust the background rectangle to fit the text."""
        text_rect = self.text.boundingRect()  # Get the bounding rect of the text
        padding = 1  # Padding around the text
        # Set the rectangle position based on the fixed position
        self.background.setRect(self.fixed_x - padding, 
                                 self.fixed_y - padding,
                                 text_rect.width() * self.text.scale() + 2 * padding, 
                                 text_rect.height() * self.text.scale() + 2 * padding)

    def boundingRect(self):
        # Return an appropriate bounding rectangle that includes the action point
        return QRectF(-actionPointPen.width() / 2, -actionPointPen.width() / 2, actionPointPen.width(), actionPointPen.width())

    def paint(self, painter, option, widget):
        painter.setPen(actionPointPen)
        # Draw in item coords (the action point)
        painter.drawPoint(0, 0)

    def hoverEnterEvent(self, event):
        '''Triggered when the mouse cursor enters a hover item in the scene.'''
        self.setCursor(Qt.PointingHandCursor)
        self.text.setVisible(True)  # Show the text on hover
        self.background.setVisible(True)  # Show background
        event.accept()

    def hoverLeaveEvent(self, event):
        '''Triggered when the mouse cursor leaves a hover item in the scene.'''
        self.setCursor(Qt.ArrowCursor)
        self.text.setVisible(False)  # Hide the text
        self.background.setVisible(False)  # Hide background
        event.accept()

    def mousePressEvent(self, event):
        '''Triggered by mouse presses in the scene.'''
        self.mapScene.clearSelection()
        self.setSelected(True)
        event.accept()

class GraphicsPoint(QGraphicsItem):
    def __init__(self, x, y):
        super().__init__()
        # Position in scene coords
        self.setPos(x,y)
        self.setVisible(False)


class VehicleGI(QGraphicsItem):

    def __init__(self, x, y, description, mapScene):
        super().__init__()
        self.pen = vehiclePen
        self.loc = (x, y)
        self.mapScene = mapScene

        # Position in scene coords
        self.setPos(x,y)
        self.text = QGraphicsTextItem(description, parent=self)
        self.text.setPos(2, - 2.25*self.pen.width())

    def boundingRect(self):
        penWidth = self.pen.width()
        return QRectF(- penWidth / 2, - penWidth / 2, penWidth,  penWidth)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        # Draw in item coords
        painter.drawPoint(0,0)        

