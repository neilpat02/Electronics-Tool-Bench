
"""
import RPi.GPIO as GPIO
import time 

#A rotary enocder class is created
class RotaryEncoder:
    #creating a constructor 
    def __init__(self, encoder_pin, led_pin):
        self.encoder_pin = encoder_pin
        self.led_pin  = led_pin
        self.led_state = False
        #initializing and setting up encoder and led as input and output respectively 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.encoder_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.led_pin, GPIO.OUT)

        #event detection for the encoder pin for the purpose of detecting a change in the state of a rotary encoder.
        #based on the change state, a callback function is programmed to change the state of the led. 
        #basetime of 250 ms is created to prevent multiple callbacks in between intermediate events.
        GPIO.add_event_detect(self.encoder_pin, GPIO.RISING, callback = self.encoder_cb, bouncetime = 250)

    #encoder callback function that use 'not' logic operator to change the state of the led and then output the correct state to 
    #visualize the change,
    def encoder_cb(self, encoder_pin): 
        self.led_state = not self.led_state
        GPIO.output(self.led_pin, self.led_state)
    
    #simple function to end the program gracefully without running into any issues. 
    def cleanup(self):
        GPIO.cleanup()


#main function that initializes an instance of the RotaryEncoder class given the desired GPIO.  
def main(): 
    #try-catch = to ensure the program terminates gracefully, if the user desires to abruptly stop the program. 
    try:
        encode = RotaryEncoder(18,24)
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        encode.cleanup()

#main function is called to begin the program 
if __name__ == "__main__":
    main()
"""

import pigpio
import RPi.GPIO as GPIO
import time 

pi = pigpio.pi()

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(24,GPIO.OUT)

while True:
    if not pi.read(18):
        print(pi.read(18))
        GPIO.output(27,1)
    elif pi.read(18):
        print(pi.read(17))
        GPIO.output(27,