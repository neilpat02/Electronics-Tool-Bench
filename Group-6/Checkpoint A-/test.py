
import time
import rgb1602
import spidev
import pigpio


cs1 = 7
cs2 = 8

gpio = pigpio.pi()
gpio.set_mode(cs1, pigpio.OUTPUT)
gpio.set_mode(cs2, pigpio.OUTPUT)

spi0 = spidev.SpiDev()
spi0.open(0,0)
spi1 = spidev.SpiDev()
spi1.open(0,1)

def set_pot(pot_num, value):
    #gpio.write(cs, 0)
    #spi0.xfer2([device, value])
    #gpio.write(cs, 1)
    if pot_num == 1:
        print("inside 1")
        gpio.write(cs1, pigpio.LOW)
        spi0.xfer2([value])
        gpio.write(cs1, pigpio.HIGH)
        
    elif pot_num == 2:
        print("inside 2")
        gpio.write(cs2, pigpio.LOW)
        spi1.xfer2([value])
        gpio.write(cs2, pigpio.HIGH)


def main():
    #set_pot(0x10, cs1, 128)
    #set_pot(0x00, cs2, 0)
    set_pot(1,0)
    set_pot(2,0)
    while True:
        
        gpio.hardware_PWM(12, 1000, 500000)

    #set_pot(0x10, cs1, 0)
    #set_pot(0x00, cs2, 0)
main()
gpio.close()

