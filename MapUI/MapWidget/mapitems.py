from PySide6.QtCore import Qt, QRectF, QEvent
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QApplication, QGraphicsItem, QGraphicsLineItem

roadLinkPen = QPen(Qt.white, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
actionPointPen = QPen(Qt.red, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

def createRoadLink(x1, y1, x2, y2):
    roadLink = QGraphicsLineItem(x1, y1, x2, y2)
    roadLink.setPen(roadLinkPen)
    return roadLink


class ActionPoint(QGraphicsItem):

    def __init__(self, actionPointData, mapScene):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.pen = actionPointPen

        # TODO: Get data out of dict, store in some other form?
        self.actionPointData = actionPointData
        self.ap_id = actionPointData['action_id']
        self.mapScene = mapScene

        x = actionPointData['destination_long']
        y = actionPointData['destination_lat']

        # Position in scene coords
        self.setPos(x,y)

    def boundingRect(self):
        penWidth = self.pen.width()
        return QRectF(- penWidth / 2, - penWidth / 2, penWidth,  penWidth)

    def paint(self, painter, option, widget):
        painter.setPen(actionPointPen)
        # Draw in item coords
        painter.drawPoint(0,0)

    def hoverEnterEvent(self, event):
        '''
        Triggered byQEvent.GraphicsSceneHoverEnter

        The mouse cursor enters a hover item in a graphics scene (QGraphicsSceneHoverEvent).
        '''
        self.setScale(1.5)
        self.setCursor(Qt.PointingHandCursor)
        event.accept() # accepting event here ensures event does not get propogated to parent widget

    def hoverLeaveEvent(self, event):
        '''
        Triggered byQEvent.GraphicsSceneHoverLeave

        The mouse cursor leaves a hover item in a graphics scene (QGraphicsSceneHoverEvent).
        '''
        self.setScale(1)
        self.setCursor(Qt.ArrowCursor)
        event.accept()

    def mousePressEvent(self, event):
        '''
        Triggered by QEvent.GraphicsSceneMousePress

        Mouse press in a graphics scene (QGraphicsSceneMouseEvent).
        '''
        self.mapScene.clearSelection()
        self.setSelected(True)
        event.accept()
