import RPi.GPIO as GPIO
import time
import rgb1602
import spidev
# Set up the rotary encoder pin numbers
encoder_a = 17
encoder_b = 18
encoder_btn = 27

# Set up the RGB1602 display
lcd = rgb1602.RGB1602(16,2)
lcd.setRGB(0,140,130)

# Set up the rotary encoder
GPIO.setmode(GPIO.BCM)
GPIO.setup(encoder_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoder_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encoder_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

options = ["P0", "P1"]
position = 0
selected_option = None
value = 100
global cclk
cclk = False

def display_menu():
    global position
    lcd.clear()
    #lcd.printout("Select: " + options[position])
    lcd.setCursor(0,0)
    lcd.printout("Select Potentio:")
    lcd.setCursor(0,1)
    if position == 0: 
        lcd.printout("P0 <-- P1")
        time.sleep(0.1)
    elif position == 1:
        lcd.printout("P0 --> P1")
        time.sleep(0.1)
    time.sleep(0.2)
    
def display_value(selected_option):
    global value
    lcd.clear()
    lcd.printout(selected_option + ": " + str(value) + " ohms")

def btn_callback(channel):
    global selected_option
    start_time = time.time()
    while GPIO.input(encoder_btn) == 0:
        if time.time() - start_time >= 3:
            selected_option = None
            display_menu()
            return
        elif time.time() - start_time <= 0.2:
            time.sleep(0.2)
            send_pot_val(value)
    selected_option = options[position]
    display_value(selected_option)
    
# Define the callback function for the encoder_a event
def encoder_a_callback(channel):
    if GPIO.input(encoder_a) == GPIO.LOW:
        if GPIO.input(encoder_b) == GPIO.LOW:
            # Counterclockwise rotation
            print("Counterclockwise rotation")
        else:
            # Clockwise rotation
            print("Clockwise rotation")

# Define the callback function for the encoder_b event
def encoder_b_callback(channel):
    if GPIO.input(encoder_b) == GPIO.LOW:
        if GPIO.input(encoder_a) == GPIO.HIGH:
            # Counterclockwise rotation
            print("Counterclockwise rotation")
            cclk = True
        else:
            # Clockwise rotation
            print("Clockwise rotation")

GPIO.add_event_detect(encoder_a, GPIO.BOTH, callback=encoder_a_callback, bouncetime = 120)
GPIO.add_event_detect(encoder_b, GPIO.BOTH, callback=encoder_b_callback, bouncetime = 120)
    
def send_pot_val(value):
    lcd.setCursor(1,0)
    time.sleep(0.1)
    start_time = time.time()
    spi = spidev.SpiDev()
    spi.open(0,0)
    spi.max_speed_hz = 1000000
    wiper_set = int(value / (9500 / 128))

    if wiper_set > 255:
        raise ValueError("Wiper setting value is too high, maximum is 255")
    if options[position] == "P0":
        spi.xfer2([0x00, wiper_set])
    elif options[position] == "P1":
        spi.xfer2([0x10, wiper_set])
    else:
        raise ValueError("invalid attempt, try again!")



def inc_value(increment):
    global value
    value += increment
    time.sleep(0.2)
    if value > 10000:
        value = 10000
    elif value < 100:
        value = 100
    display_value(selected_option)
    

    
    
GPIO.add_event_detect(encoder_btn, GPIO.FALLING, callback=btn_callback, bouncetime=300)

display_menu()


last_time = time.time()
direction = None
while True:
    # Rotate the encoder to change the menu position or value
    if GPIO.input(encoder_a) == 0:
        if GPIO.input(encoder_b) == 1:
            if selected_option is None:
                # If the rotation is fast, change the position immediately
                if time.time() - last_time < 0.3:
                    position = (position + 1) % len(options)
                    display_menu()
                else:
                    direction = 1
            else:
                # If the rotation is fast, change the value by 100
                if time.time() - last_time < 0.3:
                    inc_value(100)
                    time.sleep(0.1)
                else:
                    inc_value(10)
                    time.sleep(0.1)
        elif GPIO.input(encoder_b) == 0:
            if selected_option is None:
                # If the rotation is fast, change the position immediately
                if time.time() - last_time < 0.3:
                    position = (position - 1) % len(options)
                    display_menu()
                else:
                    direction = -1
            elif cclk == True:
                if time.time() - last_time < 0.3:
                    inc_value(-100)
                else:
                    inc_value(-10)
            else:
                # If the rotation is fast, change the value by 100
                if time.time() - last_time < 0.3:
                    inc_value(-100)
                    time.sleep(0.1)
                else:
                    inc_value(-10)
                    time.sleep(0.1)
        # Update the last time the encoder was rotated
        last_time = time.time()
    if direction == 1:
        position = (position + 1) % len(options)
        display_menu()
    elif direction == -1:
        position = (position - 1) % len(options)
        display_menu()
    direction = None
    


GPIO.cleanup()

