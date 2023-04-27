import RPi.GPIO as GPIO
import time
import spidev
import rgb1602
# Set up the pins
comp = 6
clk = 17
dt = 18
button = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(comp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

# Set up the SPI interface
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000

# Set up the RGB1602 display
lcd = rgb1602.RGB1602(16, 2)
lcd.setRGB(0,128,128)

def adc():
    #set 2v
    spi.xfer2([0x00, 113])
    if GPIO.input(comp) == 0:  # Greater than 2V
        #set 3v
        spi.xfer2([0x00, 91])
        if GPIO.input(comp) == 0:  # Greater than 3V
            # Set 3.5V
            spi.xfer2([0x00, 72])
            if GPIO.input(comp) == 0:  # Greater than 3.5V
                # Set 3.75V
                spi.xfer2([0x00, 50])
                if GPIO.input(comp) == 0:  # Greater than 3.75V
                    return 3.75
                else:  # Less than 3.75V
                    return 3.5
            else:  # Less than 3.5V
                # Set 3.25V
                spi.xfer2([0x00, 83])
                if GPIO.input(comp) == 0:  # Greater than 3.25V
                    return 3.25
                else:  # Less than 3.25V
                    return 3
        else:  # Less than 3V
            # Set 2.5V
            spi.xfer2([0x00, 104])
            if GPIO.input(comp) == 0:  # Greater than 2.5V
                # Set 2.75V
                spi.xfer2([0x00, 98])
                if GPIO.input(comp) == 0:  # Greater than 2.75V
                    return 2.75
                else:  # Less than 2.75V
                    return 2.5
            else:  # Less than 2.5V
                # Set 2.25V
                spi.xfer2([0x00, 108])
                if GPIO.input(comp) == 0:  # Greater than 2.25V
                    return 2.25
                else:  # Less than 2.25V
                    return 2
    else:  # Less than 2V
        # Set 1V
        spi.xfer2([0x00, 123])
        if GPIO.input(comp) == 0:  # Greater than 1V
            # Set 1.5V
            spi.xfer2([0x00, 119])
            if GPIO.input(comp) == 0:  # Greater than 1.5V
                # Set 1.75V
                spi.xfer2([0x00, 116])
                if GPIO.input(comp) == 0:  # Greater than 1.75V
                    return 1.75
                else:  # Less than 1.75V
                    return 1.5
            else:  # Less than 1.5V
                # Set 1.25V
                spi.xfer2([0x00, 121])
                if GPIO.input(comp) == 0:  # Greater than 1.25V
                    return 1.25
                else:  # Less than 1.25V
                    return 1
        else:  # Less than 1V
            # Set 0.5V
            spi.xfer2([0x00, 127])
            if GPIO.input(comp) == 0:  # Greater than 0.5V
                # Set 0.75V
                spi.xfer2([0x00, 125])
                if GPIO.input(comp) == 0:  # Greater than 0.75V
                    return 0.75
                else:  # Less than 0.75V
                    return 0.5
            else:  # Less than 0.5V
                # Set 0.25V
                spi.xfer2([0x00, 128])
                if GPIO.input(comp) == 0:  # Greater than 0.25V
                    return 0.25
                else:  # Less than 0.25V
                    return 0


while True:
        print('volt: ' + str(adc()))
        lcd.setCursor(0,0)
        lcd.printout("Voltage +/- .25v")
        lcd.setCursor(0,1)
        lcd.clear()
        lcd.printout(str(adc()) + ' volts')
    
        time.sleep(0.1)
         