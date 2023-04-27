import RPi.GPIO as GPIO
import time
from rgb1602 import RGB1602

# set up the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

# create an instance of the RGB1602 class
lcd = RGB1602(rs=14, enable=15, d4=18, d5=23, d6=24, d7=25, cols=16, rows=2)

# set the background color to blue
lcd.set_color(0, 0, 255)

# set the text color to white
lcd.set_text_color(255, 255, 255)

# define the frequency and duration of the square wave
frequency = 100  # Hz
duration = 10    # seconds

# display the frequency on the LCD
lcd.display_string("Frequency: {}Hz".format(frequency), 1)

# generate the square wave and display it on the LCD
period = 1.0 / frequency
half_period = period / 2.0
num_cycles = int(duration / period)

for i in range(num_cycles):
    GPIO.output(18, GPIO.HIGH)
    time.sleep(half_period)
    GPIO.output(18, GPIO.LOW)
    time.sleep(half_period)

    # display the waveform on the LCD
    lcd.clear()
    lcd.display_string("Waveform:", 1)
    lcd.display_string("  __  " if i % 2 == 0 else " |  | ", 2)
    time.sleep(half_period)
