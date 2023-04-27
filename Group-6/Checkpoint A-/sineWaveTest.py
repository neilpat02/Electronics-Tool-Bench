import pigpio
import spidev
import rgb1602

#lcd = rgb1602.RGB1602(16,2)
pi = pigpio.pi()

cs = 7
pin = 13
pi.set_mode(cs, pigpio.OUTPUT)

spi = spidev.SpiDev()

def pot(device, pot_num, stepValue):
    if device == 2:
        pi.write(cs, 1)
        spi.open(0,1)
    
    spi.max_speed_hz = 1000000
    if pot_num == 1:
        spi.xfer2([0x00, stepValue])
    elif pot_num == 2:
        spi.xfer2([0x10, stepValue])
    


pot(2,1,49)
pot(2,2,0)

while True:
    pi.hardware_PWM(pin, 9400, 500000)

spi.close()
pi.stop()

#MISSED RANGE 6500-6600
#CAPS OUT FREQ=1100 1.25V