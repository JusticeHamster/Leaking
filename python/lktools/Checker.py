from lktools import LoggerFactory

class Checker:
  """
  用于类型、值合法性检查
  """
  def __init__(self, name):
    self.logger = LoggerFactory.LoggerFactory(name)()
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
        if func is None:
          return
        func(name, self.containers)
      else:
        func = self.asserts.get('type')
        if func is None:
          return
        func(name, assert_type, self.containers)
    if isinstance(name, (tuple, list)):
      for n in name:
        __check(n, assert_type)
    elif isinstance(name, str):
      __check(name, assert_type)
    else:
      self.logger.error(f'error attribute name: {name}')
