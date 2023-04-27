import RPi.GPIO as GPIO
import time
import rgb1602
import spidev
import pigpio
import random
# Set up the pins
compOut = 5
comp = 6
compInt = 14
clk = 17
dt = 18
btn = 27
# Set up the PWM pin
PWM_PIN = 12
#initialize pigpio
pi = pigpio.pi()
cs = 7
pi.set_mode(cs, pigpio.OUTPUT)
readFreq = 0
# Set up the RGB1602 display
lcd = rgb1602.RGB1602(16,2)
lcd.setRGB(0,128,128) # Set the RGB color to teal
#setting up the rotary encoder and comparator output pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(comp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(compOut, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(compInt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN)
# Set up the RGB1602 display
lcd = rgb1602.RGB1602(16, 2)
lcd.setRGB(0,128,128)
# Set up the SPI interface
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000
spi.xfer2([0x10, 128])
spi2 = spidev.SpiDev()
spi2.open(0,1)
spi2.mode = 0
spi2.max_speed_hz = 1000000
spi2.xfer2([0x00,128])
voltVal = 0
#for the function generator, gave it a default value of 100 Hz
currentFreq = 100
currentFreq2 = 1000
desiredFreq = currentFreq
desiredFreq2 = currentFreq2
Amp = 2.5
#keep track of the last time the rotary encoder was rotated
last_rotation_time = time.time()

"""
The ohmmeter function will use the comparator output to determine the resistance of the unknown resistor.
We have characterized our digital potentiometer to have a resistance of 72 ohms per step. The initial resistance
of the potentiometer is 111 ohms. The comparator output will be high when the resistance of the unknown resistor
is greater than the resistance of the potentiometer. The comparator output will be low when the resistance of the
unknown resistor is less than the resistance of the potentiometer. The digital potentiometer will be adjusted
until the comparator output is low. The digital potentiometer will be adjusted by 1 step at a time. The resistance
of the unknown resistor will be calculated by multiplying the number of steps the potentiometer was adjusted by
72 ohms. The resistance of the unknown resistor will be displayed on the LCD screen.
"""
def ohmmeter():
    print("inside res val")
    global R_unknown
    val = True
    wiper_pos = 128
    spi.xfer2([0x10, wiper_pos])
    while GPIO.input(compOut) == 0:
        print(GPIO.input(compOut))
        time.sleep(0.01)
        spi.xfer2([0x10, wiper_pos])
        wiper_pos -= 1
        print("inside while loop: ", wiper_pos)
        if wiper_pos <= 0:
            break
    if wiper_pos == 128: 
        R_unknown = 111 
    elif wiper_pos == 127:
        R_unknown = 183
    elif wiper_pos <= 0:
        R_unknown = 9288
    else:
        wiper_pos2 = 128 - wiper_pos
        R_unknown = ((wiper_pos2 + 1) * 73)
    print(GPIO.input(compOut))     
    lcd.setCursor(0, 1)
    lcd.printout(str(R_unknown) + " Ohms")
    
"""
The two functions below are used for the function generator. The set_frequency function will set the frequency of the
square wave. The square_wave function will set the frequency of the square wave and turn the output on or off.
pigpio is used to set the frequency of the square wave.
"""
def set_frequency(pin, freq): 
    pi.set_mode(pin, pigpio.OUTPUT)
    frequency = int(freq)
    pi.hardware_PWM(pin, freq, 500000) 
    print("Frequency set to {} Hz".format(frequency)) #This is used for testing

def square_wave(freq, output_on):
    global getFreq
    #getFreq = currentFreq
    getFreq = desiredFreq
    print(f"Setting square wave frequency to {getFreq} Hz") #This is used for testing
    
    if output_on: #this if-statement will be invoked if the flag is set to True, indicating that the output should be on.
        set_frequency(PWM_PIN, getFreq)
    else: #this else-statement will be invoked if the flag is set to False, indicating that the output should be off, when the user presses the 'off', 'back', or 'main' button.
        set_frequency(PWM_PIN, 0)


"""
The following function is the adc function. The adc function will use the comparator output to determine the voltage
of the unknown voltage source. The digital potentiometer will be adjusted until the comparator output is low. The
digital potentiometer will be adjusted by 1 step at a time. The voltage of the unknown voltage source will be calculated
by multiplying the number of steps the potentiometer was adjusted by 0.25 volts. The voltage of the unknown voltage
source will be displayed on the LCD screen.
"""
def adc(arg = None):
    if arg == None: #if arg is None, then the function is able to take the measure the external voltage source.
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
    elif arg != None: #if the arg is not None, then the function will be able to set the digital potentiometer to a specific voltage, based on the internal voltage input.
        if arg == 0.25: #set to 0.25V
            spi.xfer2([0x00, 128])
        elif arg == 0.50: #set to 0.50V
            spi.xfer2([0x00, 127])
        elif arg == 0.75: #set to 0.75V
            spi.xfer2([0x00, 125])
        elif arg == 1.00: #set to 1.00V
            spi.xfer2([0x00, 123])
        elif arg == 1.25:  # set to 1.25V
            spi.xfer2([0x00, 121])
        elif arg == 1.50:  # set to 1.50V
            spi.xfer2([0x00, 119])
        elif arg == 1.75: # set to 1.75V
            spi.xfer2([0x00, 116])
        elif arg == 2.00: #set to 2.00V
            spi.xfer2([0x00, 113])
        elif arg == 2.25: #set to 2.25V
            spi.xfer2([0x00, 108])
        elif arg == 2.50: #set to 2.50V
            spi.xfer2([0x00, 104])
        elif arg == 2.75: #set to 2.75V
            spi.xfer2([0x00, 98])
        elif arg == 3.00: #set to 3.00V
            spi.xfer2([0x00, 91])
        elif arg == 3.25: #set to 3.25V
            spi.xfer2([0x00, 83])
        elif arg == 3.50: #set to 3.50V
            spi.xfer2([0x00, 72])
        elif arg == 3.75: #set to 3.75V
            spi.xfer2([0x00, 50])
        elif arg > 3.75: #if the voltage is greater than 3.75V, then the function will set the digital potentiometer to 3.75V, which is the maximum voltage that the digital potentiometer can handle.
            spi.xfer2([0x00,50])

#simple function to call the adc function and return the voltage which will be displayed on the LCD screen. 
def voltmeter():
    voltage = adc()
    return voltage

"""
the internal_ref function is used to set the digital potentiometer to a specific voltage, based on the internal voltage input.
the digitpot was characterized by testing the voltage output at each step of the digital potentiometer. Based on the voltage output, 
the digital potentiometer was set to the closest voltage to the internal voltage input.
"""
def internal_ref(val):
    global voltVal
    voltVal = val
    if voltVal == 0.25:
        spi2.xfer2([0x00, 128])
    elif voltVal == 0.50:
        spi2.xfer2([0x00,127])
    elif voltVal == 0.75:
        spi2.xfer2([0x00,125])
    elif voltVal == 1.00:
        spi2.xfer2([0x00,123])
    elif voltVal == 1.25:
        spi2.xfer2([0x00,121])
    elif voltVal == 1.50:
        spi2.xfer2([0x00,119])
    elif voltVal == 1.75:
        spi2.xfer2([0x00,116])
    elif voltVal == 2.00:
        spi2.xfer2([0x00,113])
    elif voltVal == 2.25:
        spi2.xfer2([0x00,109])
    elif voltVal == 2.50:
        spi2.xfer2([0x00,104])
    elif voltVal == 2.75:
        spi2.xfer2([0x00,98])
    elif voltVal == 3.00:
        spi2.xfer2([0x00,92])
    elif voltVal == 3.25:
        spi2.xfer2([0x00,84])
    elif voltVal == 3.50:
        spi2.xfer2([0x00,73])
    elif voltVal == 3.75:
        spi2.xfer2([0x00,56])
    elif voltVal == 4.00:
        spi2.xfer2([0x00,25])
    adc(voltVal)
    
# Initialize the counter. This will be incremented by the pulse function
global counter
counter = 0

