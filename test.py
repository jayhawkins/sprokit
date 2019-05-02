#!/usr/bin/env python

import RPi.GPIO as GPIO
import sys
sys.path.append('/home/pi/MFRC522-python')
from MFRC522 import MFRC522

reader = MFRC522()

print("Hold a tag near the reader")

try:
    #id, text = reader.Read_MFRC522()
    text = reader.Read_MRFC522()
    #print(id)
    print(text)

finally:
    GPIO.cleanup()
