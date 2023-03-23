#!/usr/bin/env python3

"""
A simple display of the NTP shared memory segment

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import os
import sys
import time
import datetime
import logging

sys.path.insert(0, os.path.abspath('.'))

from wwvb.ntpdriver28 import NTPDriver28, NTPDriver28Error

# based on ...
# https://github.com/ntp-project/ntp/blob/9c75327c3796ff59ac648478cd4da8b205bceb77/util/sht.c

def doit(args):
    """ doit """

    required_format = '%(asctime)s %(name)s %(levelname)s %(message)s'
    logging.basicConfig(format=required_format)
    logging.basicConfig(level=logging.INFO)

    if len(args) > 0:
        try:
            unit = int(args[0])
        except ValueError:
            sys.exit('%s: invalid argument - should be interger' % (args[0]))
    else:
        unit = 2

    try:
        d28 = NTPDriver28(unit=unit, debug=True)
    except NTPDriver28Error as err:
        sys.exit(err)

    while True:
        try:
            d28.load()
            d28.dump()
            time.sleep(1)
        except KeyboardInterrupt:
            break

    del d28

def main(args=None):
    """ main """
    if args is None:
        args = sys.argv[1:]
    doit(args)

if __name__ == '__main__':
    main()
