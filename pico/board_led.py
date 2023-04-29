"""

    board_led - so so simple

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

from machine import Pin

ledINT = Pin('LED', Pin.OUT) # internal on board LED
led16 = Pin('GP16', Pin.OUT) # external LED built into pc board
led17 = Pin('GP17', Pin.OUT) # external LED built into pc board
led18 = Pin('GP18', Pin.OUT) # external LED built into pc board
led19 = Pin('GP19', Pin.OUT) # external LED built into pc board

ledINT.off()
led16.off()
led17.off()
led17.off()
led18.off()

led = led16 # presently we used this LED

def led_on():
    led.on()
def led_off():
    led.off()

