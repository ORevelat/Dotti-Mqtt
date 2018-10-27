import paho.mqtt.client as mqtt
import time
import json
import ast

from config import Config
from dotti import Dotti
from logger import Logger as logger

DoNotExit = True

def on_message(client, userdata, message):
	if message.topic != Config.server_topic:
		return

	global DoNotExit
	if not DoNotExit:
		return
	
	try:
		j = json.loads(str(message.payload.decode("utf-8")))
		
		device_mac = str(Config.dotti_mac)
		if "mac" in j:
			device_mac = str(j["mac"])

		mode = str(j["mode"])
		color = [0,0,0]
		if mode == "color" and "color" in j:
			color = ast.literal_eval(str(j["color"]))

		if DoNotExit and mode == "exit":
			DoNotExit = False
			return

		if mode != "hour" and mode != "color":
			print("ERROR - unknown mode=" + mode)
			return

		dotti = Dotti(device_mac)
		dotti.mode(mode, color)
		
	except ValueError:
		logger.error("decoding house/dotti payload failed !")
	except:
		logger.error("processing house/dotti payload failed !")

def on_log(client, userdata, level, buf):
    logger.debug("log: " + buf)

"""

Entry point
	- server to run continuously
	-  mqtt client that subscribe to a topic and process messages within 

"""

client = mqtt.Client("hass-dotti")
client.on_message = on_message
# client.on_log = on_log
client.username_pw_set(Config.user_name, Config.user_pwd)

client.connect(Config.server_addr, Config.server_port)
client.loop_start()

client.subscribe(Config.server_topic)

try:
    while DoNotExit:
        time.sleep(1)
except KeyboardInterrupt:
    logger.error('interrupted!')

client.loop_stop()
