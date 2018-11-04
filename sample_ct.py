# -*- coding: utf-8 -*-
import Adafruit_ADS1x15
import time

def reading():
    CHANNEL = 0
    GAIN = 16

    adc = Adafruit_ADS1x15.ADS1015()
    return adc.read_adc(CHANNEL, gain=GAIN)

for i in range(5):
    msg = "電流センサー: {0} V".format(reading())
    print(msg)
    time.sleep(1)