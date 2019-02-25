"""
log
"""
import logging
"""
system
"""
import sys
"""
lktools
"""
import lktools.Loader
"""
lock
"""
import threading
"""
partial
"""
import functools

class LoggerFactory:
  """
  创建默认设置好的logger
  """
  def __init__(self, name, level=None, stream=sys.stdout):
    """
    注意:
      level如果为None，则会默认从settings中读取。

      但如果是从Loader中调用的Logger.init，则会循环调用，所以在这种情况下请提供level
    """
    if level is None:
      settings = lktools.Loader.get_settings()
      level = settings['debug_level']
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter(
      '[%(levelname)-7s] [%(name)-12s] %(message)s [%(filename)s: %(lineno)d, @%(process)d] [%(asctime)s]',
      '%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    """
    提供额外方法

    注意: 由于是string hash存储，所以如果字符串相同
    会被视作同一个打印请求，计数

    debug_times:
      提示用户debug信息，但只重复n次，n可设置
    warning_times:
      提示用户warning信息，但只重复n次，n可设置
    counter:
      记录是每条信息的出现次数
    """
    self.counter = {}

    def XXX_times(func, info, n=1):
      count = self.counter.get(info, 0)
      if count >= n:
        return
      func(info)
      self.counter[info] = count + 1

    logger.warning_times = functools.partial(XXX_times, logger.warning)
    logger.debug_times   = functools.partial(XXX_times, logger.debug)

    """
    提供打印traceback的功能
    """
    def __error_tb(func, error):
      import traceback
      tb = '\n{}'.format(''.join(traceback.format_tb(error.__traceback__)))
      func(tb)
      func(error)

    logger.error_tb = functools.partial(__error_tb, logger.error)

    self.logger = logger

  @staticmethod
  def getChild(logger, name):
    return logger.getChild(name)

  """
  default Logger的线程锁
  """
  lock = threading.Lock()
  __default_logger = None

  @staticmethod
  def default():
    if LoggerFactory.__default_logger is None:
      LoggerFactory.lock.acquire()
      if LoggerFactory.__default_logger is None:
        LoggerFactory.__default_logger = LoggerFactory('Default').logger
      LoggerFactory.lock.release()
    return LoggerFactory.__default_logger
