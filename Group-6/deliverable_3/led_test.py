import RPi.GPIO as GPIO
import time

# Use physical pin numbering
GPIO.setmode(GPIO.BCM)

# Set pin 17 as an output pin
LED_PIN = 18
GPIO.setup(LED_PIN, GPIO.OUT)

# Turn on the LED
GPIO.output(LED_PIN, GPIO.HIGH)

# Wait for 5 seconds
time.sleep(5)

# Turn off the LED
GPIO.output(LED_PIN, GPIO.LOW)

# Clean up
GPIO.cleanup()
