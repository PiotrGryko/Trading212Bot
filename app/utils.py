import logging
import time

logger = logging.getLogger('api')


def expect(func, args, times=7, sleep_t=0.5):
    while times > 0:
        try:
            return func(*args)
        except Exception as e:
            times -= 1
            logger.debug("expect failed - attempts left: %d" % times)
            time.sleep(sleep_t)
            if times == 0:
                raise e


def expect_none(func, args, times=7, sleep_t=0.5):
    while times > 0:
        try:
            return func(*args)
        except Exception as e:
            times -= 1
            logger.debug("expect failed - attempts left: %d" % times)
            time.sleep(sleep_t)
            if times == 0:
                return None
