#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO
import sys


repeat = 5
sleep_sec = 1

if len(sys.argv) > 1:
    repeat = int(sys.argv[1])

if len(sys.argv) > 2:
    sleep_sec = int(sys.argv[2])

def reading():
    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BOARD)
    TRIG = 12
    ECHO = 16
     
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.3)
      
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
      signaloff = time.time()
      
    while GPIO.input(ECHO) == 1:
      signalon = time.time()

    timepassed = signalon - signaloff
    distance = timepassed * 17000
    return distance
    GPIO.cleanup()
        
for i in range(repeat):
  msg = "超音波センサー:{0} cm".format(reading())
  time.sleep(sleep_sec)
  print(msg)