# Define the pulse callback function, which increments the counter variable
def pulse(channel):
    global counter
    print(counter)
    counter += 1


# Define the calcFreq function, which calculates and displays the frequency
def calcFreq(pin):
    global counter, readFreq, current_menu
    counter = 0  # Reset the counter
    begin = time.time() # record the current time 

    lcd.clear() # lcd setup to output nicely formatted frequency
    lcd.setCursor(0, 0)
    lcd.printout("Freq:")
    lcd.setCursor(0, 1)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=pulse)
    time.sleep(2)
    GPIO.remove_event_detect(16)
    
    elapsed = time.time() - begin
    readFreq = (counter / elapsed) * 1.019
    
    lcd.clear()  # lcd setup to output nicely formatted frequency
    global externalFreqOptions
    externalFreqOptions[0] = f"Frequency: {int(readFreq)} Hz"
    current_menu = externalFreqOptions

    print(readFreq)
    
def amplitudeTable():
    global Amp, currentFreq2
    if 9800 <= currentFreq2 <= 10000:
        amp_map = {
            1: {"D1": 40, "D2": 0},
            1.25: {"D1": 27, "D2": 0},
            1.5: {"D1": 21, "D2": 0},
            1.75: {"D1": 18, "D2": 0},
            2: {"D1": 16, "D2": 0},
            2.25: {"D1": 13, "D2": 0},
            2.5: {"D1": 10, "D2": 0},
            2.75: {"D1": 9, "D2": 0},
            3: {"D1": 8, "D2": 0},
            3.25: {"D1": 7, "D2": 0},
            3.5: {"D1": 6, "D2": 0},
            3.75: {"D1": 6, "D2": 0},
            4: {"D1": 5, "D2": 0},
            4.25: {"D1": 4, "D2": 0},
            4.5: {"D1": 4, "D2": 0},
            4.75: {"D1": 4, "D2": 0},
            5: {"D1": 3, "D2": 0},
        }
        
    elif 9300 <= currentFreq2 <= 9400:
        amp_map = {
            1: {"D1": 49, "D2": 0},
            1.25: {"D1": 37, "D2": 0},
            1.5: {"D1": 29, "D2": 0},
            1.75: {"D1": 25, "D2": 0},
            2: {"D1": 19, "D2": 0},
            2.25: {"D1": 16, "D2": 0},
            2.5: {"D1": 14, "D2": 0},
            2.75: {"D1": 13, "D2": 0},
            3: {"D1": 12, "D2": 0},
            3.25: {"D1": 10, "D2": 0},
            3.5: {"D1": 9, "D2": 0},
            3.75: {"D1": 8, "D2": 0},
            4: {"D1": 7, "D2": 0},
            4.25: {"D1": 6, "D2": 0},
            4.5: {"D1": 5, "D2": 0},
            4.75: {"D1": 5, "D2": 0},
            5: {"D1": 4, "D2": 0},
        }
    
    elif 9500 <= currentFreq2 <= 9700:
        amp_map = {
            5:    {'D1': 3,  'D2': 0},
            4.75: {'D1': 4,  'D2': 0},
            4.5:  {'D1': 4,  'D2': 0},
            4.25: {'D1': 5,  'D2': 0},
            4:    {'D1': 6,  'D2': 0},
            3.75: {'D1': 6,  'D2': 0},
            3.5:  {'D1': 7,  'D2': 0},
            3.25: {'D1': 8,  'D2': 0},
            3:    {'D1': 9,  'D2': 0},
            2.75: {'D1': 12, 'D2': 0},
            2.5:  {'D1': 14, 'D2': 0},
            2.25: {'D1': 16, 'D2': 0},
            2:    {'D1': 17, 'D2': 0},
            1.75: {'D1': 22, 'D2': 0},
            1.5:  {'D1': 26, 'D2': 0},
            1.25: {'D1': 40, 'D2': 0},
            1:    {'D1': 50, 'D2': 0},
        }
    elif 8900 <= currentFreq2 <= 9200:
        amp_map = {
            5:    {'D1': 5,  'D2': 0},
            4.75: {'D1': 5,  'D2': 0},
            4.5:  {'D1': 6,  'D2': 0},
            4.25: {'D1': 6,  'D2': 0},
            4:    {'D1': 7,  'D2': 0},
            3.75: {'D1': 8,  'D2': 0},
            3.5:  {'D1': 9,  'D2': 0},
            3.25: {'D1': 10, 'D2': 0},
            3:    {'D1': 12, 'D2': 0},
            2.75: {'D1': 15, 'D2': 0},
            2.5:  {'D1': 18, 'D2': 0},
            2.25: {'D1': 18, 'D2': 0},
            2:    {'D1': 21, 'D2': 0},
            1.75: {'D1': 28, 'D2': 0},
            1.5:  {'D1': 32, 'D2': 0},
            1.25: {'D1': 45, 'D2': 0},
            1:    {'D1': 56, 'D2': 0},
        }
    elif 8500 <= currentFreq2 <= 8800:
        amp_map = {
            5:    {'D1': 6,  'D2': 0},
            4.75: {'D1': 6,  'D2': 0},
            4.5:  {'D1': 7,  'D2': 0},
            4.25: {'D1': 8,  'D2': 0},
            4:    {'D1': 9,  'D2': 0},
            3.75: {'D1': 10, 'D2': 0},
            3.5:  {'D1': 11, 'D2': 0},
            3.25: {'D1': 12, 'D2': 0},
            3:    {'D1': 13, 'D2': 0},
            2.75: {'D1': 16, 'D2': 0},
            2.5:  {'D1': 18, 'D2': 0},
            2.25: {'D1': 20, 'D2': 0},
            2:    {'D1': 26, 'D2': 0},
            1.75: {'D1': 30, 'D2': 0},
            1.5:  {'D1': 35, 'D2': 0},
            1.25: {'D1': 50, 'D2': 0},
            1:    {'D1': 64, 'D2': 0},
        }
    elif 8200 <= currentFreq2 <= 8400:
        amp_map = {
            5:    {'D1': 7,  'D2': 0},
            4.75: {'D1': 8,  'D2': 0},
            4.5:  {'D1': 8,  'D2': 0},
            4.25: {'D1': 9,  'D2': 0},
            4:    {'D1': 10, 'D2': 0},
            3.75: {'D1': 11, 'D2': 0},
            3.5:  {'D1': 12, 'D2': 0},
            3.25: {'D1': 14, 'D2': 0},
            3:    {'D1': 16, 'D2': 0},
            2.75: {'D1': 18, 'D2': 0},
            2.5:  {'D1': 20, 'D2': 0},
            2.25: {'D1': 23, 'D2': 0},
            2:    {'D1': 27, 'D2': 0},
            1.75: {'D1': 33, 'D2': 0},
            1.5:  {'D1': 39, 'D2': 0},
            1.25: {'D1': 55, 'D2': 0},
            1:    {'D1': 70, 'D2': 0},
        }
    elif 7800 <= currentFreq2 <= 8100:
        amp_map = {
            5:    {'D1': 8,  'D2': 0},
            4.75: {'D1': 9,  'D2': 0},
            4.5:  {'D1': 9,  'D2': 0},
            4.25: {'D1': 10, 'D2': 0},
            4:    {'D1': 12, 'D2': 0},
            3.75: {'D1': 13, 'D2': 0},
            3.5:  {'D1': 14, 'D2': 0},
            3.25: {'D1': 16, 'D2': 0},
            3:    {'D1': 18, 'D2': 0},
            2.75: {'D1': 21, 'D2': 0},
            2.5:  {'D1': 23, 'D2': 0},
            2.25: {'D1': 27, 'D2': 0},
            2:    {'D1': 31, 'D2': 0},
            1.75: {'D1': 36, 'D2': 0},
            1.5:  {'D1': 43, 'D2': 0},
            1.25: {'D1': 68, 'D2': 0},
            1:    {'D1': 80, 'D2': 0},
        }
    elif 7500 <= currentFreq2 <= 7700:
        amp_map = {
            5:    {'D1': 10, 'D2': 0},
            4.75: {'D1': 10, 'D2': 0},
            4.5:  {'D1': 11, 'D2': 0},
            4.25: {'D1': 12, 'D2': 0},
            4:    {'D1': 14, 'D2': 0},
            3.75: {'D1': 15, 'D2': 0},
            3.5:  {'D1': 16, 'D2': 0},
            3.25: {'D1': 19, 'D2': 0},
            3:    {'D1': 21, 'D2': 0},
            2.75: {'D1': 24, 'D2': 0},
            2.5:  {'D1': 28, 'D2': 0},
            2.25: {'D1': 31, 'D2': 0},
            2:    {'D1': 35, 'D2': 0},
            1.75: {'D1': 43, 'D2': 0},
            1.5:  {'D1': 49, 'D2': 0},
            1.25: {'D1': 74, 'D2': 0},
            1:    {'D1': 90, 'D2': 0},
        }
    elif 7100 <= currentFreq2 <= 7400:
        amp_map = {
            5:    {'D1': 11, 'D2': 0},
            4.75: {'D1': 12, 'D2': 0},
            4.5:  {'D1': 13, 'D2': 0},
            4.25: {'D1': 14, 'D2': 0},
            4:    {'D1': 15, 'D2': 0},
            3.75: {'D1': 17, 'D2': 0},
            3.5:  {'D1': 19, 'D2': 0},
            3.25: {'D1': 21, 'D2': 0},
            3:    {'D1': 24, 'D2': 0},
            2.75: {'D1': 28, 'D2': 0},
            2.5:  {'D1': 33, 'D2': 0},
            2.25: {'D1': 36, 'D2': 0},
            2:    {'D1': 40, 'D2': 0},
            1.75: {'D1': 46, 'D2': 0},
            1.5:  {'D1': 55, 'D2': 0},
            1.25: {'D1': 79, 'D2': 0},
            1:    {'D1': 100, 'D2': 0},
        }
    elif 6700 <= currentFreq2 <= 7000:
        amp_map = {
            5:    {'D1': 14, 'D2': 0},
            4.75: {'D1': 14, 'D2': 0},
            4.5:  {'D1': 15, 'D2': 0},
            4.25: {'D1': 16, 'D2': 0},
            4:    {'D1': 18, 'D2': 0},
            3.75: {'D1': 20, 'D2': 0},
            3.5:  {'D1': 22, 'D2': 0},
            3.25: {'D1': 24, 'D2': 0},
            3:    {'D1': 26, 'D2': 0},
            2.75: {'D1': 29, 'D2': 0},
            2.5:  {'D1': 32, 'D2': 0},
            2.25: {'D1': 43, 'D2': 0},
            2:    {'D1': 50, 'D2': 0},
            1.75: {'D1': 60, 'D2': 0},
            1.5:  {'D1': 70, 'D2': 0},
            1.25: {'D1': 80, 'D2': 0},
            1:    {'D1': 110, 'D2': 0},
        }
    elif 6500 <= currentFreq2 <= 6600:
        amp_map = {
            5:    {'D1': 14,  'D2': 0},
            4.75: {'D1': 15,  'D2': 0},
            4.5:  {'D1': 16,  'D2': 0},
            4.25: {'D1': 17,  'D2': 0},
            4:    {'D1': 20,  'D2': 0},
            3.75: {'D1': 23,  'D2': 0},
            3.5:  {'D1': 25,  'D2': 0},
            3.25: {'D1': 28,  'D2': 0},
            3:    {'D1': 31,  'D2': 0},
            2.75: {'D1': 36,  'D2': 0},
            2.5:  {'D1': 38,  'D2': 0},
            2.25: {'D1': 42,  'D2': 0},
            2:    {'D1': 49,  'D2': 0},
            1.75: {'D1': 59,  'D2': 0},
            1.5:  {'D1': 73,  'D2': 0},
            1.25: {'D1': 95,  'D2': 0},
            1:    {'D1': 118, 'D2': 0},
        }
    elif 6100 <= currentFreq2 <= 6400:
        amp_map = {
            5:    {'D1': 16, 'D2': 0},
            4.75: {'D1': 17, 'D2': 0},
            4.5:  {'D1': 19, 'D2': 0},
            4.25: {'D1': 20, 'D2': 0},
            4:    {'D1': 22, 'D2': 0},
            3.75: {'D1': 24, 'D2': 0},
            3.5:  {'D1': 26, 'D2': 0},
            3.25: {'D1': 29, 'D2': 0},
            3:    {'D1': 33, 'D2': 0},
            2.75: {'D1': 36, 'D2': 0},
            2.5:  {'D1': 40, 'D2': 0},
            2.25: {'D1': 46, 'D2': 0},
            2:    {'D1': 52, 'D2': 0},
            1.75: {'D1': 65, 'D2': 0},
            1.5:  {'D1': 79, 'D2': 0},
            1.25: {'D1': 100, 'D2': 0},
            1:    {'D1': 128, 'D2': 0},
        }
    elif 5800 <= currentFreq2 <= 6000:
        amp_map = {
            5:    {'D1': 18, 'D2': 0},
            4.75: {'D1': 19, 'D2': 0},
            4.5:  {'D1': 21, 'D2': 0},
            4.25: {'D1': 23, 'D2': 0},
            4:    {'D1': 24, 'D2': 0},
            3.75: {'D1': 27, 'D2': 0},
            3.5:  {'D1': 30, 'D2': 0},
            3.25: {'D1': 32, 'D2': 0},
            3:    {'D1': 37, 'D2': 0},
            2.75: {'D1': 41, 'D2': 0},
            2.5:  {'D1': 46, 'D2': 0},
            2.25: {'D1': 52, 'D2': 0},
            2:    {'D1': 59, 'D2': 0},
            1.75: {'D1': 75, 'D2': 0},
            1.5:  {'D1': 90, 'D2': 0},
            1.25: {'D1': 112, 'D2': 0},
            1:    {'D1': 128, 'D2': 0},
        }
    elif 5500 <= currentFreq2 <= 5700:
        amp_map = {
            5:    {'D1': 19, 'D2': 0},
            4.75: {'D1': 21, 'D2': 0},
            4.5:  {'D1': 23, 'D2': 0},
            4.25: {'D1': 25, 'D2': 0},
            4:    {'D1': 27, 'D2': 0},
            3.75: {'D1': 30, 'D2': 0},
            3.5:  {'D1': 33, 'D2': 0},
            3.25: {'D1': 36, 'D2': 0},
            3:    {'D1': 39, 'D2': 0},
            2.75: {'D1': 44, 'D2': 0},
            2.5:  {'D1': 48, 'D2': 0},
            2.25: {'D1': 55, 'D2': 0},
            2:    {'D1': 64, 'D2': 0},
            1.75: {'D1': 80, 'D2': 0},
            1.5:  {'D1': 97, 'D2': 0},
            1.25: {'D1': 120, 'D2': 0},
            1:    {'D1': 128, 'D2': 0},
        }
    elif 5200 <= currentFreq2 <= 5400:
       amp_map = {
            5:    {'D1': 6, 'D2': 10},
            4.75: {'D1': 6, 'D2': 10},
            4.5:  {'D1': 7, 'D2': 10},
            4.25: {'D1': 8, 'D2': 10},
            4:    {'D1': 8, 'D2': 10},
            3.75: {'D1': 10, 'D2': 10},
            3.5:  {'D1': 11, 'D2': 10},
            3.25: {'D1': 12, 'D2': 10},
            3:    {'D1': 14, 'D2': 10},
            2.75: {'D1': 15, 'D2': 10},
            2.5:  {'D1': 18, 'D2': 10},
            2.25: {'D1': 22, 'D2': 10},
            2:    {'D1': 25, 'D2': 10},
            1.75: {'D1': 29, 'D2': 10},
            1.5:  {'D1': 35, 'D2': 10},
            1.25: {'D1': 50, 'D2': 10},
            1:    {'D1': 62, 'D2': 10},
        }
    elif 4900 <= currentFreq2 <= 5100:
        amp_map = {
            5:    {'D1': 7, 'D2': 10},
            4.75: {'D1': 8, 'D2': 10},
            4.5:  {'D1': 8, 'D2': 10},
            4.25: {'D1': 9, 'D2': 10},
            4:    {'D1': 10, 'D2': 10},
            3.75: {'D1': 11, 'D2': 10},
            3.5:  {'D1': 13, 'D2': 10},
            3.25: {'D1': 15, 'D2': 10},
            3:    {'D1': 17, 'D2': 10},
            2.75: {'D1': 19, 'D2': 10},
            2.5:  {'D1': 22, 'D2': 10},
            2.25: {'D1': 26, 'D2': 10},
            2:    {'D1': 30, 'D2': 10},
            1.75: {'D1': 34, 'D2': 10},
            1.5:  {'D1': 40, 'D2': 10},
            1.25: {'D1': 55, 'D2': 10},
            1:    {'D1': 74, 'D2': 10},
        }
    elif 4600 <= currentFreq2 <= 4800:
        amp_map = {
            5:    {'D1': 9, 'D2': 10},
            4.75: {'D1': 9, 'D2': 10},
            4.5:  {'D1': 10, 'D2': 10},
            4.25: {'D1': 11, 'D2': 10},
            4:    {'D1': 12, 'D2': 10},
            3.75: {'D1': 14, 'D2': 10},
            3.5:  {'D1': 15, 'D2': 10},
            3.25: {'D1': 17, 'D2': 10},
            3:    {'D1': 19, 'D2': 10},
            2.75: {'D1': 22, 'D2': 10},
            2.5:  {'D1': 25, 'D2': 10},
            2.25: {'D1': 29, 'D2': 10},
            2:    {'D1': 34, 'D2': 10},
            1.75: {'D1': 40, 'D2': 10},
            1.5:  {'D1': 48, 'D2': 10},
            1.25: {'D1': 63, 'D2': 10},
            1:    {'D1': 82, 'D2': 10},
        }
    elif 4300 <= currentFreq2 <= 4500:
        amp_map = {
            5:    {'D1': 11, 'D2': 10},
            4.75: {'D1': 11, 'D2': 10},
            4.5:  {'D1': 12, 'D2': 10},
            4.25: {'D1': 14, 'D2': 10},
            4:    {'D1': 15, 'D2': 10},
            3.75: {'D1': 17, 'D2': 10},
            3.5:  {'D1': 18, 'D2': 10},
            3.25: {'D1': 20, 'D2': 10},
            3:    {'D1': 22, 'D2': 10},
            2.75: {'D1': 27, 'D2': 10},
            2.5:  {'D1': 30, 'D2': 10},
            2.25: {'D1': 34, 'D2': 10},
            2:    {'D1': 40, 'D2': 10},
            1.75: {'D1': 46, 'D2': 10},
            1.5:  {'D1': 58, 'D2': 10},
            1.25: {'D1': 72, 'D2': 10},
            1:    {'D1': 94, 'D2': 10},
        }
    elif 4000 <= currentFreq2 <= 4200:
        amp_map = {
            5:    {'D1': 13, 'D2': 10},
            4.75: {'D1': 14, 'D2': 10},
            4.5:  {'D1': 15, 'D2': 10},
            4.25: {'D1': 16, 'D2': 10},
            4:    {'D1': 18, 'D2': 10},
            3.75: {'D1': 20, 'D2': 10},
            3.5:  {'D1': 22, 'D2': 10},
            3.25: {'D1': 24, 'D2': 10},
            3:    {'D1': 27, 'D2': 10},
            2.75: {'D1': 32, 'D2': 10},
            2.5:  {'D1': 35, 'D2': 10},
            2.25: {'D1': 42, 'D2': 10},
            2:    {'D1': 47, 'D2': 10},
            1.75: {'D1': 58, 'D2': 10},
            1.5:  {'D1': 68, 'D2': 10},
            1.25: {'D1': 90, 'D2': 10},
            1:    {'D1': 112, 'D2': 10},
        }
    elif 3800 <= currentFreq2 <= 3900:
        amp_map = {
            5:    {'D1': 16, 'D2': 10},
            4.75: {'D1': 17, 'D2': 10},
            4.5:  {'D1': 18, 'D2': 10},
            4.25: {'D1': 20, 'D2': 10},
            4:    {'D1': 21, 'D2': 10},
            3.75: {'D1': 24, 'D2': 10},
            3.5:  {'D1': 26, 'D2': 10},
            3.25: {'D1': 29, 'D2': 10},
            3:    {'D1': 32, 'D2': 10},
            2.75: {'D1': 40, 'D2': 10},
            2.5:  {'D1': 42, 'D2': 10},
            2.25: {'D1': 46, 'D2': 10},
            2:    {'D1': 60, 'D2': 10},
            1.75: {'D1': 72, 'D2': 10},
            1.5:  {'D1': 85, 'D2': 10},
            1.25: {'D1': 99, 'D2': 10},
            1:    {'D1': 128, 'D2': 10},
        }
    elif 3500 <= currentFreq2 <= 3700:
        amp_map = {
            5:    {'D1': 8, 'D2': 20},
            4.75: {'D1': 9, 'D2': 20},
            4.5:  {'D1': 10, 'D2': 20},
            4.25: {'D1': 11, 'D2': 20},
            4:    {'D1': 12, 'D2': 20},
            3.75: {'D1': 14, 'D2': 20},
            3.5:  {'D1': 15, 'D2': 20},
            3.25: {'D1': 17, 'D2': 20},
            3:    {'D1': 19, 'D2': 20},
            2.75: {'D1': 23, 'D2': 20},
            2.5:  {'D1': 26, 'D2': 20},
            2.25: {'D1': 30, 'D2': 20},
            2:    {'D1': 35, 'D2': 20},
            1.75: {'D1': 41, 'D2': 20},
            1.5:  {'D1': 45, 'D2': 20},
            1.25: {'D1': 65, 'D2': 20},
            1:    {'D1': 83, 'D2': 20},
        }
    elif 3200 <= currentFreq2 <= 3400:
        amp_map = {
            5:    {'D1': 11, 'D2': 20},
            4.75: {'D1': 12, 'D2': 20},
            4.5:  {'D1': 13, 'D2': 20},
            4.25: {'D1': 14, 'D2': 20},
            4:    {'D1': 16, 'D2': 20},
            3.75: {'D1': 18, 'D2': 20},
            3.5:  {'D1': 20, 'D2': 20},
            3.25: {'D1': 22, 'D2': 20},
            3:    {'D1': 25, 'D2': 20},
            2.75: {'D1': 28, 'D2': 20},
            2.5:  {'D1': 31, 'D2': 20},
            2.25: {'D1': 36, 'D2': 20},
            2:    {'D1': 44, 'D2': 20},
            1.75: {'D1': 54, 'D2': 20},
            1.5:  {'D1': 65, 'D2': 20},
            1.25: {'D1': 79, 'D2': 20},
            1:    {'D1': 108, 'D2': 20},
        }
    elif 2900 <= currentFreq2 <= 3100:
        amp_map = {
            5:    {'D1': 14, 'D2': 20},
            4.75: {'D1': 15, 'D2': 20},
            4.5:  {'D1': 17, 'D2': 20},
            4.25: {'D1': 19, 'D2': 20},
            4:    {'D1': 21, 'D2': 20},
            3.75: {'D1': 23, 'D2': 20},
            3.5:  {'D1': 25, 'D2': 20},
            3.25: {'D1': 27, 'D2': 20},
            3:    {'D1': 32, 'D2': 20},
            2.75: {'D1': 36, 'D2': 20},
            2.5:  {'D1': 40, 'D2': 20},
            2.25: {'D1': 47, 'D2': 20},
            2:    {'D1': 53, 'D2': 20},
            1.75: {'D1': 65, 'D2': 20},
            1.5:  {'D1': 80, 'D2': 20},
            1.25: {'D1': 107, 'D2': 20},
            1:    {'D1': 128, 'D2': 20},
        }
    elif 2600 <= currentFreq2 <= 2800:
        amp_map = {
            5:    {'D1': 3,  'D2': 50},
            4.75: {'D1': 3,  'D2': 50},
            4.5:  {'D1': 5,  'D2': 50},
            4.25: {'D1': 6,  'D2': 50},
            4:    {'D1': 7,  'D2': 50},
            3.75: {'D1': 8,  'D2': 50},
            3.5:  {'D1': 10, 'D2': 50},
            3.25: {'D1': 11, 'D2': 50},
            3:    {'D1': 14, 'D2': 50},
            2.75: {'D1': 16, 'D2': 50},
            2.5:  {'D1': 18, 'D2': 50},
            2.25: {'D1': 21, 'D2': 50},
            2:    {'D1': 26, 'D2': 50},
            1.75: {'D1': 33, 'D2': 50},
            1.5:  {'D1': 40, 'D2': 50},
            1.25: {'D1': 50, 'D2': 50},
            1:    {'D1': 70, 'D2': 50},
        }
    elif 2300 <= currentFreq2 <= 2500:
        amp_map = {
            5:    {'D1': 6,  'D2': 50},
            4.75: {'D1': 6,  'D2': 50},
            4.5:  {'D1': 8,  'D2': 50},
            4.25: {'D1': 9,  'D2': 50},
            4:    {'D1': 11, 'D2': 50},
            3.75: {'D1': 12, 'D2': 50},
            3.5:  {'D1': 14, 'D2': 50},
            3.25: {'D1': 16, 'D2': 50},
            3:    {'D1': 19, 'D2': 50},
            2.75: {'D1': 21, 'D2': 50},
            2.5:  {'D1': 25, 'D2': 50},
            2.25: {'D1': 27, 'D2': 50},
            2:    {'D1': 32, 'D2': 50},
            1.75: {'D1': 42, 'D2': 50},
            1.5:  {'D1': 50, 'D2': 50},
            1.25: {'D1': 62, 'D2': 50},
            1:    {'D1': 87, 'D2': 50},
        }
    elif 2100 <= currentFreq2 <= 2200:
        amp_map = {
            5:    {'D1': 9,   'D2': 50},
            4.75: {'D1': 10,  'D2': 50},
            4.5:  {'D1': 11,  'D2': 50},
            4.25: {'D1': 13,  'D2': 50},
            4:    {'D1': 15,  'D2': 50},
            3.75: {'D1': 17,  'D2': 50},
            3.5:  {'D1': 19,  'D2': 50},
            3.25: {'D1': 22,  'D2': 50},
            3:    {'D1': 25,  'D2': 50},
            2.75: {'D1': 29,  'D2': 50},
            2.5:  {'D1': 32,  'D2': 50},
            2.25: {'D1': 37,  'D2': 50},
            2:    {'D1': 45,  'D2': 50},
            1.75: {'D1': 55,  'D2': 50},
            1.5:  {'D1': 67,  'D2': 50},
            1.25: {'D1': 88,  'D2': 50},
            1:    {'D1': 112, 'D2': 50},
        }

    elif 1800 <= currentFreq2 <= 2000:
        amp_map = {
            5:    {'D1': 4,  'D2': 80},
            4.75: {'D1': 5,  'D2': 80},
            4.5:  {'D1': 6,  'D2': 80},
            4.25: {'D1': 7,  'D2': 80},
            4:    {'D1': 9,  'D2': 80},
            3.75: {'D1': 11, 'D2': 80},
            3.5:  {'D1': 13, 'D2': 80},
            3.25: {'D1': 15, 'D2': 80},
            3:    {'D1': 18, 'D2': 80},
            2.75: {'D1': 24, 'D2': 80},
            2.5:  {'D1': 28, 'D2': 80},
            2.25: {'D1': 32, 'D2': 80},
            2:    {'D1': 37, 'D2': 80},
            1.75: {'D1': 46, 'D2': 80},
            1.5:  {'D1': 54, 'D2': 80},
            1.25: {'D1': 71, 'D2': 80},
            1:    {'D1': 89, 'D2': 80},
        }
    elif 1600 <= currentFreq2 <= 1700:
        amp_map = {
            5:    {'D1': 7,   'D2': 80},
            4.75: {'D1': 8,   'D2': 80},
            4.5:  {'D1': 10,  'D2': 80},
            4.25: {'D1': 12,  'D2': 80},
            4:    {'D1': 15,  'D2': 80},
            3.75: {'D1': 16,  'D2': 80},
            3.5:  {'D1': 19,  'D2': 80},
            3.25: {'D1': 22,  'D2': 80},
            3:    {'D1': 26,  'D2': 80},
            2.75: {'D1': 30,  'D2': 80},
            2.5:  {'D1': 35,  'D2': 80},
            2.25: {'D1': 40,  'D2': 80},
            2:    {'D1': 49,  'D2': 80},
            1.75: {'D1': 59,  'D2': 80},
            1.5:  {'D1': 71,  'D2': 80},
            1.25: {'D1': 95,  'D2': 80},
            1:    {'D1': 120, 'D2': 80},
        }
    elif 1400 <= currentFreq2 <= 1500:
        amp_map = {
            5:    {'D1': 3,   'D2': 110},
            4.75: {'D1': 4,   'D2': 110},
            4.5:  {'D1': 6,   'D2': 110},
            4.25: {'D1': 8,   'D2': 110},
            4:    {'D1': 10,  'D2': 110},
            3.75: {'D1': 12,  'D2': 110},
            3.5:  {'D1': 15,  'D2': 110},
            3.25: {'D1': 18,  'D2': 110},
            3:    {'D1': 22,  'D2': 110},
            2.75: {'D1': 26,  'D2': 110},
            2.5:  {'D1': 30,  'D2': 110},
            2.25: {'D1': 35,  'D2': 110},
            2:    {'D1': 42,  'D2': 110},
            1.75: {'D1': 52,  'D2': 110},
            1.5:  {'D1': 65,  'D2': 110},
            1.25: {'D1': 84,  'D2': 110},
            1:    {'D1': 112, 'D2': 110},
        }
    elif currentFreq2 == 1300:
        amp_map = {
            5:    {'D1': 3,   'D2': 128},
            4.75: {'D1': 5,   'D2': 128},
            4.5:  {'D1': 7,   'D2': 128},
            4.25: {'D1': 8,   'D2': 128},
            4:    {'D1': 10,  'D2': 128},
            3.75: {'D1': 12,  'D2': 128},
            3.5:  {'D1': 15,  'D2': 128},
            3.25: {'D1': 18,  'D2': 128},
            3:    {'D1': 22,  'D2': 128},
            2.75: {'D1': 26,  'D2': 128},
            2.5:  {'D1': 30,  'D2': 128},
            2.25: {'D1': 35,  'D2': 128},
            2:    {'D1': 42,  'D2': 128},
            1.75: {'D1': 52,  'D2': 128},
            1.5:  {'D1': 65,  'D2': 128},
            1.25: {'D1': 84,  'D2': 128},
            1:    {'D1': 112, 'D2': 128},
        }
    elif currentFreq2 == 1200:
        amp_map = {
            5:    {'D1': 5,   'D2': 128},
            4.75: {'D1': 8,   'D2': 128},
            4.5:  {'D1': 10,  'D2': 128},
            4.25: {'D1': 12,  'D2': 128},
            4:    {'D1': 15,  'D2': 128},
            3.75: {'D1': 20,  'D2': 128},
            3.5:  {'D1': 24,  'D2': 128},
            3.25: {'D1': 26,  'D2': 128},
            3:    {'D1': 32,  'D2': 128},
            2.75: {'D1': 40,  'D2': 128},
            2.5:  {'D1': 45,  'D2': 128},
            2.25: {'D1': 50,  'D2': 128},
            2:    {'D1': 59,  'D2': 128},
            1.75: {'D1': 75,  'D2': 128},
            1.5:  {'D1': 95,  'D2': 128},
            1.25: {'D1': 112, 'D2': 128},
            1:    {'D1': 128, 'D2': 128},
        }
    elif currentFreq2 == 1100:
        amp_map = {
            5:    {'D1': 57,  'D2': 57},
            4.75: {'D1': 59,  'D2': 59},
            4.5:  {'D1': 61,  'D2': 61},
            4.25: {'D1': 64,  'D2': 64},
            4:    {'D1': 68,  'D2': 68},
            3.75: {'D1': 70,  'D2': 70},
            3.5:  {'D1': 73,  'D2': 73},
            3.25: {'D1': 76,  'D2': 76},
            3:    {'D1': 81,  'D2': 81},
            2.75: {'D1': 85,  'D2': 85},
            2.5:  {'D1': 90,  'D2': 90},
            2.25: {'D1': 95,  'D2': 95},
            2:    {'D1': 100, 'D2': 100},
            1.75: {'D1': 110, 'D2': 110},
            1.5:  {'D1': 119, 'D2': 119},
            1.25: {'D1': 128, 'D2': 128},
            1:    {'D1': 128, 'D2': 128},
        }
    elif currentFreq2 == 1000:
        amp_map = {
            5:    {'D1': 62,  'D2': 62},
            4.75: {'D1': 66,  'D2': 66},
            4.5:  {'D1': 68,  'D2': 68},
            4.25: {'D1': 71,  'D2': 71},
            4:    {'D1': 75,  'D2': 75},
            3.75: {'D1': 80,  'D2': 80},
            3.5:  {'D1': 83,  'D2': 83},
            3.25: {'D1': 86,  'D2': 86},
            3:    {'D1': 88,  'D2': 88},
            2.75: {'D1': 94,  'D2': 94},
            2.5:  {'D1': 96,  'D2': 96},
            2.25: {'D1': 102,  'D2': 102},
            2:    {'D1': 112, 'D2': 112},
            1.75: {'D1': 119, 'D2': 119},
            1.5:  {'D1': 125, 'D2': 125},
            1.25: {'D1': 128, 'D2': 128},
            1:    {'D1': 128, 'D2': 128},
        }
    amp_vals = amp_map[Amp]
    sine(amp_vals["D1"], amp_vals["D2"])
    

