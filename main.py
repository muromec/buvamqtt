import config
import time
import machine
import umqttsimple
import random

import loop
from fan import Fan
from adapter import Adapter

mqtt = umqttsimple.MQTTClient(*config.mqtt_config)
try:
  mqtt.connect()
except:
  machine.reset()


fan = Fan(config.fan_model, config.fan_network)
adapter = Adapter(mqtt, fan)
adapter.link()

loop.loop(mqtt, station)
