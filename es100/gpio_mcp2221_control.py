""" GPIO control (for EN & IRQ lines) via MCP2221

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import os
import sys
import time

os.environ['BLINKA_MCP2221'] = "1"
try:
    import board
    import digitalio
except RuntimeError:
    board = None

IRQ_WAKEUP_DELAY = 2      # When waiting for an IRQ; wake up after this time and loop again

class ES100GPIOError(Exception):
    """ ES100GPIOError

    ES100GPIOError is raised should errors occur when using ES100GPIO() class.
    """

def irq_wait_for_edge(gpio_irq, timeout=None):
    # XXX TODO - not correct; but could work
    time.sleep(0.001)
    return True

class ES100GPIO():
    """ ES100GPIO_MCP2221

    :param en: EN pin number
    :param irq: IRQ pin number
    :param debug: True to enable debug messages
    :return: New instance of ES100GPIO_MCP2221()

    All GPIO control is via ES100GPIO() class.
    """

    def __init__(self, en=None, irq=None, debug=False):
        """ """
        if en is None or irq is None:
            raise ES100GPIOError('GPIO must be defined - no default provided')
        self._gpio_en = en
        self._gpio_irq = irq
        self._debug = debug
        self._setup()

    def _setup(self):
        """ _setup """
        if board is None:
            raise ES100GPIOError('MCP2221 not present')
        self._gpio_en = digitalio.DigitalInOut(getattr(board, 'G%d' % self._gpio_en))
        self._gpio_en.direction = digitalio.Direction.OUTPUT
        self._gpio_irq = digitalio.DigitalInOut(getattr(board, 'G%d' % self._gpio_irq))
        self._gpio_en.direction = digitalio.Direction.INPUT

    def __del__(self):
        """ __del__ """
        self._close()

    def _close(self):
        """ _close """
        self.en_low()

    def en_low(self):
        """ en_low()

        EN set low
        """
        # Enable Input. When low, the ES100 powers down all circuitry.
        self._gpio_en = False

    def en_high(self):
        """ en_high()

        EN set high
        """
        # Enable Input. When high, the device is operational.
        self._gpio_en = True

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
            if not self._gpio_irq:
                break
            if self._debug:
                sys.stderr.write('H')
                # sys.stderr.flush()
            # now wait (for any transition) - way better than looping, sleeping, and checking
            if timeout:
                this_timeout=min(int(timeout*1000), IRQ_WAKEUP_DELAY*1000)
            else:
                this_timeout=IRQ_WAKEUP_DELAY*1000
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
