# イントロダクション

2018年度の中小企業診断士 三多摩支部 IoT活用研究会のテーマとして、
作成している電流センサーとCTセンサーを活用するためのソフトウェアです。

会員の橋向氏が構築された「ia-cloud」（IoT向けクラウドサービスフレームワーク)を活用させてもらい実装しています。

# ラズベリーパイの準備

ご自宅にネット回線を引いていることが前提になっています。

## 必要なモノ
Raspberry PI3 model B
HDMIケーブル
LANケーブル(WIFIがついてるためなくてもいけますが、あるといいかも)
外部ディスプレイ(HDMIで接続できればOK)
キーボード(USB)
マウス(USB)
センサー付きブレッドボード(清水氏考案のモノ)
microSDカード 32GB程度
microSDカードを差し込めるwindowsパソコン

# 環境の構築
## OSのインストール

若干時間を要しますので、余裕があるときに行ってください。
すでに事例が多数ありますので、下記の記事を参考にご準備ください。

http://share-lab.net/raspberrypi2

## 環境構築

ADS1115用のpythonライブラリを追加する。

```
$ git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git
$ cd Adafruit_Python_ADS1x15/
$ sudo python3 setup.py install
```


