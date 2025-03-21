class BSMItem:
    def __init__(self, latitude, longitude, speed, heading, msgCnt, tempid):
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.heading = heading
        self.msgCnt = msgCnt
        self.tempid = tempid

    def __str__(self):
        return ("Latitude: " + self.latitude + "\n"
        + "Longitude: " + self.longitude + "\n"
        + "Speed: " + self.speed + "\n"
        + "Heading: " + self.heading)