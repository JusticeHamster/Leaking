import logging
import sys

class LoggerFactory:
  """
  创建默认设置好的logger
  """
  def __init__(self, name, stream=sys.stdout):
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARN)
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.WARN)
    formatter = logging.Formatter(
      '%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(name)s %(message)s',
      '%a %d %b %Y %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    self.logger = logger

  def __call__(self):
    return self.logger