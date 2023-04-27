import sys
import time 
import pigpio
import RPi.GPIO as GPIO
import time
import rgb1602

lcd = rgb1602.RGB1602(16,2)
lcd.setRGB(0,128,128)

#initialize pigpio
pi = pigpio.pi()

#set the pin to use
PWM_PIN = 12

#for the rotary encocder 
clk = 17
dt = 18

#pins are set to BCM mode   
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#initialize the frequency, and also keep track of the last time the rotary encoder was rotated
currentFreq = 100
last_rotation_time = time.time()
lcd.printout("hello")


#method will update the LCD screen with current frequency
def update_lcd():
    lcd.clear()
    lcd.write_string(f"Frequency: {currentFreq} Hz")
    

#callback for the rotary encoder. This method will be called every time the rotary encoder is rotated.
def rotary_callback(channel):
    global currentFreq, last_rotation_time
    dt_state = GPIO.input(dt)
    #each time the rotary encoder is rotated, the time will be updated
    now = time.time()

    #this block of code is to determine if the rotary encoder is being rotated fast or slow.
    #depedning on the speed, the frequency will be incremented or decremented by 10 or 100 Hz
    if GPIO.input(clk) != dt_state:
        if now - last_rotation_time >= 0.1:  # Slow rotation
            currentFreq = min(10000, currentFreq + 10)
        else:  # Fast rotation
            currentFreq = min(10000, currentFreq + 100)
        last_rotation_time = now
    else:
        if now - last_rotation_time >= 0.1:  # Slow rotation
            currentFreq = max(100, currentFreq - 10)
        else:  # Fast rotation
            currentFreq = max(100, currentFreq - 100)
        last_rotation_time = now
    update_lcd()
    
#set the frequency of the PWM signal. Using the pigpio library
#pigpio uses hardware PWM, which is more accurate than other software PWM libraries
def set_frequency(pin, freq):
    pi.set_mode(pin, pigpio.OUTPUT)
    frequency = int(freq)
    pi.hardware_PWM(pin, freq, 500000)  # frequency, duty cycle - 50 %
    print("Frequency set to {} Hz".format(frequency))


#main function will set up the encoder pins and use the rotary_callback method
def main():
    global currentFreq

    # Set up GPIO for rotary encoder
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    #event handler for the rotary encoder
    GPIO.add_event_detect(clk, GPIO.FALLING, callback=rotary_callback, bouncetime=2)
    
    try:
        while True:
            #passing the current frequency to the set_frequency method. This will update the PWM signal to the new frequency.
            set_frequency(PWM_PIN, currentFreq)
            time.sleep(1)
    #program will terminate if the user presses ctrl+c
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()
        pi.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
























