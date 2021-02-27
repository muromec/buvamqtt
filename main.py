import config
import time
import machine
import umqttsimple
import random
from fan import Fan

mqtt = umqttsimple.MQTTClient(*config.mqtt_config)
try:
  mqtt.connect()
except:
  machine.reset()


def pub_fan(fan):
    speed = ['off', 'off', 'low', 'medium', 'high'][fan.speed]
    if speed == 'off':
      mqtt.publish('home/fan', 'OFF')
    else:
      mqtt.publish('home/fan', 'ON')
      mqtt.publish('home/fan/speed', speed)

fan = Fan(config.fan_model, config.fan_network)
fan.set_cb(pub_fan)

def mqtt_msg(topic, msg):
    if topic == b'home/fan/speed' or topic == b'home/fan':
        try:
            msg = {
              b'OFF': 1,
              b'ON': 2, # TODO: remember last speed
              b'off': 1,
              b'low': 2,
              b'medium': 3,
              b'high': 4,
            }.get(msg) or msg
            fan.set_speed(int(msg))
        except Exception as e:
            print('ooops', e, msg)
            
mqtt.set_callback(mqtt_msg)
mqtt.subscribe('home/fan')
mqtt.subscribe('home/fan/speed')

import loop
loop.loop(mqtt, station)
