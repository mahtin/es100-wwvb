#!/usr/bin/env python3
""" WWVB 60Khz receiver/parser for i2c bus based ES100-MOD on the Raspberry Pi Pico

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import sys
import json

from es100 import ES100
from pico.datetime import datetime

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
    #                       0 0
    #                       S S
    #                       C C
    #                       L K
    #   * * * * * * * * * * * * * * * * * * * *
    #   *                                     *
    #   *                                     * USB
    #   *                                     *
    #   * * * * * * * * * * * * * * * * * * * *
    #   G G                           3   G
    #   P P                           .   N
    #   1 1                           3   D
    #   6 7                           V

    i2c_bus = 1
    i2c_address = 0x32  # 50
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

    try:
        doit(antenna=antenna_choice, irq=es100_irq, en=es100_en, bus=i2c_bus, address=i2c_address, verbose=flag_verbose, debug=flag_debug)
    except KeyboardInterrupt:
        sys.exit('^C')

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
        es = ES100(antenna=None, en=en, irq=irq, bus=bus, address=address, verbose=verbose, debug=debug)
    except Exception as err:
        # can't find device!
        print(err)
        return

    # loop forever - setting the system RTC as you proceed
    while True:
        dt = es.time()
        if dt:
            print('WWVB:',dt, es.system_time(), es.rx_antenna(), es.delta_seconds())

            # set system time
            datetime.setrtc(dt)
