from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QGridLayout, QGraphicsView
from MapWidget.vgraphicsscene import ViewGraphicsScene
from MapWidget.mapitems import createRoadLink, ActionPoint
import geopandas as gpd
import yaml

pgm_map = './MapUI/PortDrayageData/garage.pgm'
map_info = './MapUI/PortDrayageData/garage.yaml'
graph = './MapUI/PortDrayageData/garage_graph_port_drayage_v2.geojson'

# Subclass QMainWindow to customize your application's main window
class MapWidget(QWidget):
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
        points, lines = self._readGraphFile(graph_fp, roundPixelPosition = True)

        # Add all road segments to scene
        road_group = self.scene.createItemGroup([])
        for _, line in lines.iterrows():
            roadLink = createRoadLink(line['start_x'], line['start_y'], line['end_x'], line['end_y'])
            self.scene.addItem(roadLink)
            road_group.addToGroup(roadLink)

        # Add QGraphicsView to main window
        mapWidgetLayout = QGridLayout()
        mapWidgetLayout.addWidget(self.view, 0, 0)

        self.setLayout(mapWidgetLayout)

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

    def addActionPoint(self, ap_dict):
        '''
        Takes an action point dictionary and adds the action point to the map
        '''
        ap_dict['destination_long'], ap_dict['destination_lat'] = self._convertCoords(ap_dict['destination_long'], ap_dict['destination_lat'])
        ap = ActionPoint(ap_dict, self.scene)
        self.scene.addItem(ap)

    def addActionPointList(self, ap_list):
        '''
        Add multiple action points
        '''
        for ap_dict in ap_list:
            self.addActionPoint(ap_dict)

    # def _pullLocationActions(self, schema):
    #     '''
    #     Pull data from SQL and convert coords to pixel coords
    #     '''
    #     db = Database(schema)
    #     actionData = db.getData()
    #     actionData['destination_long'], actionData['destination_lat'] = self._convertCoords(actionData['destination_long'], actionData['destination_lat'])
    #     return(actionData)

    def _convertCoords(self, x_vals, y_vals):
        converted_y = (y_vals - self.y_origin) / self.resolution * -1
        converted_x = (x_vals - self.x_origin) / self.resolution
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
