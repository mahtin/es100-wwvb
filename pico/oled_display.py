"""

OLED I2C display logic for ...
  I2C 0.96 Inch OLED I2C Display Module 128x64 Pixel
  https://www.amazon.com/dp/B09C5K91H7

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

from machine import Pin, I2C

from pico.ssd1306 import SSD1306_I2C

class OLEDDisplay128x64:
    """ OLEDDisplay128x64 """

    def __init__(self):
        """ __init__ """
        self._ssd1306 = None
        self._open()

    def _open(self):
        """ _open() """
        try:
            i2c = I2C(0, sda=Pin(8), scl=Pin(9))
        except ValueError as err:
            print('I2C bus - failed open: %s' % (err))
            return
        scan = i2c.scan()
        if len(scan) == 0:
            print('I2C bus - failed to find anything on the bus')
            return
        if scan[0] != 0x3c:
            print('I2C bus - failed to find LCD on the bus')
            return
        try:
            self._ssd1306 = SSD1306_I2C(128, 64, i2c)
        except OSError as err:
            self._ssd1306 = None
            print('I2C display - failed to open: %s' % (err))
            return

    def background(self):
        """ background() """
        if not self._ssd1306:
            return
        self._ssd1306.fill_rect(0, 0, 128, 16, 0)     # yellow area
        self._ssd1306.fill_rect(0, 16, 128, 48, 0)    # blue area (if your display is that type)
        self._ssd1306.show()

    def datetime(self, dt=None):
        """ datetime() """
        if not self._ssd1306:
            return
        self._ssd1306.fill_rect(0, 0, 128, 16, 0)
        if dt is None:
            # leave screen blank
            self._ssd1306.show()
            return
        msec = int(dt.microsecond/1000.0)
        dt = dt.replace(microsecond=msec*1000)
        # 2023-03-22 17:57:42.803+00:00
        date_str = str(dt)
        self._ssd1306.text('%s' % date_str[0:0+10], 0, 0, 1)
        self._ssd1306.text('%s   UTC' % date_str[11:11+10], 0, 8, 1)
        self._ssd1306.show()

    def text(self, s, x, y):
        """ text """
        if not self._ssd1306:
            return
        self._ssd1306.fill_rect(x, y, 128, 8, 0)
        self._ssd1306.text(s, x, y, 1)
        self._ssd1306.show()

    def progress_bar(self, percent, x, y):
        """ progress_bar """
        if not self._ssd1306:
            return
        width = min(128, int(128 * percent))
        self._ssd1306.fill_rect(x, y, width, 8, 1)
        self._ssd1306.fill_rect(x+width, y, 128-width, 8, 0)
        self._ssd1306.show()
