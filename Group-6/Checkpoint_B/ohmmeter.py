import RPi.GPIO as GPIO
import time
import rgb1602
import spidev

# Set up the pins
compOut = 5
clk = 17
dt = 18
button = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(compOut, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

# Set up the RGB1602 display
lcd = rgb1602.RGB1602(16, 2)
lcd.setRGB(0,128,128)

# Set up the SPI interface
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000
spi.xfer2([0x10, 128])


def res_val():
    
    wiper_pos = 128
    spi.xfer2([0x10, wiper_pos])
    while GPIO.input(compOut) == 0:
        
        time.sleep(0.01)
        spi.xfer2([0x10, wiper_pos])
        wiper_pos -= 1
        print("inside while loop: ", wiper_pos)
    if wiper_pos == 128: 
        R_unknown = 111 
    elif wiper_pos == 127:
        R_unknown = 183
    else:
        wiper_pos2 = 128 - wiper_pos
        R_unknown = ((wiper_pos2 + 1) * 70)
        
    lcd.setCursor(0, 1)
    lcd.printout(str(R_unknown) + " Ohms")
    wiper_pos = 0 

def button_pressed_callback(channel):
    print("inside callback event")
    if GPIO.input(button) == 1:
        print("detect a button press")
        res_val()

# Register the button event handler
GPIO.add_event_detect(button, GPIO.RISING, callback=button_pressed_callback, bouncetime=10)

try:
    while True:
        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()

    




    

    
    



