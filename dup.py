import uio
import usocket as socket

class Proxy(uio.IOBase):
    def __init__(self, host, port):
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
      self.addr = (host, port)
    
    def write(self, buf):
        try:
          self.sock.sendto(buf, self.addr)
        except:
          pass
        
    def readinto(self, *args): pass
    
def start(host, port):
    import os
    os.dupterm(Proxy(host, port))
    
