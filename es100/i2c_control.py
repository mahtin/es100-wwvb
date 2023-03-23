""" i2c communications for ES100

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import time

DEVICE_LIBRARY_UNKNOWN = 0
DEVICE_LIBRARY_SMBUS = 1
DEVICE_LIBRARY_I2C = 2

DEVICE_LIBRARY = DEVICE_LIBRARY_UNKNOWN

try:
    # Linux or Mac's or something like that ...
    from smbus import SMBus
    DEVICE_LIBRARY = DEVICE_LIBRARY_SMBUS
except ImportError:
    pass

try:
    # Micropython on Raspberry Pi Pico (or Pico W)
    from machine import I2C
    DEVICE_LIBRARY = DEVICE_LIBRARY_I2C
except ImportError:
    pass

class ES100I2CError(Exception):
    """ ES100I2CError """

class ES100I2C:
    """ ES100I2C """

    ERROR_DELAY_SEC = 0.001             # 1 ms delay if i2c read/write error

    def __init__(self, bus, address, debug=False):
        """ __init__ """
        self._device = None
        if DEVICE_LIBRARY == DEVICE_LIBRARY_UNKNOWN:
            raise ES100I2CError('SMBus or I2C package not installed - are you on a Raspberry Pi?')
        self._debug = debug
        self._i2c_bus = bus
        self._i2c_address = address
        if not 0 <= self._i2c_bus <= 1:
            raise ES100I2CError('i2c bus number error: %s' % bus)
        if not 0x08 <= self._i2c_address <= 0x77:
            raise ES100I2CError('i2c address number error: %s' % address)
        self.open()

    def __del__(self):
        """ __del__ """
        if not self._device:
            return
        self.close()

    def open(self):
        """ _setup """
        if self._device:
            # already open
            return

        try:
            if DEVICE_LIBRARY == DEVICE_LIBRARY_SMBUS:
                self._device = SMBus(self._i2c_bus)
                #self._device.open(self._i2c_bus) # not needed if passed on class creation
            if DEVICE_LIBRARY == DEVICE_LIBRARY_I2C:
                # Presently there's no Pin() passing option to this code; hence ...
                # bus0 -> I2C(0, freq=399361, scl=5, sda=4) i.e GP5 (pin  7) & GP4 (pin 6)
                # bus1 -> I2C(1, freq=399361, scl=7, sda=6) i.e GP7 (pin 10) & GP6 (pin 9)
                # ... use these deaults
                self._device = I2C(self._i2c_bus)
        except FileNotFoundError as err:
            raise ES100I2CError('i2c bus %d open error: %s' % (self._i2c_bus, err)) from err

    def close(self):
        """ _close """
        if self._device:
            if DEVICE_LIBRARY == DEVICE_LIBRARY_SMBUS:
                self._device.close()
            if DEVICE_LIBRARY == DEVICE_LIBRARY_I2C:
                pass
            self._device = None

    def read(self):
        """ read """
        count = 0
        while True:
            try:
                if DEVICE_LIBRARY == DEVICE_LIBRARY_SMBUS:
                    rval = self._device.read_byte(self._i2c_address)
                if DEVICE_LIBRARY == DEVICE_LIBRARY_I2C:
                    rval = self._device.readfrom(self._i2c_address, 1)
                    rval = rval[0]
                return rval
            except OSError as err:
                if count > 10:
                    raise ES100I2CError('i2c read: %s' % (err)) from err
            time.sleep(ES100I2C.ERROR_DELAY_SEC)
            count += 1

    def write_addr(self, addr, data):
        """ write_addr """
        count = 0
        while True:
            try:
                if DEVICE_LIBRARY == DEVICE_LIBRARY_SMBUS:
                    self._device.write_byte_data(self._i2c_address, addr, data)
                if DEVICE_LIBRARY == DEVICE_LIBRARY_I2C:
                    self._device.writeto_mem(self._i2c_address, addr, bytes([data]))
                return
            except OSError as err:
                if count > 10:
                    raise ES100I2CError('i2c write 0x%02x: %s' % (addr, err)) from err
            time.sleep(ES100I2C.ERROR_DELAY_SEC)
            count += 1

    def write(self, data):
        """ write """
        count = 0
        while True:
            try:
                if DEVICE_LIBRARY == DEVICE_LIBRARY_SMBUS:
                    self._device.write_byte(self._i2c_address, data)
                if DEVICE_LIBRARY == DEVICE_LIBRARY_I2C:
                    self._device.writeto(self._i2c_address, bytes([data]))
                return
            except OSError as err:
                if count > 10:
                    raise ES100I2CError('i2c write 0x%02x: %s' % (data, err)) from err
            time.sleep(ES100I2C.ERROR_DELAY_SEC)
            count += 1
