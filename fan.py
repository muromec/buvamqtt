from nrf905 import NRF, be32

channel_buva = 117 # 868200000
channel_zehnder = 118 # 868400000
band = True
tx_power = 0x03
rx_power = False
retrans = True
rx_addr_width = 4
tx_addr_width = 4
rx_width = 16
tx_width = 16

LINK_ADDR = 0xA55A5AA5

clckout = 500000
clckout_enable = False
xtal = 16000000
crc = 16

conf_buva = (
  channel_buva, band, tx_power, rx_power, retrans,
  rx_addr_width, tx_addr_width, rx_width, tx_width,
  clckout, clckout_enable, xtal, crc
)
conf_zehnder = (channel_zehnder, ) + conf_buva[1:]


class Fan:
  def __init__(self, model='zehnder', network_id=None):

    self.speed = 0
    self.cb = None
    self.model = model
    self.network_id = LINK_ADDR if network_id is None else network_id

    self.nrf = NRF()
    self.configure_nrf()
    self.nrf.listen(self.frame_handler)

  def configure_nrf(self):
    conf = conf_buva if self.model == 'buva' else conf_zehnder
    self.nrf.read_config()
    self.nrf.configure(self.network_id, *conf)

  def set_cb(self, cb):
    self.cb = cb

  def set_speed(self, speed):
    if self.speed == speed:
      return

    self.speed = speed

    buf = bytearray(b'\x01\x00\x03\x00\xfa\x02\x01\x01')
    buf[7] = speed
    buf[3] = 89 # remote id
    self.nrf.send_frame(self.network_id, buf)

  def frame_handler(self, rbuf):
    cmd = {
      2: 'set_speed',
      3: 'set_timer',
      5: 'speed_ack',
      6: 'link_ad',
      7: 'settings',
    }.get(rbuf[6]) or rbuf[6]
    plen = rbuf[7]
    payload = rbuf[8:8+plen]

    msg = {'ttype': rbuf[3], 'tid': rbuf[4], 'cmd': cmd, 'payload': payload}
    print(msg)

    if cmd == 'set_speed' or cmd == 'settings':
      self.speed = payload[0]

    if cmd == 'link_ad' and self.network_id == LINK_ADDR:
      self.network_id = be32(payload)
      print('got network id', hex(self.network_id))
      self.configure_nrf()

    if self.cb:
      self.cb(self)
