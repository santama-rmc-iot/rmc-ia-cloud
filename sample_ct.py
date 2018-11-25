# -*- coding: utf-8 -*-
import Adafruit_ADS1x15
import time
import sys

repeat = 5
sleep_sec = 1

if len(sys.argv) > 1:
    repeat = int(sys.argv[1])

if len(sys.argv) > 2:
    sleep_sec = int(sys.argv[2])

def reading():
    CHANNEL = 0
    GAIN = 16

    adc = Adafruit_ADS1x15.ADS1115()
    return adc.read_adc(CHANNEL, gain=GAIN) * (0.256 / 32768)

for i in range(repeat):
    msg = "電流センサー: {0} V".format(reading())
    print(msg)
    time.sleep(sleep_sec)