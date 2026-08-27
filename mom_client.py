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
    
def main():
    with connect("ws://localhost:8765") as websocket:
        while True:
            op = input("Which operation do you want to emulate? ")

            mom = {'MobilityOperationMessage':{
                'action_id': 2,
                'cmv_id': 'Billys_truck',
                'cargo_name': 'computers',
                'cargo_id': 34506,
                'destination': {'longitude': 0, 'latitude': 0},
                'operation': op

                }
            }

            try:
                websocket.send(json.dumps(mom))
            except:
                websocket = connect("ws://localhost:8765")
            time.sleep(0.1)  # Wait 0.1 seconds (1/10th of a second)
            print(mom)

if __name__ == "__main__":
    main()


