"""
lktools
"""
import lktools.LoggerFactory

class Checker:
  """
  用于类型、值合法性检查
  """
  def __init__(self, logger):
    self.logger = lktools.LoggerFactory.LoggerFactory.getChild(logger, 'Checker')
    self.dirty = False
    self.containers = {}
    self.asserts = {}

  def add_container(self, name, container):
    self.containers[name] = container

  def add_assert(self, assert_name, assert_func):
    self.asserts[assert_name] = assert_func

  def check(self, name, assert_type):
    def __check(name, assert_type):
      if type(assert_type) == str:
        func = self.asserts.get(assert_type)
        args = (name, self.containers)
      else:
        func = self.asserts.get('type')
        args = (name, assert_type, self.containers)
      if func is None:
        return
      item, s = func(*args)
      if not s:
        self.logger.error(item)
        self.dirty = True
    if isinstance(name, (tuple, list)):
      for n in name:
        __check(n, assert_type)
    elif isinstance(name, str):
      __check(name, assert_type)
    else:
      self.logger.error(f'error attribute name: {name}')
