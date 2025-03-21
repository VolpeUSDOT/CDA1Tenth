import json
from bsmItem import BSMItem
from actionItem import ActionItem
from vehicleItem import VehicleItem
from cargoItem import CargoItem
from actionPointItem import ActionPoint

class MessageDecoder:
    def __init__(self):
        # Initialize any necessary variables here if needed
        pass
    
    def _decodeBSM(self, bsm_json):
        """
        This function takes a BSM stored in a json string and returns a BSM object
        
        Args:
            bsm_json (str): A json string containing the BSM data to decode
        
        Returns:
            bsm (BSM): The processed data after the conversion
        """
        bsm_dict = json.loads(bsm_json)
        # Extract the relevant data from the nested dictionary structure
        latitude = bsm_dict['BasicSafetyMessage']['coreData'].get('lat', None)
        longitude = bsm_dict['BasicSafetyMessage']['coreData'].get('long', None)
        speed = bsm_dict['BasicSafetyMessage']['coreData'].get('speed', None)
        heading = bsm_dict['BasicSafetyMessage']['coreData'].get('heading', None)
        '''add tempid,msgcount'''
        bsm = BSMItem(latitude, longitude, speed, heading)

        
        return bsm
    
    def _decodeMOM(self, mom_json):
        """
        This function takes a MOM stored in a json string and returns a MOM object

        Args:
            mom_json (str): A json string containing the MOM data to decode
        
        Returns:
            mom (ActionItem): The processed data after the conversion
        """
        mom_dict = json.loads(mom_json)
        # Extract the relevant data from the nested dictionary structure
        actionID = mom_dict['MobilityOperationMessage']['action_id']
        vehicle = mom_dict['MobilityOperationMessage']['cmv_id']
        cargo_name = mom_dict['MobilityOperationMessage']['cargo_name']
        cargo_id = mom_dict['MobilityOperationMessage']['cargo_id']
        destination_long = mom_dict['MobilityOperationMessage']['destination']['longitude']
        destination_lat = mom_dict['MobilityOperationMessage']['destination']['latitude']
        operation = mom_dict['MobilityOperationMessage']['operation']
        action_point = ActionPoint(actionID=int(actionID), name=operation, longitude=float(destination_long), latitude=float(destination_lat))
        vehicle_item = VehicleItem(veh_id=vehicle, name="TRUCK A")
        cargo_item = CargoItem(name=cargo_name, cargo_uuid=cargo_id)
        mom = ActionItem(vehicle=vehicle_item, cargo=cargo_item, actionPoint=action_point)
        return mom


    def decodeMessage(self, json_str):
        """
        This function decodes a message from V2X Hub and returns the appropriate result
        
        Args:
            json_str (str): A json string containing the data to decode
        
        Returns:
            data (dict): The processed data after the conversion
        """
        data = json.loads(json_str)
        # Check the type of message and decode accordingly
        if "BasicSafetyMessage" in data:
            decoded_data = self._decodeBSM(json_str)
        elif "MobilityOperationMessage" in data:
            decoded_data = self._decodeMOM(json_str)
        else:
            raise Exception("Unknown message type")
        return decoded_data


if __name__ == "__main__":
    # Example Usage:
    # Initialize the decoder
    decoder = MessageDecoder()

    # Sample BSM
    bsm_json = '{"BasicSafetyMessage":{"coreData":{"id":"fb31f855","msgCnt":"119","secMark":"3314","lat":"-12330619","long":"-2954826","elev":"0","accuracy":{"semiMajor":"255","semiMinor":"255","orientation":"65535"},"transmission":{"neutral":""},"speed":"8191","heading":"28800","angle":"127","accelSet":{"yaw":"0","long":"2001","lat":"2001","vert":"-127"},"brakes":{"wheelBrakes":"10000","traction":{"unavailable":""},"abs":{"unavailable":""},"scs":{"unavailable":""},"brakeBoost":{"unavailable":""},"auxBrakes":{"unavailable":""}},"size":{"width":"200","length":"500"}}}}'

    # decode the JSON array
    bsm = decoder.decodeBSM(bsm_json)

    # Print the processed result
    print(bsm)
