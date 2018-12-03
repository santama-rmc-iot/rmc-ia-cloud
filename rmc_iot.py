#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
ia-cloud sample application for raspberryPi module using a ia_cloud pakage.

Usage:
	This application gets RaspberryPi's CPU information and GPIO digital
	input data and stores to CCS.
	Data acquisition application configration file must be provided as an
	argument of this application.
	Module attribute
		PINS_INPUT = (tuple of pin number)
		PINS_OUTPUT = (tuple of pin number)
	define the GPIO i/o default configuration.
'''
import pdb
import sys
import time
#jsonのパッケージ
import json
# Python組込のデータコンテナに変わるコンテナのパッケージ OrderedDictを利用
from collections import OrderedDict
# Shellコマンドを呼び出すパッケージ
import subprocess
# マルチスレッドのモジュール
import threading
# シグナルをハンドルするパッケージ
import signal
import logging

# requestsモジュールの例外の定義をインポート
from requests.exceptions import ConnectionError, Timeout
# RaspberryPiのGPIOを制御するパッケージ
import RPi.GPIO as GPIO

# ia-cloudのパッケージをインポート
from ia_cloud.ia_cloud_app import IaCloudApp
from ia_cloud.ia_cloud_connection import IaCloudConnection, CCSBadResponseError

import Adafruit_ADS1x15

# GPIOのPinの入出力設定のデフォルト値
# アプリケーションの設定JSONファイルの"userAppConfig"エントリーで変更が可能
PINS_INPUT = (16)
PINS_OUTPUT = (12)
# Outputをトグルする間隔を秒数でセット
TOGGLE＿INTERVAL = 30
# GPIO event監視チャネル
EVENT_CH = 40

def ct_sensor_value():
	adc = Adafruit_ADS1x15.ADS1115()
	return adc.read_adc(0, 16) * (0.256 / 32768)

def usonic_sensor_value():
	GPIO.output(12, True)
	time.sleep(0.00001)
	GPIO.output(12, False)

	while GPIO.input(16) == 0:
		signal_off = time.time()

	while GPIO.input(16) == 1:
		signal_on = time.time()

	time_passed = signal_on - signal_off
	distance = time_passed * 17000

	return distance

#-------------------------------------------------------
# RaspberryPi GPIO 初期設定
#-------------------------------------------------------
def _GPIO＿init(pins_input:tuple, pins_output:tuple):
	'''
	This function initializes and cofigurates GPIO of the RaspberryPi.

	Args:
		pins_input(tuple):
			A tuple of PIN numbers that would be assigned to input.
			PIN numbers are using the BOARD numbering system. This refers
			to the pin numbers on the P1 header of the Raspberry Pi board.
		pins_output(tuple):
			A tuple of PIN numbers that would be assigned to output.
			Pin numbers are same as the above.
	'''
	# GPIOの再設定warningを停止
	GPIO.setwarnings(False)

	# GPIOを設定する。
	GPIO.setmode(GPIO.BOARD)	# Pin番号指定をボードコネクタPin番号で

	# 入力Pinをプルアップで設定
	GPIO.setup(pins_input, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	# 出力Pinをdefault Hi で設定
	GPIO.setup(pins_output, GPIO.OUT,  initial=GPIO.HIGH)

#-------------------------------------------------------
# RaspberryPi GPIOのDOをトグルする関数・別スレッドとして起動される
#-------------------------------------------------------
def _GPIO_toggle_out(pins:tuple, interval:int, event:threading.Event):
	'''
	A function to toggle the specific output pins of RaspberryPi's GPIO.
	It is supposed to be a child thread. So that, a threading.Event instance
	should be an argument in order to stop this thread by Event.

	Args:
		pins(tuple):
			A tuple of PIN numbers that would be periodically toggled.
			PIN numbers are using the BOARD numbering system. This refers
			to the pin numbers on the P1 header of the Raspberry Pi board.
		interval(int):
			A int value for interval of toggle action.
		event(threading.Event):
			A Event instance for recieve thread event in order to terminate
			this function's thread.
	'''
	# イベントを受けるまで無限に実行
	while True:
		# ターゲットのDOのPinをトグル
		for pin in pins:
			GPIO.output(pin, not GPIO.input(pin))
		# interval秒待ち、イベントの有無をチェック
		if event.wait(interval):
			# イベントを受信したらスレッドを終了
			break


#-------------------------------------------------------
# アプリケーションクラスの定義
# ia_cloud_app.pyモジュールのIaCloudAppクラスを拡張する。
#-------------------------------------------------------
class MyIaCloudApp(IaCloudApp):

	#-------------------------------------------------------
	# AIからデータを取得するための内部メソッドをオーバーライドし、
	# GPIOを読み込む機能をメソッドに追加
	#-------------------------------------------------------

	def _get_data(self, source:str, obj_content:dict):
		if source == "CPU_info":		# CPU温度を取得

			# データソースがCPU情報だったら、親クラスの_get_data()を呼び出す
			obj_content = super()._get_data(source, obj_content)

		elif source == "SENSORS_INFO":
			sensors = obj_content["contentData"]

			for sensor in sensors:
				if sensor["dataName"] == "CTセンサー":
					sensor["dataValue"] = ct_sensor_value()
				elif sensor["dataName"] == "超音波センサー":
					sensor["dataValue"] = usonic_sensor_value()

				msg = "{0} [{1}]: {2}".format(sensor["dataName"], sensor["unit"], sensor["dataValue"])
				self.logger.info(msg)

		else : obj_content["contentData"] = []

		# オブジェクトコンテントをリターン
		return obj_content

	#-------------------------------------------------------
	# RaspberryPi GPIOの入力の変化のcallbackを受けるメソッドを定義
	# 対応するデータオブジェクト名を探し出し、非同期収集のメソッドを起動
	#-------------------------------------------------------
	def GPIO_event_handler(self, pin:int):
		'''
		A GPIO event handler method. function

		Args:
			pin(int):
				A PIN number of GPIO board that change event has been occurd
		'''
		# 対象の入力状態から、edgeの方向を判定
		p_edge = GPIO.input(pin)

		# CCSへ格納すべきデータオブジェクトリストを取得
		obj_conf_list = self.options["asyncObjects"]

		# データオブジェクト名に空文字列
		on_name = ""
		off_name = ""

		# オブジェクトリストをサーチ
		for obj_name in obj_conf_list:
			# 対象のデータオブジェクトを探索
			if obj_name == "GPIO_"+str(pin)+"_on":
				on_name = obj_name

			elif obj_name == "GPIO_"+str(pin)+"_off":
				off_name = obj_name

		# オブジェクト名が空文字列だったら
		if not on_name or not off_name:
			# 対象のデータオブジェクトが存在しないのでログを出力しリターン
			msg = "Target object name can't be found at GPIO event handler"
			self.logger.error(msg)
			return

		# 対象のオブジェクトを使用し、エッジのデータペアーを格納
		pre_name = off_name if p_edge else on_name
		aft_name = on_name if p_edge else off_name

		iac_app.async_trigger(pre_name)
		iac_app.async_trigger(aft_name)

#-------------------------------------------------------
# signalイベントハンドラ
#-------------------------------------------------------
def _signal_handler(signum, frame, app:IaCloudApp,
					th_tgle:threading.Thread, event:threading.Event
					):
	'''
	A signal handler function that should be set by signal.signal().
	The handler would call ia_clod_app.stop() to terminate data acquisition
	threads, set Event to stop a toggling thread and shutdown the logging
	 system. Then exit the application with sys.exit().

	Usage:
		signal.signal(signal.SIGTERM,
			(lambda a,b: _signal_handler(a, b, iac_app, th_toggle, GPIOevt)))
		signal.signal(signal.SIGINT,
			(lambda a,b: _signal_handler(a, b, iac_app, th_toggle, GPIOevt)))
		signal.signal(signal.SIGALRM,
			(lambda a,b: _signal_handler(a, b, iac_app, th_toggle, GPIOevt)))
	Args:
		ia_clod_app(IaCloudApp): ia-cloud application instance.
		th_tgle(threading.Thread):
		A Thread object for toggling GPIO outputs which should be stopped when
		SIGNAL interruppt.
		event(threading.Event):
		event object to be set in order to stop the toggle thread.
	'''
	# CCSへのデータ送信を停止
	app.stop()

	# トグルスレッドにEventをセット
	event.set()
	# GPIOトグルスレッドの停止を待つ
	while True :
		if th_tgle.is_alive():
			continue
		break

		# GPIOの設定をクリア
	GPIO.cleanup()

	if signum == signal.SIGALRM:
		# 内部エラーによるsignalの場合
		msg = "Application has been terminated by comunication error with CCS"
	else:
		# キーボードなどの割り込みによる中断
		msg = "Application has been terminated by key interruppt"

	iac_app.logger.error(msg)
	# ロギングシステムを終了
	logging.shutdown()

	# アプリケーションを終了
	sys.exit()


#-------------------------------------------------------
# main処理スクリプト
#-------------------------------------------------------

if __name__ == "__main__":

	# 各種設定情報をここで読み取る。
	argvs = sys.argv  # コマンドライン引数を格納したリストの取得
	argc = len(argvs) # 引数の個数

	# ファイル名が引数にない場合は、デフォルトのファイル名
	fname = "./rmc_iot_config.json"  if argc == 1 else argvs[1]

	# 設定情報の入ったjsonファイルを辞書型のconfに読み込み
	with open(fname, encoding="utf-8") as f:

	# 設定ファイルからJSONを読み出す。
	# collections.OrderedDictオブジェクトを使い、json内の出現順を維持
		FDS_config = json.load(f, object_pairs_hook=OrderedDict)

	# GPIOの設定情報を取得し、デフォルト設定を上書き
	if "userAppConfig" in FDS_config:
		app_config = FDS_config.pop("userAppConfig")
		GPIO_config = app_config["GPIOConfig"]

		PINS_INPUT = GPIO_config["GPIOInputPins"]
		PINS_OUTPUT = GPIO_config["GPIOOutputPins"]
		# Outputをトグルする間隔を秒数でセット
		TOGGLE＿INTERVAL = GPIO_config["toggleInterval"]
		# GPIO event監視チャネル
		EVENT_CH = GPIO_config["eventWatchCh"]

	# iaCloudアプリケーションクラスをのインスタンスを作成
	iac_app = MyIaCloudApp(FDS_config=FDS_config)

	# GPIOを初期設定する。
	_GPIO_init(PINS_INPUT, PINS_OUTPUT)

	# スレッドへ停止を伝えるイベントを作成
	GPIOevt = threading.Event()

	# 設定秒毎にGPIO出力を反転するスレッドを起動
	# 停止用のイベントインスタンスを引数で渡す
	th_toggle = threading.Thread(
			target=_GPIO_toggle_out,name="th_GPIO_tgl",
			args=(PINS_OUTPUT, TOGGLE＿INTERVAL, GPIOevt)
			)
	th_toggle.start()

	# GPIOの割り込みイベントハンドラーをセット
	# GPIO.add_event_detect(
	# 		EVENT_CH, GPIO.BOTH,
	# 		callback = iac_app.GPIO_event_handler,
	# 		bouncetime = 30
	# 		)

	# エラー時やKey割り込み時のシグナルハンドラーを設定
	signal.signal(signal.SIGTERM,
		(lambda a,b: _signal_handler(a, b, iac_app, th_toggle, GPIOevt)))
	signal.signal(signal.SIGINT,
		(lambda a,b: _signal_handler(a, b, iac_app, th_toggle, GPIOevt)))
	signal.signal(signal.SIGALRM,
		(lambda a,b: _signal_handler(a, b, iac_app, th_toggle, GPIOevt)))

	try:
		# データの周期収集をスタート
		iac_app.start()

		# 無限ループ。KeyInterruptかエラーで抜ける。
		while True:
				time.sleep(1)

	except Exception as err:

		# 予期せぬエラーが発生した場合
		msg = "IaCloudApp has been stopped by an uncaught Error"
		iac_app.logger.error(msg)
		iac_app.logger.error(err)
		iac_app.logger.error(type(err))

		# エラー終了
		sys.exit()
