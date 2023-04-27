import RPi.GPIO as GPIO
import time
import rgb1602
import spidev

# Set up the RGB1602 display
lcd = rgb1602.RGB1602(16, 2)
lcd.setRGB(0,128,128)

lcd.printout("9934 Ohms")