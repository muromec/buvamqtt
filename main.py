import config
import time
import machine
import umqttsimple
import random
import fan

mqtt = umqttsimple.MQTTClient(*config.mqtt_config)
try:
  mqtt.connect()
except:
  machine.reset()


def pub_fan(fan):
    mqtt.publish('home/fan', str(fan.speed))
    
fan.Fan.cb = pub_fan

def mqtt_msg(topic, msg):
    if topic == b'home/fan/speed':
        try:
            if msg == b'off':
              msg = 1
            fan.Fan.set_speed(int(msg))
        except Exception as e:
            print('ooops', e, msg)
            
mqtt.set_callback(mqtt_msg)
mqtt.subscribe('home/fan/speed')

import loop
loop.loop(mqtt, station)
