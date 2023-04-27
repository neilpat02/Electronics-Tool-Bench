import rgb1602
import RPi.GPIO as GPIO
import time

#rotary encoder intialization
clk = 17
dt = 18
btn = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lcd = rgb1602.RGB1602(16, 2)

# Initialize the counter. This will be incremented by the pulse function
counter = 0

# Define the pulse callback function, which increments the counter variable
def pulse(channel):
    global counter
    counter += 1


# Define the calcFreq function, which calculates and displays the frequency
def calcFreq():
    global counter
    counter = 0  # Reset the counter
    begin = time.time() # record the current time 

    lcd.clear() # lcd setup to output nicely formatted frequency
    lcd.setCursor(0, 0)
    lcd.printout("Freq:")
    lcd.setCursor(0, 1)

    GPIO.add_event_detect(16, GPIO.FALLING, callback=pulse)
    time.sleep(2)
    #GPIO.remove_event_detect(16)
    elapsed = time.time() - begin
    readFreq = (counter / elapsed) * 1.019
    lcd.clear()
    #GPIO.add_event_detect(16, GPIO.RISING, callback=pulse) # add the pulse callback function to the GPIO pin
    time.sleep(2) # wait 2 seconds
    elapsed = time.time() - begin # calculate the elapsed time
    readFreq = (counter / elapsed) * 1.029 # calculate the frequency with an offset of 0.029 accounted for for better accuracy 
    lcd.clear() # lcd setup to output nicely formatted frequency
    lcd.setCursor(0, 1)
    print(readFreq)
    lcd.printout(f"{int(readFreq)}Hz")
    #time.sleep(1)
    GPIO.remove_event_detect(16)

# Monitor the button state and call calcFreq when pressed
try:
    while True:
        if GPIO.input(btn) == 0:
            #time.sleep(0.3) # debounce the button
            calcFreq()
            #GPIO.remove_event_detect(16)
        #time.sleep(0.1)
        
except KeyboardInterrupt:
    GPIO.cleanup()
