from PySide6.QtCore import QSize, Signal, Qt, QPointF, QLineF, QRectF
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QGraphicsView,
    QPushButton,
    QGraphicsLineItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPen, QBrush, QPixmap, QColor
import geopandas as gpd
import yaml
from MapWidget.vgraphicsscene import ViewGraphicsScene
from MapWidget.mapitems import ActionPointGI, VehicleGI

# Constants
png_map = '../MapUI/PortDrayageData/pdroadmap.png'
pgm_map = '../MapUI/PortDrayageData/garage.pgm'
map_info = '../MapUI/PortDrayageData/garage.yaml'
graph = '../MapUI/PortDrayageData/garage_center_line.geojson'
cdalogo = '../Resources/Cooperative Driving Automation 1Tenth_White.png'
volpelogo = '../Resources/volpewh.png'
roadLinkPen = QPen(Qt.yellow, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
DEGREE_TO_TENTH_MICRO = 10000000
MAX_VEHICLES = 50  # Maximum number of vehicle trails to display

class MapWidget(QWidget):
    selectionUpdate = Signal(ActionPointGI)

    def __init__(self, acceptHoverEvents, png_map_fp=png_map, pgm_map_fp=pgm_map, map_info_fp=map_info,
                 graph_fp=graph, volpe_fp=volpelogo, cda_fp=cdalogo):
        super().__init__()
        self.setMinimumSize(QSize(550, 400))
        self.zoomLevel = 0
        self.graphicsVisible = True  # State to track overall graphics visibility

        # State variables for individual graphical elements
        self.show_bg_map = bool(png_map_fp)  # Set to False if file path is None or ""
        self.show_logos = bool(volpe_fp and cda_fp) # Set to False if file path is None or ""
        self.show_vehicle_trail = True  # Vehicle trail visibility
        if (not self.show_bg_map):
            self.show_road_links = True # Default to true if no bg map
        else:
            self.show_road_links = False

        self.opacityRangeTop = 0.3  # 2nd vehicle in trail opacity (goes to 0 from here)
        self.opacityTruckValue = self.opacityRangeTop  # Initial trail visibility
        self.isAddActionPoint = False  # State to create a new action point
        self.acceptHoverEvents = acceptHoverEvents

        # Create QGraphicsScene and QGraphicsView
        self.scene = ViewGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.scale(2.5, 2.5)  # Scale starting view

        # Used when create a new action pointAdd commentMore actions
        self.isAddActionPoint = False
        self.scene.mousePressEvent = self._mouse_press_event
        self.view = QGraphicsView(self.scene)

        # Scale starting view
        self.view.scale(2.5, 2.5)

        # Define the viewable portion of the scene
        scene_rect = QRectF(34, -123, 100, 100)
        self.scene.setSceneRect(scene_rect)

        # Set background color for the scene
        background_color = QColor(23, 30, 93)  # Dark Blue
        self.scene.setBackgroundBrush(QBrush(background_color))

        # Load map image as the background and add it to the scene (if valid)
        if png_map_fp:
            scale_factor = 0.23
            x_offset = 9
            y_offset = -139.5
            self.bg_image_item = self.load_bg_image(png_map_fp, scale_factor, x_offset, y_offset)
            self.scene.addItem(self.bg_image_item)
        else:
            self.bg_image_item = None  # No background image available

        # Load logos and add them to the scene (if valid)
        if volpe_fp and cda_fp:
            scale_factor = 0.028
            x_offset = 86
            y_offset = -103
            self.volpelogo = self.load_bg_image(volpe_fp, scale_factor, x_offset, y_offset)
            self.scene.addItem(self.volpelogo)

            scale_factor = 0.1
            x_offset = 106
            y_offset = -136
            self.cdalogo = self.load_bg_image(cda_fp, scale_factor, x_offset, y_offset)
            self.scene.addItem(self.cdalogo)
        else:
            self.volpelogo = None
            self.cdalogo = None

        # Process graph data and road links
        mapInfo = self._readMapInfo(map_info_fp)
        self.x_origin = mapInfo["origin"][0]
        self.y_origin = mapInfo["origin"][1]
        self.resolution = mapInfo["resolution"]
        self.points, self.lines = self._readGraphFile(graph_fp, roundPixelPosition=True)

        # Create a group for road links
        self.road_group = self.scene.createItemGroup([])
        for _, line in self.lines.iterrows():
            roadLink = createRoadLink(
                line["start_x"], line["start_y"], line["end_x"], line["end_y"]
            )
            self.scene.addItem(roadLink)
            self.road_group.addToGroup(roadLink)
        self.road_group.setVisible(self.show_road_links)

        # Initialize lists for action points and vehicle positions
        self.ap_list = []
        self.vehicle_position = []

        # Create individual toggle buttons for graphics manipulation
        self.map_button = QPushButton("Toggle Map")
        self.map_button.setCheckable(True)
        self.map_button.setChecked(self.show_bg_map)
        self.map_button.setEnabled(self.show_bg_map)  # Disable button if no map file
        self.map_button.clicked.connect(self.toggle_bg_map)
        self.update_button_style(self.map_button, self.show_bg_map)

        self.logos_button = QPushButton("Toggle Logos")
        self.logos_button.setCheckable(True)
        self.logos_button.setChecked(self.show_logos)
        self.logos_button.setEnabled(self.show_logos)  # Disable button if logos are invalid
        self.logos_button.clicked.connect(self.toggle_logos)
        self.update_button_style(self.logos_button, self.show_logos)
        

        self.trail_button = QPushButton("Toggle Trail")
        self.trail_button.setCheckable(True)
        self.trail_button.setChecked(self.show_vehicle_trail)
        self.trail_button.clicked.connect(self.toggle_vehicle_trail)
        self.update_button_style(self.trail_button, self.show_vehicle_trail)

        self.road_button = QPushButton("Toggle Roads")
        self.road_button.setCheckable(True)
        self.road_button.setChecked(self.show_road_links)
        self.road_button.clicked.connect(self.toggle_road_links)
        self.update_button_style(self.road_button, self.show_road_links)

        # Add QGraphicsView and toggle buttons to the layout
        mapWidgetLayout = QGridLayout()
        mapWidgetLayout.addWidget(self.view, 0, 0, 1, 4)  # QGraphicsView spans 4 columns
        mapWidgetLayout.addWidget(self.map_button, 1, 0)
        mapWidgetLayout.addWidget(self.logos_button, 1, 1)
        mapWidgetLayout.addWidget(self.trail_button, 1, 2)
        mapWidgetLayout.addWidget(self.road_button, 1, 3)
        self.setLayout(mapWidgetLayout)

    # Button toggle methods
    def toggle_bg_map(self):
        self.show_bg_map = not self.show_bg_map
        self.bg_image_item.setVisible(self.show_bg_map)
        self.update_button_style(self.map_button, self.show_bg_map)

    def toggle_logos(self):
        self.show_logos = not self.show_logos
        self.volpelogo.setVisible(self.show_logos)
        self.cdalogo.setVisible(self.show_logos)
        self.update_button_style(self.logos_button, self.show_logos)

    def toggle_vehicle_trail(self):
        self.show_vehicle_trail = not self.show_vehicle_trail
        if self.show_vehicle_trail:
            self.opacityTruckValue = self.opacityRangeTop
        else:
            self.clearVehiclePosition()
            self.opacityTruckValue = 0
        self.update_button_style(self.trail_button, self.show_vehicle_trail)

    def toggle_road_links(self):
        self.show_road_links = not self.show_road_links
        self.road_group.setVisible(self.show_road_links)
        self.update_button_style(self.road_button, self.show_road_links)

    def update_button_style(self, button, is_checked):
        """
        Update the button style based on its state (pressed or unpressed).
        Pressed state uses light green, unpressed state uses light coral.
        """
        if is_checked:
            button.setStyleSheet("background-color: lightgreen;")
        else:
            button.setStyleSheet("background-color: lightcoral;")

    def load_bg_image(self, image_path, sf, xoff, yoff):
        pixmap = QPixmap(image_path)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setScale(sf)
        pixmap_item.setPos(xoff, yoff)
        return pixmap_item

    def _compactedSignal(self):
        """
        Send custom signal that selection has changed only when new item is selected, ignore when selection is cleared to prevent other code from running multiple times
        """
        selected_ap_list = self.scene.selectedItems()
        if not selected_ap_list:
            return  # List isn't empty
        # Multiple can be selected, but we should only ever have one selected
        if len(selected_ap_list) == 1:
            self.selectionUpdate.emit(selected_ap_list[0])
        else:
            print("Error, multiple ap were selected in map which shouldn't be possible")

    def clearActionPoints(self):
        for ap in self.ap_list:
            self.scene.removeItem(ap)
        self.ap_list = []

    def clearVehiclePosition(self):
        '''Removes all vehicles from scene/empties array, not called when using trail method'''
        for vehicle in self.vehicle_position:
            self.scene.removeItem(vehicle)
        self.vehicle_position = []

    def addActionPoint(self, lat, long, description="No Description"):
        """
        Takes an action point dictionary and adds the action point to the map
        """
        if long is None or lat is None:
            return
        x, y = self._convertCoords(long, lat)
        ap = ActionPointGI(x, y, self.acceptHoverEvents, description, self.scene)
        self.ap_list.append(ap)
        self.scene.addItem(ap)

    def addActionPointList(self, ap_list):
        """
        Add multiple action points
        """
        for ap_dict in ap_list:
            self.addActionPointGI(ap_dict)

    def addVehiclePosition(self, lat, long):
        """
        Adds a new vehicle to the map and manages the vehicle_position list with opacity adjustments.
        If self.opacityTruckValue == 0, only the latest vehicle is kept visible (no trail).
        """
        # Convert coordinates
        x, y = self._convertCoords(float(long) / DEGREE_TO_TENTH_MICRO, float(lat) / DEGREE_TO_TENTH_MICRO)
        
        # Create a new vehicle
        vehicle = VehicleGI(x, y, f'BSM - Lat: {lat / DEGREE_TO_TENTH_MICRO}, Long: {long / DEGREE_TO_TENTH_MICRO}', self.scene)
        self.scene.addItem(vehicle)

        # Check opacity behavior: keep only current vehicle if opacityTruckValue is 0
        if self.opacityTruckValue == 0:
            # Remove all previous vehicles from the scene
            for v in self.vehicle_position:
                self.scene.removeItem(v)
            # Clear the vehicle list
            self.vehicle_position = []
            # Add only the current vehicle
            self.vehicle_position.append(vehicle)
            # Set full opacity for the current vehicle
            vehicle.setOpacity(1.0)
            return 

        # Insert the new vehicle at the beginning of the list
        self.vehicle_position.insert(0, vehicle)

        # Ensure the list does not exceed MAX_VEHICLES
        if len(self.vehicle_position) > MAX_VEHICLES:
            # Remove the oldest vehicle from the scene and the list
            removed_vehicle = self.vehicle_position.pop()  # Remove last element
            self.scene.removeItem(removed_vehicle)

        # Update opacities for all vehicles in the list
        #total = len(self.vehicle_position)
        for index, v in enumerate(self.vehicle_position):
            if index == 0:
                # Set latest vehicle position to 100% opacity
                v.setOpacity(1.0)
            else:
                # Interpolate remaining positions from opacityTruckValue down to 0.01
                step = (self.opacityTruckValue - 0.01) / (MAX_VEHICLES - 1)
                opacity = self.opacityTruckValue - step * (index - 1)
                v.setOpacity(opacity)

    def _readMapInfo(self, fp):
        with open(fp, "r") as stream:
            map_info = yaml.safe_load(stream)
        return map_info

    def _readGraphFile(self, graph_fp, roundPixelPosition):
        graph_data = gpd.read_file(graph_fp)
        graph_data["adjusted_x"], graph_data["adjusted_y"] = self._convertCoords(
            graph_data["geometry"].x, graph_data["geometry"].y
        )
        points = graph_data.loc[(graph_data["geometry"] != None)][
            ["id", "adjusted_x", "adjusted_y"]
        ]
        if roundPixelPosition:
            points = self._roundPixelPositions(points)
        lines = graph_data.loc[(graph_data["geometry"] == None)]
        df_for_starts = points.rename(
            columns={"id": "startid", "adjusted_x": "start_x", "adjusted_y": "start_y"}
        )
        df_for_ends = points.rename(
            columns={"id": "endid", "adjusted_x": "end_x", "adjusted_y": "end_y"}
        )
        lines = lines.merge(df_for_starts, on="startid")
        lines = lines.merge(df_for_ends, on="endid")
        lines = lines[
            ["id", "startid", "endid", "start_x", "start_y", "end_x", "end_y"]
        ]
        return points, lines

    def _convertCoords(self, x_vals, y_vals):
        converted_y = (y_vals - self.y_origin) / self.resolution * -1
        converted_x = (x_vals - self.x_origin) / self.resolution
        return converted_x, converted_y

    def _roundPixelPositions(self, points, nearest=5):
        points["adjusted_x"] = nearest * round(points["adjusted_x"] / nearest)
        points["adjusted_y"] = nearest * round(points["adjusted_y"] / nearest)
        return points
    
    def _convertCoords(self, x_vals, y_vals):
            converted_y = (y_vals - self.y_origin) / self.resolution * -1
            converted_x = (x_vals - self.x_origin) / self.resolution
            return converted_x, converted_y
    
    def reverseCoordConversion(self, x, y):
        # TODO Check this is working 100%
        converted_y = self.y_origin + (y * self.resolution) * -1
        converted_x = self.x_origin + (x * self.resolution)
        return converted_x, converted_y
    
    def zoom_in(self):
        if self.zoomLevel >= 6:
            return
        self.view.scale(1.25, 1.25)
        self.zoomLevel += 1

    def zoom_out(self):
        if self.zoomLevel <= -6:
            return
        self.view.scale(0.8, 0.8)
        self.zoomLevel -= 1

    def _mouse_press_event(self, event):
        click_pos = event.scenePos()
        lines = self._get_lines()
        if not lines:
            return
        nearest_point = self._get_nearest_point_on_lines(self._get_lines(), click_pos)
        self.clickedNewPoint = nearest_point
        existing_points = self._get_points()
        if self.isAddActionPoint:
            # Remove added new point when user tries to create new point
            for point in existing_points:
                self.scene.removeItem(point)
                # Reset existing points
                existing_points = []
        if len(existing_points) == 0:
            # Assuming when map is used for creating an action point, there is no point item on the map
            self.isAddActionPoint = True
            self._add_clicked_point_to_map()
        # Call the base class mousePressEvent to ensure default behavior
        super(ViewGraphicsScene, self.scene).mousePressEvent(event)

    def _add_clicked_point_to_map(self, description="No Description"):
        if self.clickedNewPoint is None:
            return
        newActionPoint = ActionPointGI(
            self.clickedNewPoint.x(), self.clickedNewPoint.y(), self.acceptHoverEvents, description, self.scene
        )
        self.scene.addItem(newActionPoint)

    def _get_nearest_point_on_lines(self, lines, click_pos):
        nearest_line = min(
            lines, key=lambda line: self._distance_to_line(line, click_pos)
        )
        nearest_point = self._get_nearest_point_on_line(nearest_line, click_pos)
        return nearest_point
    
    def _get_nearest_point_on_line(self, line, click_pos):
        """Finds the closest point on a given line segment to the click position."""
        line_f = line.line()
        p1, p2 = line_f.p1(), line_f.p2()  # Line endpoints
        # Vector math to compute closest point
        v_line = p2 - p1
        v_click = click_pos - p1
        # Projection formula
        t = (v_click.x() * v_line.x() + v_click.y() * v_line.y()) / (
            v_line.x() ** 2 + v_line.y() ** 2
        )
        t = max(0, min(1, t))  # Clamp t to stay within the segment
        # Compute the closest point coordinates
        nearest_x = p1.x() + t * v_line.x()
        nearest_y = p1.y() + t * v_line.y()
        return QPointF(nearest_x, nearest_y)
    
    def _distance_to_line(self, line, point):
        """Calculates the perpendicular distance from a point to a line segment."""
        nearest_point = self._get_nearest_point_on_line(line, point)
        return (nearest_point - point).manhattanLength()  # Approximate distance
    
    def _get_lines(self):
        return [
            item for item in self.scene.items() if isinstance(item, QGraphicsLineItem)
        ]
    
    def _get_points(self):
        return [item for item in self.scene.items() if isinstance(item, ActionPointGI)]

def createRoadLink(x1, y1, x2, y2):
    roadLink = QGraphicsLineItem(x1, y1, x2, y2)
    roadLink.setPen(roadLinkPen)
    #roadLink.setVisible(False)  # Initially hidden to match default toggle state
    return roadLink