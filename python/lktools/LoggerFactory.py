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
      '[%(levelname)-7s] [%(asctime)-15s] [%(filename)s: %(lineno)d, @%(process)d] %(name)s: %(message)s',
      '%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    self.logger = logger

  @staticmethod
  def getChild(logger, name):
    return logger.getChild(name)
