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

class LoggerFactory:
  """
  创建默认设置好的logger
  """
  def __init__(self, name, level=None, stream=sys.stdout):
    """
    注意：
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
    LoggerFactory.lock.acquire()
    if LoggerFactory.__default_logger is None:
      LoggerFactory.__default_logger = LoggerFactory('Default').logger
    LoggerFactory.lock.release()
    return LoggerFactory.__default_logger
