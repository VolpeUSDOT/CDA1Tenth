from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QGraphicsView, QGraphicsLineItem, QGraphicsItem
from PySide6.QtGui import QPen
from MapWidget.vgraphicsscene import ViewGraphicsScene
from MapWidget.mapitems import ActionPointGI, VehicleGI
import geopandas as gpd
import yaml

pgm_map = '../MapUI/PortDrayageData/garage.pgm'
map_info = '../MapUI/PortDrayageData/garage.yaml'
graph = '../MapUI/PortDrayageData/garage_graph_port_drayage_v2.geojson'

roadLinkPen = QPen(Qt.white, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

# Subclass QMainWindow to customize your application's main window
class MapWidget(QWidget):
    selectionUpdate = Signal(ActionPointGI)

    def __init__(self, pgm_map_fp = pgm_map, map_info_fp = map_info, graph_fp = graph):
        super().__init__()
        self.setMinimumSize(QSize(600,400))
        self.zoomLevel = 0

        # Create QGraphicsScene and QGraphicsView
        self.scene = ViewGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        # Process data from port drayage
        mapInfo = self._readMapInfo(map_info_fp)
        self.x_origin = mapInfo['origin'][0]
        self.y_origin = mapInfo['origin'][1]
        self.resolution = mapInfo['resolution']
        self.points, lines = self._readGraphFile(graph_fp, roundPixelPosition = True)

        # Add all road segments to scene
        road_group = self.scene.createItemGroup([])
        for _, line in lines.iterrows():
            roadLink = createRoadLink(line['start_x'], line['start_y'], line['end_x'], line['end_y'])
            self.scene.addItem(roadLink)
            road_group.addToGroup(roadLink)

        # point_group = self.scene.createItemGroup([])
        # for point in points.iterrows():
        #     gp = GraphicsPoint(point['adjusted_x'], point['adjusted_y'])
        #     self.scene.addItem(gp)
        #     point_group.addToGroup(gp)

        # Add QGraphicsView to main window
        mapWidgetLayout = QGridLayout()
        mapWidgetLayout.addWidget(self.view, 0, 0)
        self.setLayout(mapWidgetLayout)

        self.ap_list = []
        self.vehicle_position = None

        # Update map by redrawing whenever model changes
        #
        # Handle Scene event
        self.scene.selectionChanged.connect(self._compactedSignal)

    def _compactedSignal(self):
        '''
        Send custom signal that selection has changed only when new item is selected, ignore when selection is cleared to prevent other code from running multiple times
        '''
        selected_ap_list = self.scene.selectedItems()
        if not selected_ap_list: return #List isn't empty
        # Multiple can be selected, but we should only ever have one selected
        if len(selected_ap_list) == 1:
            self.selectionUpdate.emit(selected_ap_list[0])
        else:
            print("Error, multiple ap were selected in map which shouldn't be possible")

    def _readMapInfo(self, fp):
        with open(fp, 'r') as stream:
            map_info = yaml.safe_load(stream)
        return map_info

    def _readGraphFile(self, graph_fp, roundPixelPosition):
        """
        Converts geojson file to usable data format
        """
        graph_data = gpd.read_file(graph_fp)
        graph_data['adjusted_x'], graph_data['adjusted_y'] = self._convertCoords(graph_data['geometry'].x, graph_data['geometry'].y)

        points = graph_data.loc[(graph_data['geometry'] != None)][['id', 'adjusted_x', 'adjusted_y']]
        if roundPixelPosition:
            points = self._roundPixelPositions(points)

        lines = graph_data.loc[(graph_data['geometry'] == None)]

        df_for_starts = points.rename(columns={'id':'startid', 'adjusted_x':'start_x', 'adjusted_y':'start_y'})
        df_for_ends = points.rename(columns={'id':'endid', 'adjusted_x':'end_x', 'adjusted_y':'end_y'})
        lines = lines.merge(df_for_starts, on='startid')
        lines = lines.merge(df_for_ends, on='endid')
        lines  = lines[['id', 'startid', 'endid', 'start_x', 'start_y', 'end_x', 'end_y']]

        return points, lines

    def _roundPixelPositions(self, points, nearest=5):
        """
        Round coordinates to the nearest pixel value until the roads look good and straight
        """
        points['adjusted_x'] = nearest * round(points['adjusted_x']/nearest)
        points['adjusted_y'] = nearest * round(points['adjusted_y']/nearest)
        return points

    def clearActionPoints(self):
        for ap in self.ap_list:
            self.scene.removeItem(ap)
        self.ap_list = []

    def clearVehiclePosition(self):
        if self.vehicle_position is not None:
            self.scene.removeItem(self.vehicle_position)
            self.vehicle_position = None

    def addActionPoint(self, lat, long):
        '''
        Takes an action point dictionary and adds the action point to the map
        '''
        x, y = self._convertCoords(long, lat)
        ap = ActionPointGI(x, y, self.scene)
        self.ap_list.append(ap)
        self.scene.addItem(ap)

    def addActionPointList(self, ap_list):
        '''
        Add multiple action points
        '''
        for ap_dict in ap_list:
            self.addActionPointGI(ap_dict)

    def addVehiclePosition(self, lat, long):
        '''
        Adds the vehicle position to the map
        '''
        self.clearVehiclePosition()
        x, y = self._convertCoords(float(long), float(lat))
        vehicle = VehicleGI(x, y, self.scene)
        self.vehicle_position = vehicle
        self.scene.addItem(vehicle)

    def _convertCoords(self, x_vals, y_vals):
        converted_y = (y_vals - self.y_origin) / self.resolution * -1
        converted_x = (x_vals - self.x_origin) / self.resolution
        return converted_x, converted_y

    def reverseCoordConversion(self, x, y):
        # TODO Check this is working 100%
        converted_y = self.y_origin + (y * self.resolution) * -1
        converted_x = self.x_origin + (x * self.resolution)
        return converted_x, converted_y

    def zoom_in (self):
        if self.zoomLevel >= 3:
            return
        self.view.scale(2, 2)
        self.zoomLevel += 1

    def zoom_out (self):
        if self.zoomLevel <= -3:
            return
        self.view.scale(0.5, 0.5)
        self.zoomLevel -= 1

def createRoadLink(x1, y1, x2, y2):
    roadLink = QGraphicsLineItem(x1, y1, x2, y2)
    roadLink.setPen(roadLinkPen)
    return roadLink
