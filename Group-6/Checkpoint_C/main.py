import RPi.GPIO as GPIO
import time
import rgb1602
import subprocess


# Set up the rotary encoder pin numbers
clk = 17
dt = 18
btn = 27

# Set up the RGB1602 display
lcd = rgb1602.RGB1602(16,2)
lcd.setRGB(0,128,128)

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clkLastState = GPIO.input(clk)
currentSelection = 0
selectionOptions = ["OFF","Function Generator", "Ohmmeter", "Voltmeter", "DC Reference", "Back", "Main"]
modeOptions = ["Type", "Frequency", "Amplitude", "Output"]
fgOptions = ["Amplitude", "Type", "Frequency"]
fgTypeOptions = ["Square", "Back", "Main"]
fgFreqOptions = ["Input Frequency", "Back", "Main"]
fgAmpOptions = ["Input Amplitude", "Back", "Main"]
outputOptions = ["On", "Off", "Back", "Main"]
vmSrcOptions = ["External", "Internal Reference", "Back", "Main"]
dcOutputOptions = ["On", "Off", "Back", "Main"]

# Define the rotary encoder callback function
def rotaryCallback(channel):
    global currentSelection, selectionOptions, lcd
    
    # Read the state of the rotary encoder
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState != dtState:
        # Clockwise rotation
        currentSelection = (currentSelection + 1) % len(selectionOptions)
    else:
        # Counterclockwise rotation
        currentSelection = (currentSelection - 1) % len(selectionOptions)

    lcd.setCursor(0, 1)
    lcd.printout(selectionOptions[currentSelection])

# Register the rotary encoder callback function for both rising and falling edge
GPIO.add_event_detect(clk, GPIO.BOTH, callback=rotaryCallback, bouncetime=10)

while True:
    # Read the state of the rotary encoder
    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    # If the rotary encoder has been turned, update the current selection
    if clkState != clkLastState:
        if dtState != clkState:
            currentSelection = (currentSelection + 1) % len(selectionOptions)
        else:
            currentSelection = (currentSelection - 1) % len(selectionOptions)

        # Update the second line of the LCD screen
        lcd.setCursor(0,1)
        lcd.clear()
        lcd.printout(selectionOptions[currentSelection])
        

    # Read the state of the rotary encoder switch
    swState = GPIO.input(btn)

    # If the switch is pressed, take action based on the current selection
    if swState == False:
        if selectionOptions[currentSelection] == "OFF":
            lcd.clear()
            GPIO.cleanup()
            exit()
        elif selectionOptions[currentSelection] == "Back":
            # Go back to the main screen
            currentSelection = 0
            lcd.clear()
        elif selectionOptions[currentSelection] == "Function Generator":
            # Handle function generator option
            #...

            currentOptions = fgOptions
            while True:
                lcd.setCursor(0, 1)
                lcd.printout(currentOptions[currentSelection])

                # Read the state of the rotary encoder
                clkState = GPIO.input(clk)
                dtState = GPIO.input(dt)

                # If the rotary encoder has been turned, update the current selection
                if clkState != clkLastState:
                    if dtState != clkState:
                        
                        currentSelection = (currentSelection + 1) % len(currentOptions)
                    else:
                        
                        currentSelection = (currentSelection - 1) % len(currentOptions)

                # Read the state of the rotary encoder switch
                swState = GPIO.input(btn)
                

                # If the switch is pressed, take action based on the current selection
                if swState == False:
                    if currentOptions[currentSelection] == "Back":
                        currentSelection = 0
                        break

                # Print "Select Option:" on the first line
                lcd.setCursor(0, 0)
                #lcd.printout("Select Option:")

                # Delay to avoid bouncing of the rotary encoder switch
                time.sleep(0.01)

               # Save the last state of the rotary encoder for comparison next time around
                clkLastState = clkState
   
        elif selectionOptions[currentSelection] == "Ohmmeter":
            # Handle ohmmeter option
            # ...
            lcd.printout("Ohmmeter")
            pass
        elif selectionOptions[currentSelection] == "Voltmeter":
            # Handle voltmeter option
            # ...
            lcd.printout("Inside Voltmeter")
        elif selectionOptions[currentSelection] == "DC Reference":
            # Handle DC reference option
            # ...
            lcd.printout("Inside DC REF")
            pass
        elif selectionOptions[currentSelection] == "Main":
            # Go back to the main screen
            currentSelection = 0
            lcd.clear()

    # Print "Select Mode:" on the first line only once
    if currentSelection == 0:
        lcd.setCursor(0, 0)
        lcd.printout("Select Mode:")

    # Delay to avoid bouncing of the rotary encoder switch
    time.sleep(0.01)

    # Save the last state of the rotary encoder for comparison next time around
    clkLastState = clkState




