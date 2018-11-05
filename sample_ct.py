# -*- coding: utf-8 -*-
import Adafruit_ADS1x15
import time

def reading():
    CHANNEL = 0
    GAIN = 16

    adc = Adafruit_ADS1x15.ADS1115()
    return adc.read_adc(CHANNEL, gain=GAIN) * (0.256 / 32768)

for i in range(5):
    msg = "電流センサー: {0} V".format(reading())
    print(msg)
    time.sleep(1)