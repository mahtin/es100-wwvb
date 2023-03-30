"""

    irq_wait_for_edge

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import time
from machine import Pin

from pico.board_led import led_on, led_off

irq_triggered_done = False

def irq_triggered(pin):
    global irq_triggered_done
    irq_triggered_done = True

def irq_wait_for_edge(gpio_irq, timeout=None):
    global irq_triggered_done
    led_off()
    blink_the_led_counter = 0
    irq_triggered_done = False
    gpio_irq.irq(handler=irq_triggered, trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING)
    start_ms = time.ticks_ms()
    while not irq_triggered_done:
        if timeout is not None and time.ticks_diff(time.ticks_ms(), start_ms) > timeout:
                # timeout - kill callback and return
                gpio_irq.irq(handler=None, trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING)
                led_off()
                return None
        blink_the_led_counter += 1
        if blink_the_led_counter == 500:
            led_on()
        if blink_the_led_counter >= 1000:
            led_off()
            blink_the_led_counter = 0
        # annoyingly, this is all we can do - a small sleep
        time.sleep(0.001)
    led_off()
    return gpio_irq
