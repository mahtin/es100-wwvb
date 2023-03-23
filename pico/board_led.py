"""

    board_led - so so simple

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

from machine import Pin

led = Pin("LED", Pin.OUT) # internal LED
led.off()

def led_on():
    led.on()
def led_off():
    led.off()

