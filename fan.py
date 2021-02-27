import nrf905

#channel = 117 # 868200000  buva
channel = 118 # 868400000 zehnder
band = True
tx_power = 0x03
rx_power = False
retrans = True
rx_addr_width = 4
tx_addr_width = 4
rx_width = 16
tx_width = 16

rx_addr = 0xA55A5AA5 # link
rx_addr = 0xe0101010 # real CHANGE THIS

clckout = 500000
clckout_enable = False
xtal = 16000000
crc = 16

tx_addr = 0xA55A5AA5 # link
tx_addr = 0x01010101 # real CHANGE THIS
conf = (
  channel, band, tx_power, rx_power, retrans,
  rx_addr, rx_addr_width, tx_addr_width, rx_width, tx_width,
  clckout, clckout_enable, xtal, crc
)

def frame_handler(rbuf):
  cmd = {
    2: 'set_speed',
    3: 'set_timer',
    5: 'speed_ack',
    7: 'settings',
  }.get(rbuf[6]) or rbuf[6]
  plen = rbuf[7]
  payload = rbuf[8:8+plen]

  msg = {'ttype': rbuf[3], 'tid': rbuf[4], 'cmd': cmd, 'payload': payload}
  print(msg)

  if cmd == 'set_speed' or cmd == 'settings':
    Fan.speed = payload[0]

  if Fan.cb:
    Fan.cb(Fan)


class Fan:
  speed = 0
  cb = None

  def set_speed(speed):
    Fan.speed = speed

    buf = bytearray(b'\x01\x00\x03\x00\xfa\x02\x01\x01')
    buf[7] = speed
    buf[3] = 89 # remote id
    nrf.send_frame(tx_addr, buf)

  def inspect():
    nrf.read_config()
    print('nrf config', nrf._config)
    


nrf = nrf905.NRF()
nrf.read_config()
nrf.configure(*conf)

nrf.listen(frame_handler)
