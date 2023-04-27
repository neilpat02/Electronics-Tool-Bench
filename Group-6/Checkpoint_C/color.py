import time
import RPi.GPIO as GPIO
import rgb1602

# Pin definitions for rotary encoder
CLOCKWISE = 17
COUNTER_CLOCKWISE = 18
BUTTON = 27

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLOCKWISE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(COUNTER_CLOCKWISE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# LCD object
lcd = rgb1602.RGB1602(16,2)

# Color selection
color_options = ["Red", "Blue", "Green"]
color_index = 0

# Display initial color selection
lcd.setCursor(0,0)
lcd.printout("Color: " + color_options[color_index])

# Function to change color selection
def change_color(direction):
    global color_index
    if direction == "Clockwise":
        color_index += 1
    elif direction == "CounterClockwise":
        color_index -= 1
    color_index = color_index % len(color_options)
    lcd.setCursor(0,7)
    lcd.printout(color_options[color_index])

# Function to handle rotary encoder inputs
def rotary_encoder_input(channel):
    if channel == CLOCKWISE:
        change_color("Clockwise")
    elif channel == COUNTER_CLOCKWISE:
        change_color("CounterClockwise")
    elif channel == BUTTON:
        lcd.setRGB(*[150 * int(i == color_options[color_index]) for i in ["Red","Green","Blue"]])

# Add event detection for rotary encoder inputs
GPIO.add_event_detect(CLOCKWISE, GPIO.FALLING, callback=rotary_encoder_input, bouncetime=100)
GPIO.add_event_detect(COUNTER_CLOCKWISE, GPIO.FALLING, callback=rotary_encoder_input, bouncetime=100)
GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=rotary_encoder_input, bouncetime=100)

# Keep the program running
try:
    while True:
        time.sleep(0.1)
       

# Clean up GPIO when the program exits
except KeyboardInterrupt:
    GPIO.cleanup()
