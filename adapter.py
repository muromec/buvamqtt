import ujson
from machine import Timer

class Adapter:
  def __init__(self, mqtt, fan):
    self.mqtt = mqtt
    self.fan = fan
    self.link_done = False
    self.last_speed = None

  @property
  def state_topic(self):
    return 'homeassistant/fan/{}/state'.format(self.fan.network_id)

  @property
  def speed_topic(self):
    return 'homeassistant/fan/{}/speed'.format(self.fan.network_id)

  @property
  def config_topic(self):
    return 'homeassistant/fan/{}/config'.format(self.fan.network_id)

  @property
  def config_data(self):
    return {
      'name': 'Fan {}'.format(self.fan.network_id),
      'unique_id': str(self.fan.network_id),
      'state_topic': self.state_topic,
      'command_topic': self.state_topic,
      'speed_state_topic': self.speed_topic,
      'speed_command_topic': self.speed_topic,
      'speeds': ['off', 'low', 'medium', 'high'],
    }

  def advertise(self):
    data = ujson.dumps(self.config_data)
    packets = 30
    timer = Timer(-1)
    def send(timer):
      nonlocal packets
      self.mqtt.publish(self.config_topic, data)
      packets -= 1
      if packets < 0:
        timer.deinit()

    timer.init(period=3000, callback=send)

  def link(self):
    self.fan.set_cb(self.handle_fan)

    if not self.fan.is_ready or self.link_done:
      return

    self.link_done = True
    self.mqtt.set_callback(self.handle_mqtt)
    self.mqtt.subscribe(self.state_topic)
    self.mqtt.subscribe(self.speed_topic)
    
    self.advertise()

  def handle_mqtt(self, topic, msg):
    topic_str = str(topic, 'latin')
    if topic_str not in [self.speed_topic, self.state_topic]:
      return

    try:
        speed = {
          b'OFF': 1,
          b'ON': self.last_speed or 2,
          b'off': 1,
          b'low': 2,
          b'medium': 3,
          b'high': 4,
        }.get(msg) or int(msg)
        self.fan.set_speed(speed)
        if speed > 1:
          self.last_speed = speed

    except Exception as e:
        print('ooops', e, msg)

  def handle_fan(self, fan):
    if not self.link_done and self.fan.is_ready:
      self.link()

    speed = ['off', 'off', 'low', 'medium', 'high'][fan.speed]
    if speed == 'off':
      self.mqtt.publish(self.state_topic, 'OFF')
    else:
      self.mqtt.publish(self.state_topic, 'ON')
      self.mqtt.publish(self.speed_topic, speed)
