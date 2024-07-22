#!/usr/bin/env python3

# Written by the USDOT Volpe National Transportation Systems Center
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import os, time, sys
from ruamel.yaml import YAML
from threading import Thread
import asn1tools

from Networking.networking import UDP_NET

# initialize errors
error = False

# test scripts should always print
printData = True

# Import Configs
script_dir = os.path.dirname(__file__)
fpath = 'config/params.yaml'
file_path = os.path.join(script_dir, fpath)
try:
    y = YAML(typ='safe')
    with open(file_path,'r') as f:
        params = y.load(f)
    parseLANPacket = params['LAN_DECODE']
    parseVANETPacket = params['VANET_DECODE']
    radioApps = params['RADIO_APPS']
    printData = params['print_data']
    loopTime = params['loop_time']
    logLevel = params['logging_level']
except Exception as e:
    error = True
    print("Unable to import yaml configs")
    raise e

netTestType = sys.argv[1]
if sys.argv[1] == "vanet":
    netTestType="VANET"
elif sys.argv[1] =="lan":
    netTestType="LAN"
else:
    print("invalid network test type......exiting")
    error = True

SPECIFICATION = '''
MyUserName DEFINITIONS ::= BEGIN
    Message ::= SEQUENCE {
        number      INTEGER,
        text        UTF8String
    }
END
'''

#Added Specification and compile_spring for Signal using asn1tools
SIG_SPEC = '''
Signal DEFINITIONS ::= BEGIN
    Signal ::= SEQUENCE {
        color       UTF8String
    }
END
'''
Signal = asn1tools.compile_string(SIG_SPEC,'uper')
#added messageNum, sigcolor, and duration (Yellow = 2, Green and Red = 5)
messageNum = 0   
sigcolor = ['Green', 'Yellow', 'Red']
sigselect = 0
loadingdots = '.\r'
prevpkt = ' '
cycles = [50, 20, 50]

myUName = asn1tools.compile_string(SPECIFICATION,'uper')
uName = str(os.getlogin())
msg = {'number': 22, 'text': uName}
encoded = myUName.encode('Message', msg)

# instantiate networks
# LAN
if netTestType=="LAN":
    try:
        lan = UDP_NET(CONFIG_FILE='LAN_params.yaml')
    except:
        error = True
    try:
        lan.start_connection()
    except:
        if printData:
            print("Not connected to a LAN interface")
# VANET
if netTestType=="VANET":
    try:
        vanet = UDP_NET(CONFIG_FILE='VANET_params.yaml', print_data=True)
    except:
        error = True
    try:
        vanet.start_connection()
    except:
        print(vanet.error)
        print("Not connected to a VANET interface")

def sendVANET(vPacket):
    global vanet
    vanet.send_data(vPacket)

def sendLAN(vPacket):
    global lan
    lan.send_data(vPacket)

def sendPacketsOnLoop_thread():
    global error
    global myUName
    global uName
    global encoded
    #added
    global Signal
    global sigselect
    global loadingdots
    global messageNum
    global sig
    global enc_sig
    
    while not error:
        sig = {'color': sigcolor[sigselect % 3]}
        enc_sig = Signal.encode('Signal', sig)
        
        if messageNum == cycles[sigselect % 3]:
	        messageNum = 0
	        sigselect += 1
	        loadingdots = '.\r'
	        
        if netTestType =="LAN":
            lan.send_data(encoded)
        elif netTestType =="VANET":
            try:
                print(loadingdots,end='')
                #changed to send enc_sig instead of encoded
                vanet.send_data(enc_sig)
                loadingdots += '.'
                messageNum += 1 
            except:
                print("tried and failed")
                pass  
           
        #reduced sleep time
        time.sleep(0.1)
        
def listening_thread():
    global error
    global myUName
    global uName
    global encoded
    #added decoded to allow printing
    global decoded
    #added Signal, enc_sig
    global Signal
    global prevpkt
    
    while not error and not vanet.error:

        try:
            if netTestType =="VANET":
                pkt = vanet.recv_packets()
            elif netTestType =="LAN":
                pkt = lan.recv_packets()
            if pkt:          
                if prevpkt != pkt[0]:
                    #changed to show enc_sig instead of encoded, added print of decoded traffic signal color
                    print(f"\nrecvd_sig: {pkt[0]}\tog_encoded: {enc_sig}") 
                    print(f"loop_test_result: {pkt[0]==enc_sig}")
                    decoded = Signal.decode('Signal',pkt[0])
                    print(f"Traffic Signal: {decoded['color']}")
                prevpkt=pkt[0]
        except:
            if printData:
                print("Waiting to configure network")
            time.sleep(0.25)
        time.sleep(loopTime)

    error = True

def main():

    global error

    # set up threads
    threads = []
    
    listening_mt = Thread(target= listening_thread)
    sending_mt = Thread(target= sendPacketsOnLoop_thread)
    threads.append(listening_mt)
    threads.append(sending_mt)

    for thread in threads:
        thread.daemon=True
        thread.start()
        time.sleep(0.2)

    try:
        while not error:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard Interrupt Occurred")
    finally:
        error = True
       
# code starts here
if __name__ == '__main__':

    # print to terminal that C1T2X radio is starting up
    print("----------------------------------------------------\nSTARTING C1T2X RADIO\n----------------------------------------------------")
    
    main()
