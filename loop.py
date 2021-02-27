import machine

def loop(mqtt, station):
  while station.isconnected():
    try:
      mqtt.ping()
      mqtt.ping()
      mqtt.ping()
      mqtt.sock.settimeout(1)
      mqtt.wait_msg() 
    except Exception as e:
      print('loop e', e)
      machine.reset()

    try:
      while True:
        mqtt.sock.settimeout(60)
        mqtt.wait_msg()
    except Exception as e:
      print('loop e2', e)
      pass

  machine.reset()
