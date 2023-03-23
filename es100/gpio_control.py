""" GPIO control (for EN & IRQ lines)

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import sys
import time

DEVICE_LIBRARY_UNKNOWN = 0
DEVICE_LIBRARY_GPIO = 1
DEVICE_LIBRARY_PIN = 2

DEVICE_LIBRARY = DEVICE_LIBRARY_UNKNOWN

try:
    import RPi.GPIO as GPIO
    DEVICE_LIBRARY = DEVICE_LIBRARY_GPIO
except ImportError:
    pass

try:
    from machine import Pin
    DEVICE_LIBRARY = DEVICE_LIBRARY_PIN
except ImportError:
    pass

if DEVICE_LIBRARY == DEVICE_LIBRARY_PIN:
    from pico.irq_wait_for_edge import irq_wait_for_edge

IRQ_WAKEUP_DELAY = 2      # When waiting for an IRQ; wake up after this time and loop again

class ES100GPIOError(Exception):
    """ ES100GPIOError

    ES100GPIOError is raised should errors occur when using ES100GPIO() class.
    """

class ES100GPIO:
    """ ES100GPIO

    :param en: EN pin number
    :param irq: IRQ pin number
    :param debug: True to enable debug messages
    :return: New instance of ES100GPIO()

    All GPIO control is via ES100GPIO() class.
    """

    def __init__(self, en=None, irq=None, debug=False):
        """ """
        if DEVICE_LIBRARY == DEVICE_LIBRARY_UNKNOWN:
            raise ES100GPIOError('RPi.GPIO or machine package not installed - are you on a Raspberry Pi?')
        if en is None or irq is None:
            raise ES100GPIOError('GPIO must be defined - no default provided')
        self._gpio_en = en
        self._gpio_irq = irq
        self._debug = debug
        self._setup()

    def _setup(self):
        if DEVICE_LIBRARY == DEVICE_LIBRARY_GPIO:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self._gpio_en, GPIO.OUT)
            GPIO.setup(self._gpio_irq, GPIO.IN, GPIO.PUD_DOWN)
        if DEVICE_LIBRARY == DEVICE_LIBRARY_PIN:
            self._gpio_en = Pin('GP%d' % self._gpio_en, Pin.OUT)
            self._gpio_irq = Pin('GP%d'% self._gpio_irq, Pin.IN, Pin.PULL_DOWN)

    def __del__(self):
        """ __del__ """
        if not GPIO:
            return
        self._close()

    def _close(self):
        """ _close """
        self.en_low()
        GPIO.cleanup()

    def en_low(self):
        """ en_low()

        EN set low
        """
        # Enable Input. When low, the ES100 powers down all circuitry.
        if DEVICE_LIBRARY == DEVICE_LIBRARY_GPIO:
            GPIO.output(self._gpio_en, GPIO.LOW)
        if DEVICE_LIBRARY == DEVICE_LIBRARY_PIN:
            self._gpio_en.off()

    def en_high(self):
        """ en_high()

        EN set high
        """
        # Enable Input. When high, the device is operational.
        if DEVICE_LIBRARY == DEVICE_LIBRARY_GPIO:
            GPIO.output(self._gpio_en, GPIO.HIGH)
        if DEVICE_LIBRARY == DEVICE_LIBRARY_PIN:
            self._gpio_en.on()

    def irq_wait(self, timeout=None):
        """ irq_wait(self, timeout=None)

        :param timeout: Either None or the number of seconds to control timeout
        :return: True if IRQ/Interrupt is active low, False with timeout

        IRQ- will go active low once the receiver has some info to return.
        """
        # IRQ/Interrupt is active low to signal data available
        if self._debug:
            sys.stderr.write('IRQ WAIT: ')
            # sys.stderr.flush()
        while True:
            if DEVICE_LIBRARY == DEVICE_LIBRARY_GPIO:
                if not GPIO.input(self._gpio_irq):
                    break
            if DEVICE_LIBRARY == DEVICE_LIBRARY_PIN:
                if not self._gpio_irq.value():
                    break
            if self._debug:
                sys.stderr.write('H')
                # sys.stderr.flush()
            # now wait (for any transition) - way better than looping, sleeping, and checking
            if timeout:
                this_timeout=min(int(timeout*1000), IRQ_WAKEUP_DELAY*1000)
            else:
                this_timeout=IRQ_WAKEUP_DELAY*1000
            if DEVICE_LIBRARY == DEVICE_LIBRARY_GPIO:
                channel = GPIO.wait_for_edge(self._gpio_irq, GPIO.BOTH, timeout=this_timeout)
            if DEVICE_LIBRARY == DEVICE_LIBRARY_PIN:
                channel = irq_wait_for_edge(self._gpio_irq, timeout=this_timeout)
            if channel is None:
                # timeout happened
                if self._debug:
                    sys.stderr.write('.')
                    # sys.stderr.flush()
                if timeout:
                    timeout -= IRQ_WAKEUP_DELAY
                    if timeout <= 0:
                        if self._debug:
                            sys.stderr.write(' T\n')
                            # sys.stderr.flush()
                        return False
        if self._debug:
            sys.stderr.write(' L\n')
            # sys.stderr.flush()
        return True
