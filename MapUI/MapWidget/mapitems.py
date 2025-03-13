from PySide6.QtCore import Qt, QRectF, QEvent, QPointF
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QApplication, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem


actionPointPen = QPen(Qt.red, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
vehiclePen = QPen(Qt.blue, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

class ActionPointGI(QGraphicsItem):

    def __init__(self, x, y, text, mapScene):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.pen = actionPointPen
        self.text = QGraphicsTextItem(text, parent=self)
        self.text.setVisible(False)
        self.text.setPos(2, - 2.25*self.pen.width())

        self.mapScene = mapScene

        # Position in scene coords
        self.setPos(x,y)

    def boundingRect(self):
        penWidth = self.pen.width()
        return QRectF(- penWidth / 2, - penWidth / 2, penWidth,  penWidth)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        # Draw in item coords
        painter.drawPoint(0,0)

    # def itemChange(self, change, value):
    #     if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and value.isValid():
    #         temp_pos = value.toPointF()
    #         self.mapScene.point_group

    #     else:
    #         return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        '''
        Triggered byQEvent.GraphicsSceneHoverEnter

        The mouse cursor enters a hover item in a graphics scene (QGraphicsSceneHoverEvent).
        '''
        self.setScale(1.5)
        self.setCursor(Qt.PointingHandCursor)
        self.text.setVisible(True)
        self.text.setScale(0.75)
        event.accept() # accepting event here ensures event does not get propogated to parent widget

    def hoverLeaveEvent(self, event):
        '''
        Triggered byQEvent.GraphicsSceneHoverLeave

        The mouse cursor leaves a hover item in a graphics scene (QGraphicsSceneHoverEvent).
        '''
        self.setScale(1)
        self.setCursor(Qt.ArrowCursor)
        self.text.setVisible(False)
        self.text.setScale(1.5)
        event.accept()

    def mousePressEvent(self, event):
        '''
        Triggered by QEvent.GraphicsSceneMousePress

        Mouse press in a graphics scene (QGraphicsSceneMouseEvent).
        '''
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