def sine(d1, d2):
    global currentFreq2, Amp
    pi.write(cs, 0)
    spi.open(0,1)
    spi.max_speed_hz = 1000000
    spi.xfer2([0x00, d1])
    spi.xfer2([0x10, d2])

    pi.hardware_PWM(13, currentFreq2, 500000)
"""
All of the following are UI menu's. They will be passed into a variable called current_menu. The current_menu variable will
be used to determine which menu is currently being displayed on the LCD screen. The current_selection variable will be used
to determine which option is currently selected. 
"""
mainOptions = ["Select Mode", "Color Change", "OFF"]
colorChange = ["Random", "Back", "Main"]
selectionOptions = ["Function Generator", "Ohmmeter", "Voltmeter", "DC Reference", "Freq. Measure.", "Back", "Main"]
modeOptions = ["Type", "Frequency", "Amplitude", "Output"]
amplitudeOptions = ["5 Volts", "Back", "Main"]
amplitudeOptionsSine = ["Ampli: {Amp}", "Back", "Main"]
fgTypeOptions = ["Square", "Sine", "Back", "Main"]
fgFreqOptions = [f"Freq: {currentFreq} Hz", "Back", "Main"]
fgAmpOptions = ["Input Amplitude", "Back", "Main"]
outputOptions = ["On", "Off", "Back", "Main"]
newFgOptions = []
global newOhmmeterOptions #new screen after the unknown resistance is calculated
global newOutputOptions #new screen after the output is turned on or off
global newVoltmeterOptions #new screen after the voltage is measured
global voltageSetOptions #new screen after the voltage is set
global externalFreqOptions
externalFreqOptions = ["Frequency: 0 Hz", "Back", "Main"]
voltageSetOptions = ["", "Back", "Main"]
newVoltmeterOptions = []
new_menu = []
newOutputOptions = []
newFgOptionsSine = []
ampSineMenu = []
newOhmmeterOptions = ["--", "Back", "Main"]
ohmmeterOptions = ["XXX ohms", "Back", "Main"]
vm = ["Source"]
vmSrcOptions = ["External", "Internal Reference", "Back", "Main"]
dcReference = ["Voltage Value Input", "Output", "Back", "Main"]
dcOutputOptions = ["DC On", "DC Off", "DC Back", "DC Main"]
voltageInputOptions = ["Set Voltage: 0.00 V", "Back", "Main"]
frequencyMeasurement = ["External", "Internal", "Back", "Main"]
flag = ""
current_menu = mainOptions
current_selection = 0

