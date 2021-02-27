import config
import machine
machine.freq(80000000)
import network
import time
import dup


station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(config.wifi_network, config.wifi_password)

while not station.isconnected():
  time.sleep(0.1)

# uncomment following line to enable debug output:
#dup.start(config.log_host, config.log_port)
# run `nc -k -u -l -p $port` on $log_host to see debug output.
