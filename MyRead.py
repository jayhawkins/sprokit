#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import serial
import string
import threading
import json
import datetime
from StringIO import StringIO

from websocket_server import WebsocketServer

continue_reading = True

##port='/dev/ttyAMA0',
##port='/dev/ttyS0',
# ser = serial.Serial(
#         port='/dev/ttyS0',
# 	    baudrate = 115200,
#         parity=serial.PARITY_NONE,
#         stopbits=serial.STOPBITS_ONE,
#         bytesize=serial.EIGHTBITS,
#         timeout=1
# )

# Called for every client connecting (after handshake)
def new_client(client, server):
        print("New client connected and was given id %d" % client['id'])
        # server.send_message_to_all("Hey all, a new client has joined us")


# Called for every client disconnecting
def client_left(client, server):
        print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
        if len(message) > 200:
                message = message[:200]+'..'
        print("Client(%d) said: %s" % (client['id'], message))


# Called for every client connecting (after handshake)
def send_message_client(client, server):
        print("client data %d", client)
        msg = "id sent to client %d" % client['id']
        print(msg)
        server.send_message_to_all(msg)


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()


if __name__ == "__main__":

    ser = serial.Serial(
            port='/dev/ttyS0',
    	    baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
    )

    PORT=9001
    server = WebsocketServer(PORT)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.send_message_to_all(send_message_client)
    wst = threading.Thread(target=server.run_forever)
    wst.daemon = True
    wst.start()


    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)

    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()

    # Welcome message
    #print "Welcome to the MFRC522 data read example"
    print "\nQwiqfire Sensor Suite is running\n"

    #cmd = "AT\r\n"
    # Get machine serial number
    cmd = 'Q100\r'
    cmd = ser.write(bytes(cmd))
    #ser.write(cmd.encode('ascii'))
    Q100_response = ser.readline()
    print 'Machine Serial Number is: ' + Q100_response + '\n'
    # print list(response)

    # Get control software version
    cmd = 'Q101\r'
    cmd = ser.write(bytes(cmd))
    Q101_response = ser.readline()
    print 'Control software version is: ' + Q101_response + '\n'

    # Get machine model number
    cmd = 'Q102\r'
    cmd = ser.write(bytes(cmd))
    Q102_response = ser.readline()
    print 'Machine model number is: ' + Q102_response + '\n'

    # print "Press Ctrl-C to stop.\n"

    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:

        # Scan for cards
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print "Card detected"
            server.send_message_to_all('{"message": "scan_complete"}')
        else:
        	response = ser.readline()

    	if response != '':
    	    print 'Response is: ' + response + '\r\n'


        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            # print "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])

            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == MIFAREReader.MI_OK:
                empID = MIFAREReader.MFRC522_Read(8)
                print empID

                # Get mode
                cmd = 'Q104\r'
                cmd = ser.write(bytes(cmd))
                Q104_response = ser.readline()
                print 'Mode is: ' + Q104_response + '\n'

                # Get tool number in use
                cmd = 'Q201\r'
                cmd = ser.write(bytes(cmd))
                Q201_response = ser.readline()
                print 'Tool number in use: ' + Q201_response + '\n'

                # Get power on time total
                cmd = 'Q300\r'
                cmd = ser.write(bytes(cmd))
                Q300_response = ser.readline()
                print 'Power-On time (total): ' + Q300_response + '\n'

                # Get motion time total
                cmd = 'Q301\r'
                cmd = ser.write(bytes(cmd))
                Q301_response = ser.readline()
                print 'Motion time (total): ' + Q301_response + '\n'

                # Get last cycle time
                cmd = 'Q303\r'
                cmd = ser.write(bytes(cmd))
                Q303_response = ser.readline()
                print 'Last Cycle Time was: ' + Q303_response + '\n'

                # Get previous cycle time
                cmd = 'Q304\r'
                cmd = ser.write(bytes(cmd))
                Q304_response = ser.readline()
                print 'Previous Cycle Time was: ' + Q304_response + '\n'

                # Get M30 parts counter #1
                #ser.write('Q402' + '\r\n')
                ser.write('Q402' + '\r')
                Q402_response = ser.readline()
                print 'Parts Counter \#1 response is: ' + Q402_response + '\n\n'
                #ser.write(text.encode('ascii') + '\r\n')

                # Get M30 parts counter #2
                ser.write('Q403' + '\r')
                Q403_response = ser.readline()
                print 'Parts Counter \#2 response is: ' + Q403_response + '\r\n'

                createdAt = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
                status = "Active"

                text = "".join(chr(x) for x in empID)
                print text

                # Create JSON object for messaging and database post
                io = StringIO()
                jsonResponse = '{"userID": "' + str(text) + '", "Q100": "' + str(Q100_response) + '", "Q101": "' + str(Q101_response) + '", "Q102": "' +  str(Q102_response) + '", "Q104": "' + str(Q104_response) + '", "Q201": "' + str(Q201_response) + '", "Q300": "' + str(Q300_response) + '", "Q301": "' + str(Q301_response) + '", "Q303": "' + str(Q303_response) + '", "Q304": "' + str(Q304_response) + '", "Q402": "' + str(Q402_response) + '", "Q403": "' + str(Q403_response) + '", "createdAt": "' + str(createdAt) + '", "status": "' + str(status) + '"}'
                # json_data = json.dumps(jsonResponse, io)

                server.send_message_to_all(jsonResponse)

                MIFAREReader.MFRC522_StopCrypto1()
            else:
                print "Authentication error"
