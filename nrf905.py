# nRF905 driver for micropython (esp32)
import time
from machine import SPI, Pin

def be32(buf):
  addr = buf[0]
  addr |= buf[1] << 8
  addr |= buf[2] << 16
  addr |= buf[3] << 24
  return addr

class NRF:
  def __init__(self):
    self.retrans_n = 0
    self.spics = Pin(15, Pin.OUT)
    self.spi = SPI(1, 1000000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))

    self.am = Pin(32, Pin.IN)
    self.cd = Pin(33, Pin.IN)
    self.dr = Pin(35, Pin.IN)

    self.ce = Pin(27, Pin.OUT)
    self.pwr = Pin(26, Pin.OUT)
    self.txen = Pin(25, Pin.OUT)
    self.icoming_frame_cb = None
    self.tx = False
    self.tx_id = None

    _tx_h = self.dr_handler_tx
    _rx_h = self.dr_handler_rx
    def dr_handler(pin):
      (_tx_h if self.tx else _rx_h)(pin)

    self.dr.irq(dr_handler, Pin.IRQ_RISING)

  def mode_off(self):
    self.tx = False
    self.pwr.off()
    self.ce.off()
    self.txen.off()

  def mode_idle(self):
    self.tx = False
    self.pwr.on()
    self.ce.off()
    self.txen.off()

  def mode_transmit(self):
    self.tx = True
    self.pwr.on()
    self.txen.on()
    self.ce.on()

  def mode_receive(self):
    self.tx = False
    self.pwr.on()
    self.txen.off()
    self.ce.on()

  def transact(self, rbuf):
    self.spics.off()
    self.spi.write_readinto(rbuf, rbuf)
    self.spics.on()
    return rbuf

  def configure(self,
    rx_addr,
    channel, band, tx_power, rx_power, retrans,
    rx_addr_width, tx_addr_width, rx_width, tx_width,
    clckout, clckout_enable, xtal, crc):

    rbuf = bytearray(11)
    rbuf[0] = 0
    rbuf[1] = channel & 0xFF
    rbuf[2] = (channel >> 8) & 0x01
    rbuf[2] |= 0x02 if band  else 0x00
    rbuf[2] |= (tx_power & 0x03) << 2
    rbuf[2] |= 0x10 if rx_power else 0x00
    rbuf[2] |= 0x20 if retrans else 0x00
    rbuf[3] = (rx_addr_width & 0x07) | ((tx_addr_width & 0x07) << 4)
    rbuf[4] = rx_width & 0x3F
    rbuf[5] = tx_width & 0x3F

    rbuf[6] = rx_addr & 0xFF
    rbuf[7] = (rx_addr >> 8) & 0xFF
    rbuf[8] = (rx_addr >> 16) & 0xFF
    rbuf[9] = (rx_addr >> 24) & 0xFF

    rbuf[10] = 0x03 # clk out 500000
    rbuf[10] |= 0x04 if clckout_enable else 0x00
    rbuf[10] |= (int(xtal / 4000000) - 1 ) << 3
    rbuf[10] |= 0x40 if crc else 0x00
    rbuf[10] |= 0x80 if (crc == 16) else 0x00

    self.mode_idle()
    self.transact(rbuf)
    self._config = (
      channel, band, tx_power, rx_power, retrans,
      rx_addr, rx_addr_width, tx_addr_width, rx_width, tx_width,
      clckout, clckout_enable, xtal, crc
    )


  def read_config(self):
    rbuf = bytearray(11)
    rbuf[0] = 0x10
    rbuf = self.transact(rbuf)

    channel = rbuf[1] 
    channel |= (rbuf[2] & 0x01) << 8
    band = bool(rbuf[2] & 0x02)
    tx_power = (rbuf[2] >> 2) & 0x03
    rx_power = bool(rbuf[2] & 0x10)
    retrans = bool(rbuf[2] & 0x20)
    rx_addr_width = rbuf[2] & 0x07
    tx_addr_width = (rbuf[3] >> 4) & 0x07
    rx_width = rbuf[4] & 0x3F
    tx_width = rbuf[5] & 0x3F

    rx_addr = be32(rbuf[6:])

    clckout = (4000000 >> (rbuf[10] & 0x03))
    clckout_enable = bool(rbuf[10] & 0x04)
    xtal = (((rbuf[10] >> 3) & 0x7) + 1) * 4000000

    crc = 16 if bool(rbuf[10] & 0x80) else 8
    crc = crc if rbuf[10] & 0x40 else None

    self._config = (
      channel, band, tx_power, rx_power, retrans,
      rx_addr, rx_addr_width, tx_addr_width, rx_width, tx_width,
      clckout, clckout_enable, xtal, crc
    )


  def set_addr(self, tx_addr):
    rbuf = bytearray(5)
    rbuf[0] = 0x22
    rbuf[1] = tx_addr & 0xFF
    rbuf[2] = (tx_addr >> 8) & 0xFF
    rbuf[3] = (tx_addr >> 16) & 0xFF
    rbuf[4] = (tx_addr >> 24) & 0xFF

    self.transact(rbuf)

  def get_addr(self):
    rbuf = bytearray(5)
    rbuf[0] = 0x23
    return be32(self.transact(rbuf)[1:])

  def read_frame(self):
    rbuf = bytearray(33)
    rbuf[0] = 0x24
    self.transact(rbuf)
    self.ce.off()
    self.ce.on()
    return rbuf

  def send_frame(self, tx_addr, buf, retrans_n=10):
    self.retrans_n = retrans_n
    self.mode_idle()
    self.set_addr(tx_addr)
    
    self.transact(bytearray([0x20]) + buf)
    self.tx_id = tx_id = time.ticks_cpu()

    self.mode_transmit()

  def dr_handler_tx(self, pin):
    self.retrans_n -= 1
    if self.retrans_n > 0:
      return

    self.tx_id = None
    self.mode_receive()

  def dr_handler_rx(self, pin):
    rbuf = self.read_frame()
    if self.icoming_frame_cb:
      self.icoming_frame_cb(rbuf)

  def listen(self, cb):
    self.icoming_frame_cb = cb
    self.mode_receive()
