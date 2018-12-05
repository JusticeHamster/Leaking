import logging
import sys

class LoggerFactory:
  """
  创建默认设置好的logger
  """
  def __init__(self, name, level=logging.WARN, stream=sys.stdout):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter(
      '%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(name)s %(message)s',
      '%a %d %b %Y %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    self.logger = logger

  @staticmethod
  def getChild(logger, name):
    return logger.getChild(name)
