import json

class BSM:
    def __init__(self, latitude, longitude, speed, heading):
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.heading = heading

    def __str__(self):
        return ("Latitude: " + str(self.latitude) + "\n"
        + "Longitude: " + str(self.longitude) + "\n"
        + "Speed: " + self.speed + "\n"
        + "Heading: " + self.heading)

class BSMDecoder:
    def __init__(self):
        # Initialize any necessary variables here if needed
        pass
    
    def decodeBSM(self, bsm_json):
        """
        This function takes a BSM stored in a json string and returns a BSM object
        
        Args:
            bsm_json (str): A json string containing the BSM data to decode
        
        Returns:
            bsm (BSM): The processed data after the conversion
        """
        bsm_dict = json.loads(bsm_json)
        # Extract the relevant data from the nested dictionary structure
        latitude = float(bsm_dict['BasicSafetyMessage']['coreData'].get('lat', None)) * 1e-7
        longitude = float(bsm_dict['BasicSafetyMessage']['coreData'].get('long', None)) * 1e-7
        speed = bsm_dict['BasicSafetyMessage']['coreData'].get('speed', None)
        heading = bsm_dict['BasicSafetyMessage']['coreData'].get('heading', None)
        bsm = BSM(latitude, longitude, speed, heading)

        
        return bsm


if __name__ == "__main__":
    # Example Usage:
    # Initialize the decoder
    decoder = BSMDecoder()

    # Sample BSM
    bsm_json = '{"BasicSafetyMessage":{"coreData":{"id":"fb31f855","msgCnt":"119","secMark":"3314","lat":"-12330619","long":"-2954826","elev":"0","accuracy":{"semiMajor":"255","semiMinor":"255","orientation":"65535"},"transmission":{"neutral":""},"speed":"8191","heading":"28800","angle":"127","accelSet":{"yaw":"0","long":"2001","lat":"2001","vert":"-127"},"brakes":{"wheelBrakes":"10000","traction":{"unavailable":""},"abs":{"unavailable":""},"scs":{"unavailable":""},"brakeBoost":{"unavailable":""},"auxBrakes":{"unavailable":""}},"size":{"width":"200","length":"500"}}}}'

    # decode the JSON array
    bsm = decoder.decodeBSM(bsm_json)

    # Print the processed result
    print(bsm)
