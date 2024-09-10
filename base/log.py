import logging
import sys
from logging.handlers import TimedRotatingFileHandler

import colorlog

BASIC_FORMAT = '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(funcName)s - %(message)s'
COLOR_FORMAT = '%(log_color)s%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
DATE_FORMAT = None
basic_formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
color_formatter = colorlog.ColoredFormatter(COLOR_FORMAT, DATE_FORMAT)


class MaxFilter:
    def __init__(self, max_level):
        self.max_level = max_level

    def filter(self, record):
        if record.levelno <= self.max_level:
            return True


class EnhancedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)

    def computeRollover(self, currentTime: int):
        """
        Work out the rollover time based on the specified time.
        """
        if self.when == 'MIDNIGHT' or self.when.startswith('W'):
            return super().computeRollover(currentTime)
        return currentTime - currentTime % self.interval + self.interval


chlr = logging.StreamHandler(stream=sys.stdout)
chlr.setFormatter(color_formatter)
chlr.setLevel('INFO')
chlr.addFilter(MaxFilter(logging.INFO))

ehlr = logging.StreamHandler(stream=sys.stderr)
ehlr.setFormatter(color_formatter)
ehlr.setLevel('WARNING')

fhlr = EnhancedRotatingFileHandler('log/server', when='H', interval=1, backupCount=24*7)
fhlr.setFormatter(basic_formatter)
fhlr.setLevel('DEBUG')

# 自行调用 + 模组调用
logger = logging.getLogger()
logger.setLevel('INFO')  # 改成 DEBUG 之后，模组自身调用的 logger 也会输出
logger.addHandler(fhlr)

# 模组调用: apprise
logger = logging.getLogger('apprise')
logger.addHandler(fhlr)

# 自行调用
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(chlr)
logger.addHandler(ehlr)
