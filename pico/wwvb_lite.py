#!/usr/bin/env python3
""" WWVB 60Khz receiver/parser for i2c bus based ES100-MOD on the Raspberry Pi Pico

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import sys
import json

import utime
from machine import Timer

from es100 import ES100
from pico.datetime import datetime, timezone
from pico.logging import logging
from pico.oled_display import OLEDDisplay128x64

MY_LOCATION = [37.363056, -121.928611, 18.9]  # SJC Airport

def wwvb_lite():
    """ wwvb_lite()
    """

    # Raspberry Pi Pico wiring diagram.
    # I2C bus 1 is on physical pins 9 & 10 (called GP6 & GP7)
    # GPIO for IRQ and Enable are physical pins 21 & 22 (called GP16 * GP17)
    #
    #                       I I
    #                       2 2
    #                       C C
    #                       1 1
    #                       - -
    #                       S S
    #                       C D
    #                       L A
    #   * * * * * * * * * * * * * * * * * * * *
    #   *                                     *
    #   *    Raspberry Pi Pico (or Pico W)    * USB
    #   *                                     *
    #   * * * * * * * * * * * * * * * * * * * *
    #   G G                           3   G
    #   P P                           .   N
    #   1 1                           3   D
    #   6 7                           V

    i2c_bus = 1
    i2c_address = 0x32  # 50 decimal == 0x32 hex
    flag_debug = False
    flag_verbose = False
    es100_irq = 16
    es100_en = 17
    # our_location_name = ''
    # our_location = MY_LOCATION[:2]
    # our_masl = MY_LOCATION[2]
    # flag_enable_nighttime = False
    # flag_force_tracking = False
    antenna_choice = None

    try:
        with open('pico/config.json', 'r', encoding="utf-8") as fd:
            config = json.load(fd)
        print('config.json: loaded')
    except:
        config = {}

    if 'wwvb.station' in config:
        station = config['wwvb.station']
        # our_location_name = config[station + '.' + 'name']
        # our_location = config[station + '.' + 'location']
        # our_location = convert_location(our_location)
        # our_masl = config[station + '.' + 'masl']
        antenna_choice = config[station + '.' + 'antenna']

    if 'wwvb.bus' in config:
        i2c_bus = config['wwvb.bus']
    if 'wwvb.address' in config:
        i2c_address = config['wwvb.address']
    if 'wwvb.irq' in config:
        es100_irq = config['wwvb.irq']
    if 'wwvb.en' in config:
        es100_en = config['wwvb.en']
    # if 'wwvb.nighttime' in config:
    #     flag_enable_nighttime = config['wwvb.nighttime']
    # if 'wwvb.tracking' in config:
    #     flag_enable_nighttime = config['wwvb.tracking']
    if 'debug.debug' in config:
        flag_debug = config['debug.debug']
    if 'debug.verbose' in config:
        flag_verbose = config['debug.verbose']

    # we want any warnings - there should be very few!
    logging.basicConfig(level=logging.WARNING)

    try:
        doit(antenna=antenna_choice, irq=es100_irq, en=es100_en, bus=i2c_bus, address=i2c_address, verbose=flag_verbose, debug=flag_debug)
    except KeyboardInterrupt:
        print('^C - exiting!')
        sys.exit(0)

class SimpleOLED:
    """ SimpleOLED

    Text based display of WWVB data
    """

    _d = None
    _ms_start = None
    _timer = None

    @classmethod
    def _mycallback(cls, t):
        """ _mycallback() """
        if SimpleOLED._timer is None or SimpleOLED._ms_start is None:
            # should not have been called
            return
        dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        SimpleOLED._d.datetime(dt)
        percent = ((utime.ticks_ms() - SimpleOLED._ms_start)/((134+10)*1000.0)) % 1.0
        SimpleOLED._d.progress_bar(percent, 0, 16)

    def __init__(self):
        """ __init__ """
        self._d = OLEDDisplay128x64()

        # needed for callback
        SimpleOLED._ms_start = utime.ticks_ms()
        SimpleOLED._d = self._d

        SimpleOLED._timer = Timer(-1)
        SimpleOLED._timer.init(period=100, mode=Timer.PERIODIC, callback=SimpleOLED._mycallback)

    def __del__(self):
        if SimpleOLED._timer:
            # kill the timer
            SimpleOLED._timer.deinit()
            SimpleOLED._timer = None
            SimpleOLED._ms_start = None

    def background(self):
        """ background() """
        self._d.background()
        self._d.datetime(None)
        self._d.progress_bar(0.0, 0, 16)
        self._d.text('Ant:', 0, 24)
        self._d.text('Delta:', 0, 32)
        self._d.text('DST:', 0, 40)
        self._d.text('Leap:', 0, 48)
        self._d.text('Count:', 0, 56)

    def update(self, ant, delta, dst, leap):
        """ update() """
        self._d.text('Ant:   %s' % (ant), 0, 24)
        self._d.text('Delta: %5.3f' % (delta), 0, 32)
        self._d.text('DST:   %s' % (dst), 0, 40)
        self._d.text('Leap:  %s' % (leap), 0, 48)

    def update_counts(self, successes, loops):
        """ update_counts() """
        self._d.text('Count: %d/%d' % (successes, loops), 0, 56)

    def reset_timer(self):
        """ reset_timer() """
        SimpleOLED._ms_start = utime.ticks_ms()

def doit(antenna, irq, en, bus, address, verbose=False, debug=False):
    """ doit()
    :param en: Enable pin number
    :param irq: IRQ pin number
    :param bus: I2C bus number
    :param address: I2C address number
    :param verbose: Verbose level
    :param debug: Debug level
    :param verbose: Verbose level

    No frills loop to operate the ES100-MOD on the Raspberry Pi
    """
    try:
        es = ES100(antenna=antenna, en=en, irq=irq, bus=bus, address=address, verbose=verbose, debug=debug)
    except Exception as err:
        # can't find device!
        print(err)
        return

    count_successes = 0
    count_loops = 0

    d = SimpleOLED()
    d.background()

    # loop forever - setting the system RTC as we proceed
    while True:
        d.reset_timer()

        dt = es.time(tracking=False)
        if dt:
            print('WWVB:',dt, es.system_time(), es.rx_antenna(), es.delta_seconds())

            # set system time
            datetime.setrtc(dt)

            count_successes += 1
            d.update(es.rx_antenna(), es.delta_seconds(), es.is_presently_dst(), es.leap_second())

        count_loops += 1
        d.update_counts(count_successes, count_loops)
