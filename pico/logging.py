"""

logging for micropython - just the bare minimum

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

from pico.datetime import datetime

class logging:
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    level_names = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
         0: 'NOTSET',
    }

    default_format = '%(asctime)s %(name)s %(levelname)s %(message)s'
    default_level = None

    @classmethod
    def basicConfig(cls, format=None, level=None):
        if format:
            cls.default_format = format
        if level:
            cls.default_level = level

    class getLogger:
        def __init__(self, name):
            self._name = name
            self._level = logging.default_level

        def setLevel(self, level):
            """ setLevel()
            :param level: set logging level
            """
            self._level = level

        def critical(self, s, *args):
            """ critical()
            :param s: string to display
            :param *args: additional to display
            """
            if self._level and self._level <= logging.CRITICAL:
                print(self._d(), self._name, self._l(logging.CRITICAL), s % args)

        def error(self, s, *args):
            """ erro()
            :param s: string to display
            :param *args: additional to display
            """
            if self._level and self._level <= logging.ERROR:
                print(self._d(), self._name, self._l(logging.ERROR), s % args)

        def warning(self, s, *args):
            """ warning()
            :param s: string to display
            :param *args: additional to display
            """
            if self._level and self._level <= logging.WARNING:
                print(self._d(), self._name, self._l(logging.WARNING), s % args)

        def info(self, s, *args):
            """ info()
            :param s: string to display
            :param *args: additional to display
            """
            if self._level and self._level <= logging.INFO:
                print(self._d(), self._name, self._l(logging.INFO), s % args)

        def debug(self, s, *args):
            """ debug()
            :param s: string to display
            :param *args: additional to display
            """
            if self._level and self._level <= logging.DEBUG:
                print(self._d(), self._name, self._l(logging.DEBUG), s % args)

        def _d(self):
            """ :meta private: """
            return datetime.utcnow()

        def _l(self, level):
            """ :meta private: """
            try:
                return logging.level_names[level]
            except IndexError:
                return 'UNKNOWN'