"""
The button_callback function will be called when the rotary encoder is rotated or the button is pressed. The function will
determine which menu is currently being displayed on the LCD screen. The function will also determine which option is currently
selected. The function will then determine what to do based on the current menu and the current selection. 
"""
def button_callback(channel):
    global current_selection, current_menu, flag
    print(current_menu)
    print(flag)
    if current_menu == mainOptions: #Main menu
        print("inside mainOptions") #test line
        if current_selection == 0: #Select Mode
            current_menu = selectionOptions #the new menu on the LCD screen is now selectionOptions
            current_selection = 0
        elif current_selection == 1: #random color change
            current_menu = colorChange 
            current_selection = 0
        elif current_selection == 2: #OFF
            lcd.clear()
            lcd.setRGB(0,0,0)
            GPIO.cleanup()
            exit()
    elif current_menu == colorChange:
        if current_selection == 0: #randomly change the color
            if GPIO.input(btn) == 0:
                r = random.randint(0,255)
                g = random.randint(0,255)
                b = random.randint(0,255)
                lcd.setRGB(r,g,b)
            current_selection = 0
        elif current_selection == 1: # back
            current_menu = mainOptions
            current_selection = 0
        elif current_selection == 2: #main
            current_menu = mainOptions
            current_selection = 0 
    elif current_menu == selectionOptions: #this is the selectionOptions menu, being displayed on the screen 
        if current_selection == 0: #function generator selected
            current_menu = modeOptions
            current_selection = 0
        elif current_selection == 1: #ohmmeter selected
            current_menu = ohmmeterOptions
            current_selection = 0
        elif current_selection == 2: #voltmeter selected
            current_menu = vm
            current_selection = 0
        elif current_selection == 3: #dc reference selected
            current_menu = dcReference
            current_selection = 0
        elif current_selection == 4: #frequency measurement selected
            current_menu = frequencyMeasurement
            current_selection = 0
        elif current_selection == 5: #back selected
            current_menu = mainOptions
            current_selection = 0
        elif current_selection == 6: #main menu selected
            current_menu = mainOptions
            current_selection = 0
            
    #********************* function generator - all submenu's
    elif current_menu == modeOptions: # function generator
        print("inside modeOptions")
        if current_selection == 0: #type selected
            current_menu = fgTypeOptions
            current_selection = 0
        elif current_selection == 1: #freq selected
            current_menu = fgFreqOptions
            current_selection = 0
        elif current_selection == 2: #amplitude selected
            current_menu = fgAmpOptions
            current_selection = 0
        elif current_selection == 3: #output selected
            current_menu = outputOptions
            current_selection = 0
    elif current_menu == fgTypeOptions: #type
        if current_selection == 0: #square selected
            current_menu = modeOptions
            flag = "square"
            current_selection = 0
        elif current_selection == 1:
            current_menu = modeOptions
            flag = "sine"
            current_selection = 0
        elif current_selection == 2: #back selected
            current_menu = modeOptions
            current_selection = 0
        elif current_selection == 3: #main selected
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == fgFreqOptions: #frequency
        if current_selection == 0: #Input Frequency selected
            current_menu = fgFreqOptions
            if GPIO.input(btn) == 0: #if the button is pressed
                if flag == "square":
                    global desiredFreq
                    desiredFreq = currentFreq
                    #square_wave()
                    freqString = str(desiredFreq) + " Hz" #converts the desired frequency to a string
                    global newFgOptions #new screen after the frequency is set
                    newFgOptions = [freqString, "Back", "Main"]
                    current_menu = newFgOptions #the new menu on the LCD screen is now newFgOptions
                elif flag == "sine":
                    if GPIO.input(btn) == 0:
                        global desiredFreq2
                        desiredFreq2 = currentFreq2
                        freqString2 = str(desiredFreq2) + " Hz"
                        global newFgOptionsSine
                        newFgOptionsSine = [freqString2, "Back", "Main"]
                        current_menu = newFgOptionsSine
            current_selection = 0
        elif current_selection == 1: #back selected
            current_menu = modeOptions
            current_selection = 0
        elif current_selection == 2: #main selected
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == fgAmpOptions: #amplitude 
        if current_selection == 0: # Input Amplitude
            if flag == "square":
                current_menu = amplitudeOptions
            elif flag == "sine":
                current_menu = amplitudeOptionsSine
            current_selection = 0
        elif current_selection == 1: #back
            current_menu = modeOptions
            current_selection = 0
        elif current_selection == 2: #main
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == amplitudeOptions: #amplitude
        if current_selection == 0: #Input Amplitude
            current_selection = 0
        elif current_selection == 1: #back
            current_menu = modeOptions
            current_selection = 0
        elif current_selection == 2: #main
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == outputOptions: #output
        if current_selection == 0: # On selected
            if GPIO.input(btn) == 0: #if the button is pressed, the square wave will be generated based on the desired frequency
                if flag == "square":
                    square_wave(desiredFreq, True) #square_wave() is called
                    freqString = str(desiredFreq) + " Hz" #converts the desired frequency to a string
                    global newOutputOptions #new screen after the frequency is set
                    newOutputOptions = [freqString, "Back", "Main"] #new screen after the frequency is set
                    current_menu = newOutputOptions
                elif flag == "sine":
                    print("Here is the frequency: ", desiredFreq2, " here is the amplitude: ", Amp)
                    amplitudeTable()
                current_selection = 0
        elif current_selection == 1: #Off selected
            if GPIO.input(btn) == 0:    
                square_wave(desiredFreq, False) #square_wave() is called and the output is turned off
            current_selection = 0
        elif current_selection == 2: #back selected
            if GPIO.input(btn) == 0:
                square_wave(desiredFreq, False) #square_wave() is called and the output is turned off
                current_menu = modeOptions
            current_selection = 0
        elif current_selection == 3: #main selected
            if GPIO.input(btn) == 0:
                square_wave(desiredFreq, False) #square_wave() is called and the output is turned off
                current_menu = mainOptions
            current_selection = 0

    #********************** end of frequency submenu's
  
    #********************* ohmmeter - all submenu's

    elif current_menu == ohmmeterOptions: #ohmmeter
        if current_selection == 0: #XXX ohms selected
            ohmmeter() #ohmmeter() is called, and the resistance is measured
            resistanceStr = str(R_unknown) + " ohms" #converts the resistance to a string
            global newOhmmeterOptions #new screen after the resistance is measured
            newOhmmeterOptions = [resistanceStr, "Back", "Main"] #new screen after the resistance is measured
            current_menu = newOhmmeterOptions #the new menu on the LCD screen is now newOhmmeterOptions
            current_selection = 0
        elif current_selection == 1: #back selected
            current_menu = selectionOptions
            current_selection = 0
        elif current_selection == 2: #main selected
            current_menu = mainOptions
            current_selection = 0 
     #********************* end of ohmmeter submenu's
            
            
    
    #********************* voltmeter - all submenu's
    elif current_menu == vm: #voltmeter
        if current_selection == 0: #source selected
            current_menu = vmSrcOptions
            current_selection = 0
    elif current_menu == vmSrcOptions: #source
        if current_selection == 0: #external selected
            if GPIO.input(btn) == 0:
                volt = voltmeter() #voltmeter() is called, and the external voltage is measured.
                voltStr = str(volt) + " V +/ .25" #converts the voltage to a string
                global newVoltmeterOptions #new screen after the voltage is measured
                newVoltmeterOptions = [voltStr, "Back", "Main"] #new screen after the voltage is measured
                current_menu = newVoltmeterOptions #the new menu on the LCD screen is now newVoltmeterOptions
            current_selection = 0
        elif current_selection == 1: #internal selected
            if GPIO.input(btn) == 0: #if the button is pressed, the internal voltage is measured and displayed.
                current_menu = dcReference #the menu is changed to the DC Reference menu
                current_selection = 0 #the current selection is set to 0
            current_selection = 0
        elif current_selection == 2: #back selected
            current_menu = selectionOptions #the menu is changed to the selection menu
            current_selection = 0
        elif current_selection == 3: #main selected
            current_menu = mainOptions #the menu is changed to the main menu
            current_selection = 0 
    #********************* end of voltmeter submenu's
    
    #********************* dcreference - all submenu's
    elif current_menu == dcReference: #DC Reference
        if current_selection == 0: #Voltage Value Input Selected
            current_menu = voltageInputOptions
            current_selection = 0
        elif current_selection == 1: #Output Selected
            current_menu = dcOutputOptions
            current_selection = 0
        elif current_selection == 2: #back selected
            current_menu = selectionOptions
            current_selection = 0
        elif current_selection == 3: #main selected
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == dcOutputOptions: # DC Output Options
        if current_selection == 0: #DC On selected
            print("IT WORKS!!") #this is a test to see if the button is pressed
            if GPIO.input(btn) == 0:
                print("IT STILL WORKS!!") #this is a test to see if the button is pressed
                internal_ref(voltVal) #internal_ref() is called, and the internal voltage is set to the desired value.
                current_menu = vmSrcOptions
            current_selection = 0 #the current selection is set to 0
        elif current_selection == 1: #DC Off selected
            if GPIO.input(btn) == 0: #if the button is pressed, the internal voltage is set to 0.
                internal_ref(0.25) #internal_ref() is called, and the internal voltage is set to 0, our voltage goes to 0.25V.
            current_selection = 0
        elif current_selection == 2: #DC back selected
            if GPIO.input(btn) == 0:
                internal_ref(0.25) #internal_ref() is called, and the internal voltage is set to 0, our voltage goes to 0.25V.
            current_menu = dcReference #the menu is changed to the DC Reference menu
            current_selection = 0
        elif current_selection == 3: #DC main selected
            if GPIO.input(btn) == 0:
                internal_ref(0.25)  #internal_ref() is called, and the internal voltage is set to 0, our voltage goes to 0.25V.
            current_menu = mainOptions
            current_selection = 0
    #********************* end of dcreference submenu's
    
    #********************* newOhmmeterMenu - 
    #this menu is used to display the resistance of the unknown resistor. 
    #The user will be able to select back or main to return to the previous menu.
    elif current_menu == newOhmmeterOptions:
        if current_selection == 0:
            current_selection = 0
        elif current_selection == 1: #back
            current_menu = selectionOptions
            current_selection = 0
        elif current_selection == 2:  #main
            current_menu = mainOptions
            current_selection = 0
    #********************* end of newOhmmeterMenu 
     
    #********************* newVoltmeterOptions 
    #this menu is used to display the external voltage.
    elif current_menu == newVoltmeterOptions: #new screen after the voltage is measured
        if current_selection == 0:
            current_selection = 0
        elif current_selection == 1: #back
            current_menu = vmSrcOptions #the menu is changed to the DC Reference menu
            current_selection = 0
        elif current_selection == 2: #main
            current_menu = mainOptions
            current_selection = 0
    #********************* newVoltmeterOptions
            
    elif current_menu == voltageInputOptions: #Voltage Input Options
        if current_selection == 0: #0.25V selected
            if GPIO.input(btn) == 0: #if the button is pressed, the internal voltage is set to 0.25V.
                selected_voltage = f"{voltVal} V" #converts the voltage to a string
                global new_menu #new screen after the voltage is measured
                new_menu = [selected_voltage, "Back", "Main"] #new screen after the voltage is measured
                current_menu = new_menu #the new menu on the LCD screen is now new_menu
                current_selection = 0
        elif current_selection == 1: #back 
            current_menu = dcReference
            current_selection = 0
        elif current_selection == 2: #main
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == new_menu:
        if current_selection == 0:
            current_selection = 0
        elif current_selection == 1: #back
            current_menu = dcReference
            current_selection = 0 
        elif current_selection == 2: #main
            current_menu = mainOptions
            current_selection = 0
      
    #********************* newFgOptions 
    #this menu is used to display the frequency of the square wave.
    elif current_menu == newFgOptions:
        if current_selection == 0:
            current_selection = 0
        elif current_selection == 1: #back
            if GPIO.input(btn) == 0:
                square_wave(desiredFreq, False) #square_wave() is called, and the square wave is turned off.
                current_menu = modeOptions
            current_selection = 0
        elif current_selection == 2:  #main
            if GPIO.input(btn) == 0:
                square_wave(desiredFreq, False) #square_wave() is called, and the square wave is turned off.
                current_menu = mainOptions
            current_selection = 0
    #********************* newFgOptions

    #********************* newFgOptionsSine 
    #this menu is used to display the frequency of the sine wave.
    elif current_menu == newFgOptionsSine:
        if current_selection == 0:
            current_selection = 0
        elif current_selection == 1: #back
            #will do more here
            current_menu = modeOptions
        elif current_selection == 2: #main
            #will do more here
            current_menu = mainOptions
    #********************* newFgOptionsSine

    elif current_menu == amplitudeOptionsSine:
        if current_selection == 0:
            if GPIO.input(btn) == 0:
                selected_Amp = f"{Amp} V" #converts the voltage to a string
                global ampSineMenu #new screen
                ampSineMenu = [selected_Amp, "Back", "Main"] #new screen
                current_menu = ampSineMenu
            current_selection = 0 
        elif current_menu == 1: #back
            current_menu = modeOptions
            current_selection = 0
        elif current_menu == 2: #main
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == ampSineMenu:
        if current_selection == 0:
            current_selection = 0
        elif current_selection == 1: #back
            current_menu = modeOptions
            current_selection = 0
        elif current_selection == 2: #main
            current_menu = mainOptions
            current_selection = 0         
    elif current_menu == frequencyMeasurement:
        if current_selection == 0: #external 
            if GPIO.input(btn) == 0:
                 calcFreq(16)
            current_selection = 0 
        elif current_selection == 1: #internal
            current_menu = modeOptions
            current_selection = 0
        elif current_selection == 2: #back
            current_menu = mainOptions
            current_selection = 0
        elif current_selection == 3: #main
            current_menu = mainOptions
            current_selection = 0
    elif current_menu == externalFreqOptions:
        if current_selection == 0:
            current_selection = 0
        elif current_selection == 1: #back
            if GPIO.input(btn) == 0:     
                current_menu = modeOptions
                GPIO.remove_event_detect(16)
            current_selection = 0
        elif current_selection == 2: #main
            if GPIO.input(btn) == 0:
                current_menu = mainOptions
                GPIO.remove_event_detect(16)
            current_selection = 0
            
