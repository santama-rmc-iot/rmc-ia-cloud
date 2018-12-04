# -*- coding: utf-8 -*-
import Adafruit_ADS1x15
import time
import sys
from sklearn.cluster import KMeans
import pickle

repeat = 150
sleep_sec = 0.01

exist_list = []
not_exist_list = []

def reading():
    CHANNEL = 0
    GAIN = 16

    adc = Adafruit_ADS1x15.ADS1115()
    return adc.read_adc(CHANNEL, gain=GAIN) * (0.256 / 32768)


start = input("機械学習を始めます。よろしいですか？(yes or no) : ")
if start != "yes":
  exit(0)

print("まず、電源OFFのデータを1分間収集します。センサーに接続している電化製品の電源をOFFにしてください。")
input("準備ができたら、enterキーを押してください。enterキー押下後5秒後に開始します。")

for i in [5,4,3,2,1]:
  print(str(i) + "秒前")
  time.sleep(1)

print("スタート")

for i in range(repeat):
    value = reading()

    exist_list.append(value)
    msg = "電流センサー: {0} V".format(reading())
    print(msg)
    time.sleep(sleep_sec)

print("つぎに、電源ONのデータを1分間収集します。センサーに接続している電化製品の電源をOFFにしてください。")
input("準備ができたら、enterキーを押してください。enterキー押下後5秒後に開始します。")

for i in [5,4,3,2,1]:
  print(str(i) + "秒前")
  time.sleep(1)

print("スタート")

for i in range(repeat):
    value = reading()

    not_exist_list.append(value)
    msg = "電流センサー: {0} V".format(reading())
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

#print("[電源ON」結果：" + ','.join(map(str,exist_list)))
#print("[電源OFF」結果：" + ','.join(map(str, not_exist_list)))

pickle.dump(model, open("ct_model.sav", "wb"))