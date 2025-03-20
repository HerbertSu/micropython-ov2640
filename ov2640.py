from ov2640_constants import *
from ov2640_lores_constants import *
from ov2640_hires_constants import *
import machine
from machine import Pin
import time
import ubinascii
import uos
import gc

class ov2640(object):
    def __init__(self, sclpin=27, sdapin=26, cspin=17, resolution=OV2640_320x240_JPEG):
        self.sdapin=sdapin
        self.sclpin=sclpin
        self.cspin=cspin
        self.standby = False

        spi_baudrate = 8000000
        camera_open_time = 200 # milliseconds

        self.hspi = machine.SPI(0, baudrate=spi_baudrate, polarity=0, phase=0)
        self.i2c = machine.I2C(1, scl=machine.Pin(sclpin), sda=machine.Pin(sdapin), freq=100000)
    
        # first init spi assuming the hardware spi is connected
        self.hspi.init(baudrate=spi_baudrate)

        # chip select -- active low
        self.cspin = machine.Pin(cspin, machine.Pin.OUT)
        self.cspin.on()

        # init the i2c interface
        self.i2c.scan()
   
        # select register set
        self.i2c.writeto_mem(SENSORADDR, 0xff, b'\x01')
        # initiate system reset
        self.i2c.writeto_mem(SENSORADDR, 0x12, b'\x80')
       
        # let it come up
        led = Pin(25, Pin.OUT)
        led.toggle()
        time.sleep_ms(camera_open_time)
        led.toggle()
    
        # jpg init registers
        cam_write_register_set(self.i2c, SENSORADDR, OV2640_JPEG_INIT)
        cam_write_register_set(self.i2c, SENSORADDR, OV2640_YUV422)
        cam_write_register_set(self.i2c, SENSORADDR, OV2640_JPEG)
   
        # select register set
        self.i2c.writeto_mem(SENSORADDR, 0xff, b'\x01')
        self.i2c.writeto_mem(SENSORADDR, 0x15, b'\x00')
   
        # select jpg resolution
        cam_write_register_set(self.i2c, SENSORADDR, resolution)
    
        # register set select
        self.i2c.writeto_mem(SENSORADDR, 0xff, b'\x01')

    def capture_to_file(self, fn, overwrite):
        # bit 0 - clear FIFO write done flag
        cam_spi_write(b'\x04', b'\x01', self.hspi, self.cspin)
    
        # bit 1 - start capture then read status
        cam_spi_write(b'\x04', b'\x02', self.hspi, self.cspin)
        time.sleep_ms(100)
    
        # read status
        res = cam_spi_read(b'\x41', self.hspi, self.cspin)
        cnt = 0

        # read the image from the camera fifo
        while True:
            res = cam_spi_read(b'\x41', self.hspi, self.cspin)
            mask = b'\x08'
            if (res[0] & mask[0]):
                break
            time.sleep_ms(10)
            cnt += 1
   
        # read the fifo size
        b1 = cam_spi_read(b'\x44', self.hspi, self.cspin)
        b2 = cam_spi_read(b'\x43', self.hspi, self.cspin)
        b3 = cam_spi_read(b'\x42', self.hspi, self.cspin)
        val = b1[0] << 16 | b2[0] << 8 | b3[0] 
        print("%d bytes captured in fifo" % val)
        gc.collect()
    
        bytebuf = [ 0, 0 ]
        picbuf = [ b'\x00' ] * PICBUFSIZE
        l = 0
        bp = 0
        if (overwrite == True):
            try:
                uos.remove(fn)
            except OSError:
                pass
        while ((bytebuf[0] != b'\xd9') or (bytebuf[1] != b'\xff')):
            bytebuf[1] = bytebuf[0]
            if (bp > (len(picbuf) - 1)):
                appendbuf(fn, picbuf, bp)
                bp = 0
    
            bytebuf[0] = cam_spi_read(b'\x3d', self.hspi, self.cspin)
            l += 1
            picbuf[bp] = bytebuf[0]
            bp += 1
        if (bp > 0):
            appendbuf(fn, picbuf, bp)
        print("read %d bytes from fifo, camera said %d were available" % (l, val))
        return (l)

    # XXX these need some work
    def standby(self):
        # register set select
        self.i2c.writeto_mem(SENSORADDR, 0xff, b'\x01')
        # standby mode
        self.i2c.writeto_mem(SENSORADDR, 0x09, b'\x10')
        self.standby = True

    def wake(self):
        # register set select
        self.i2c.writeto_mem(SENSORADDR, 0xff, b'\x01')
        # standby mode
        self.i2c.writeto_mem(SENSORADDR, 0x09, b'\x00')
        self.standby = False

def cam_write_register_set(i, addr, set):
    for el in set:
        raddr = el[0]
        val = bytes([el[1]])
        if (raddr == 0xff and val == b'\xff'):
            return
        i.writeto_mem(addr, raddr, val)

def appendbuf(fn, picbuf, howmany):
    try:
        f = open(fn, 'ab')
        c = 1
        for by in picbuf:
            if (c > howmany):
                break
            c += 1
            f.write(bytes([by[0]]))
        f.close()
    except OSError:
        print("error writing file")

def cam_spi_write(address, value, hspi, cspin):
    cspin.off()
    modebit = b'\x80'
    d = bytes([address[0] | modebit[0], value[0]])
    hspi.write(d)
    cspin.on()

def cam_spi_read(address, hspi, cspin):
    cspin.off()
    maskbits = b'\x7f'
    wbuf = bytes([address[0] & maskbits[0]])
    hspi.write(wbuf)
    buf = hspi.read(1)
    cspin.on()
    return (buf)

# cam driver code
# https://github.com/kanflo/esparducam/blob/master/arducam/arducam.c
# register info
# https://github.com/ArduCAM/Sensor-Regsiter-Decoder/blob/master/OV2640_JPEG_INIT.csv




