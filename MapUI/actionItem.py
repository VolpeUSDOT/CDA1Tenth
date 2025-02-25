from actionPointItem import ActionPoint
from cargoItem import CargoItem
from vehicleItem import VehicleItem
import datetime as dt
import json

class ActionItem():
    '''
    Class to store data for individual items in model
    This allows for in place data modification, and display functions to be attached to the data item
    '''

    def __init__(self, vehicle=VehicleItem(), cargo=CargoItem(), actionPoint=ActionPoint()):
        self.vehicle = vehicle
        self.cargo = cargo
        self.areaData = actionPoint.actionItemDataFilter()
        self.actionID = actionPoint.actionID
        self.next_action = actionPoint.next_action
        self.prev_action = actionPoint.prev_action

        # These are used for display in the UI and are not part of the JSON Message
        self.status = "Pending"
        self.timeRequested = dt.datetime.now()
        self.timeCompleted = None

    def completedActionDisplay(self):
        text = 'Vehicle: {} \t\t Cargo: {} \t\t ActionID: {} \t Requested Time: {} \t Completed Time: {}'.format(self.vehicle.veh_id, self.cargo.cargo_uuid, self.actionID, self.timeRequested, self.timeCompleted)
        return text

    def convertToJSON(self):
        json_dict = dict()
        json_dict["MobilityOperationMessage"] = {"action_id": self.next_action,
                     "operation": self.areaData.name,
                     "cmv_id": self.vehicle.veh_id,
                     "cargo_name": self.cargo.name,
                     "cargo_id": self.cargo.cargo_uuid,
                     "destination": 
                        {
                            "latitude": self.areaData.latitude,
                            "longitude": self.areaData.longitude
                        }
                     }
        json_str = json.dumps(json_dict)
        print(json_str)
        return json_str
