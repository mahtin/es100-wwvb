""" i2c communications for ES100

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import os
import sys
import time

os.environ['BLINKA_MCP2221'] = "1"
try:
    import board
except RuntimeError:
    board = None

class ES100I2CError(Exception):
    """ ES100I2CError """

class ES100I2C:
    """ ES100I2C """

    ERROR_DELAY_SEC = 0.001             # 1 ms delay if i2c read/write error

    def __init__(self, bus, address, debug=False):
        """ __init__ """
        self._device = None
        self._debug = debug
        self._i2c_bus = bus
        self._i2c_address = address
        if self._i2c_bus != 0:
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

        if board is None:
            raise ES100GPIOError('MCP2221 not present')
        self._device = board.I2C()
        try:
            self._device.unlock()
        except ValueError:
            pass
        while not self._device.try_lock():
            pass
        print("DEBUG: open() - OK", file=sys.stderr)

    def close(self):
        """ _close """
        if self._device:
            try:
                self._device.unlock()
            except ValueError:
                pass
            self._device = None

    def read(self, addr):
        """ read """
        count = 0
        print("DEBUG: read(%d)" % addr, file=sys.stderr)
        while True:
            try:
                registers = bytearray(14)
                self._device.readfrom_into(self._i2c_address, registers)
                print("DEBUG: readfrom_into: %s - 0x%02x" % (registers, registers[addr]))
                rval = registers[addr]
                return rval
            except OSError as err:
                print('DEBUG: i2c read: %s' % (err))
                if count > 10:
                    raise ES100I2CError('i2c read: %s' % (err)) from err
            time.sleep(ES100I2C.ERROR_DELAY_SEC)
            count += 1

    def write_addr(self, addr, data):
        """ write_addr """
        print("DEBUG: write_addr(%d)" % addr, file=sys.stderr)
        count = 0
        while True:
            try:
                self._device.writeto(self._i2c_address, bytes([data]), start=addr)
                return
            except OSError as err:
                if count > 10:
                    raise ES100I2CError('i2c write 0x%02x: %s' % (addr, err)) from err
            time.sleep(ES100I2C.ERROR_DELAY_SEC)
            count += 1

    def write(self, data):
        """ write """
        print("DEBUG: write(%s)" % data, file=sys.stderr)
        count = 0
        while True:
            try:
                self._device.writeto(self._i2c_address, bytes([data]))
                return
            except OSError as err:
                if count > 10:
                    raise ES100I2CError('i2c write 0x%02x: %s' % (data, err)) from err
            time.sleep(ES100I2C.ERROR_DELAY_SEC)
            count += 1
