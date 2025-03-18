#!/usr/bin/env python

"""Client using the threading API."""

from websockets.sync.client import connect
import asyncio
import websockets
import json
from asn_j2735 import J2735_201603_combined
import sys, os
import datetime
import time

from binascii import hexlify

# A set to store all connected WebSocket clients

bsm = {'messageId': 20, 'value': {'BasicSafetyMessage': {'coreData': {'msgCnt': 18, 'id': '12345', 'secMark': 28782, 'lat': -20000000, 'long': -20000000, 'elev': 394, 'accuracy': {'semiMajor': 255, 'semiMinor': 255, 'orientation': 65535}, 'transmission': 'forwardGears', 'speed': 234, 'heading': 28800, 'angle': 127, 'accelSet': {'long': 2001, 'lat': 2001, 'vert': -127, 'yaw': 32767}, 'brakes': {'wheelBrakes': (0, 5), 'traction': 'unavailable', 'abs': 'unavailable', 'scs': 'unavailable', 'brakeBoost': 'unavailable', 'auxBrakes': 'unavailable'}, 'size': {'width': 0, 'length': 0}}}}}

def add_asn1_path():
    asn1 = os.path.abspath('..') + "/asn_j2735"
    sys.path.append(asn1)

def getMsgCount(msgCount):
    msgCount += 1
    if (msgCount == 128):
        msgCount = 1
    return int(msgCount)

def getSecMark():
    time = str(datetime.datetime.now())
    time = float(time.split(':')[2])
    secMark = str((time*1000)%60000).split('.')[0]
    return int(secMark)

def encode(bsmDict):
    msgFrame = J2735_201603_combined.DSRC.MessageFrame
    msgFrame.set_val(bsmDict)
    msgFrameUper = msgFrame.to_uper()
    encodedBSM = hexlify(msgFrameUper)
    return encodedBSM

encoded_bsm = None  # Initialize the global variable
    
def main():
    with connect("ws://localhost:8765") as websocket:
        input("Garbage: ")
        while True:
            msgCount = 0

            msgCount = getMsgCount(msgCount)
            bsm['value']['BasicSafetyMessage']['coreData']['msgCnt']  = msgCount
            bsm['value']['BasicSafetyMessage']['coreData']['secMark'] = getSecMark()
            bsm['value']['BasicSafetyMessage']['coreData']['lat'] += 5000000
            if bsm['value']['BasicSafetyMessage']['coreData']['lat'] > 0:
                bsm['value']['BasicSafetyMessage']['coreData']['lat'] = -50000000
            try:
                websocket.send(json.dumps(bsm['value']))
            except:
                websocket = connect("ws://localhost:8765")
            time.sleep(0.1)  # Wait 0.1 seconds (1/10th of a second)
            print(bsm)

if __name__ == "__main__":
    main()


