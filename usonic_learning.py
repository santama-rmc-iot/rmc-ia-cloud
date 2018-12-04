# -*- coding: utf-8 -*-
import time
import sys
import RPi.GPIO as GPIO
from sklearn.cluster import KMeans
import pickle

repeat = 150
sleep_sec = 1

exist_list = []
not_exist_list = []

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

start = input("機械学習を始めます。よろしいですか？(yes or no) : ")
if start != "yes":
  exit(0)

print("まず、人がいないデータを2分間収集します。人がいないシチュエーションを作ってください。")
input("準備ができたら、enterキーを押してください。enterキー押下後5秒後に開始します。")

for i in [5,4,3,2,1]:
  print(str(i) + "秒前")
  time.sleep(1)

print("スタート")

for i in range(repeat):
    value = reading()

    exist_list.append(value)
    msg = "超音波センサー: {0} cm".format(reading())
    print(msg)
    time.sleep(sleep_sec)

print("つぎに、人がいるデータを2分間収集します。人がいるシチュエーションを作ってください。")
input("準備ができたら、enterキーを押してください。enterキー押下後5秒後に開始します。")

for i in [5,4,3,2,1]:
  print(str(i) + "秒前")
  time.sleep(1)

print("スタート")

for i in range(repeat):
    value = reading()

    not_exist_list.append(value)
    msg = "超音波センサー: {0} cm".format(reading())
    print(msg)
    time.sleep(sleep_sec)


print("学習処理をします。少々時間がかかるかもしれません。")


learning_list_of_exist = [[value] for value in exist_list]
learning_list_of_not_exist = [[value] for value in not_exist_list]

learning_list = learning_list_of_exist + learning_list_of_not_exist
#import pdb; pdb.set_trace()
model = KMeans(n_clusters=2)

model.fit(learning_list)

print(model.predict([[exist_list[0]]]))
print(model.predict([[not_exist_list[0]]]))

pickle.dump(model, open("usonic_model.sav", "wb"))