"""
The rotary encoder callback function. This function is called when the rotary encoder is rotated. It will change the current
selection based on the direction of the rotation. If the user is on the frequency selection, the frequency will be changed
based on the speed of the rotation. If the user is on the last selection, the selection will be changed to the first selection.
"""
def rotary_callback(channel):
    global current_menu, current_selection, currentFreq,currentFreq2, Amp, last_rotation_time, voltVal
    dt_state = GPIO.input(dt) # Read the state of the DT pin
    now = time.time() # Get the current time
    if GPIO.input(clk) != dt_state: # Clockwise rotation
        if current_menu == fgFreqOptions and current_selection == 0 and flag == "square": # If the user is on the frequency selection menu and the selection is on the frequency option 
            if now - last_rotation_time >= 3:  # Slow rotation
                currentFreq = min(10000, currentFreq + 10) # Increase the frequency by 10 Hz if the rotation is slow
            else:  # Fast rotation
                currentFreq = min(10000, currentFreq + 100) # Increase the frequency by 100 Hz if the rotation is fast
            fgFreqOptions[0] = f"Frequency: {currentFreq} Hz" # Update the frequency option
            last_rotation_time = now # Update the last rotation time
        elif current_menu == fgFreqOptions and current_selection == 0 and flag == "sine": # If the user is on the frequency selection menu and the selection is on the frequency option
            currentFreq2 = min(10000, currentFreq2 + 100) # Increase the frequency by 100 Hz
            fgFreqOptions[0] = f"Frequency: {currentFreq2} Hz" #Update the frequency option
        elif current_menu == amplitudeOptionsSine and current_selection == 0: # If the user is on the amplitude selection menu and the selection is on the amplitude option
            Amp = min(5, Amp + 0.25)
            amplitudeOptionsSine[0] = f"Ampli: {Amp}" #update the amplitude
        elif current_menu == voltageInputOptions and current_selection == 0: # If the user is on the voltage input menu and the selection is on the voltage option
            voltVal = max(0, min(4, voltVal + 0.25)) # Increase the voltage by 0.25V
            voltageInputOptions[0] = f"Voltage: {voltVal:.2f} V" # Update the voltage option
        elif current_selection == len(current_menu) - 1: # If the user is on the last selection of the menu change the selection to the first selection
            current_selection = 0 # Change the selection to the first selection
        else: 
            current_selection += 1 # Change the selection to the next selection
    else:
        if current_menu == fgFreqOptions and current_selection == 0 and flag == "square": # If the user is on the frequency selection menu and the selection is on the frequency option
            if now - last_rotation_time >= 0.6:  # Slow rotation
                currentFreq = max(100, currentFreq - 10) # Decrease the frequency by 10 Hz if the rotation is slow
            else: # Fast rotation
                currentFreq = max(100, currentFreq - 100) # Decrease the frequency by 100 Hz if the rotation is fast
            fgFreqOptions[0] = f"Frequency: {currentFreq} Hz" # Update the frequency option
            last_rotation_time = now # Update the last rotation time
        elif current_menu == fgFreqOptions and current_selection == 0 and flag == "sine": # If the user is on the frequency selection menu and the selection is on the frequency option
            currentFreq2 = max(1000, currentFreq2 - 100) # Decrease the frequency by 100 Hz
            fgFreqOptions[0] = f"Frequency: {currentFreq2} Hz" # Update the frequency option
        elif current_menu == amplitudeOptionsSine and current_selection == 0: # If the user is on the amplitude selection menu and the selection is on the amplitude option
            Amp = max(1, Amp - 0.25)
            amplitudeOptionsSine[0] = f"Ampli: {Amp}" #update the amplitude
        elif current_menu == voltageInputOptions and current_selection == 0: # If the user is on the voltage input menu and the selection is on the voltage option
            voltVal = max(0, min(4, voltVal - 0.25)) # Decrease the voltage by 0.25V
            voltageInputOptions[0] = f"Voltage: {voltVal:.2f} V" # Update the voltage option
        elif current_selection == 0:
            current_selection = len(current_menu) - 1 # Change the selection to the last selection of the menu if the user is on the first selection
        else:
            current_selection -= 1 # Change the selection to the previous selection
    
#The button callback function. This function is called when the button is pressed. It will change the current menu based on
#the current selection. If the user is on the main menu, the program will exit.
#The rotary encoder callback function. This function is called when the rotary encoder is rotated. It will change the current
#selection based on the direction of the rotation.
GPIO.add_event_detect(btn, GPIO.FALLING, callback = button_callback, bouncetime = 120)
GPIO.add_event_detect(clk, GPIO.FALLING, callback = rotary_callback, bouncetime = 120)

#The main loop. This loop will display the current menu and selection on the LCD screen. 
while True:
    lcd.setCursor(0,0) # Set the cursor to the first line
    lcd.printout("Current Selection:") # Print the current selection
    lcd.setCursor(0,1) # Set the cursor to the second line
    lcd.clear() # Clear the second line
    lcd.printout(current_menu[current_selection]) # Print the current menu option on the second line of the LCD screen 

    time.sleep(0.1) # Wait for 0.1 seconds







