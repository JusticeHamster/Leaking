"""
lktools
"""
import lktools.LoggerFactory
"""
filesystem
"""
import os

class Checker:
  """
  用于类型、值合法性检查
  """
  def __init__(self, logger, container):
    self.logger = lktools.LoggerFactory.LoggerFactory.getChild(logger, 'Checker')
    self.container = container
    self.dirty = False

  def check(self, name, assert_type, *args):
    def __check(name, assert_type, *args):
      check_t = type(assert_type) == type
      item, s = self.type_test(name, assert_type, *args) if check_t else assert_type(name, *args)
      if not s:
        self.logger.error(item)
        self.dirty = True
      return s
    if isinstance(name, (tuple, list)):
      s = True
      for n in name:
        s = s and __check(n, assert_type, *args)
      return s
    elif isinstance(name, str):
      return __check(name, assert_type, *args)
    else:
      self.logger.error(f'error attribute name: {name}')
      return False

  def exist(self, name):
    item = self.container.get(name)
    if item is None:
      return f'"{name}" must exists', False
    return item, True

  def len_not_zero(self, name):
    item, s = self.exist(name)
    if not s:
      return item, False
    if len(item) == 0:
      return f'size of "{name}" must > 0', False
    return item, True

  def plus(self, name):
    item, s = self.exist(name)
    if not s:
      return item, False
    if not (item > 0):
      return f'"{name}" must > 0', False
    return item, True

  def range(self, name):
    item, s = self.exist(name)
    if not s:
      return item, False
    if len(item) != 2:
      return f'range "{name}" must have and only have 2 elements', False
    if item[0] < 0:
      return f'range {name}[0] must > 0', False
    if item[0] > item[1]:
      return f'range {name}[0] must <= {name}[1]', False
    return item, True

  def within(self, name, _list):
    item, s = self.exist(name)
    if not s:
      return item, False
    def __within(self, name, item, _list):
      if item not in _list:
        return f'"{name}" is "{item}", not in {_list}', False
      return item, True
    if isinstance(item, dict):
      # 如果是dict，只检查values
      item = list(item.values())
    if isinstance(item, (tuple, list)):
      for it in item:
        info, s = __within(self, name, it, _list)
        if not s:
          return info, False
      return item, True
    else:
      return __within(self, name, item, _list)

  def exists_file(self, name):
    item, s = self.exist(name)
    if not s:
      return item, False
    if not os.path.exists(item):
      return f'path "{name}" not exists', False
    return item, True

  def is_dir(self, name):
    item, s = self.exist(name)
    if not s:
      return item, False
    if not os.path.isdir(item):
      return f'path "{name}" is not a directory', False
    return item, True

  def has_file(self, name, file):
    dir_name, s = self.is_dir(name)
    if not s:
      return dir_name, False
    file_name, s = self.exist(file)
    if not s:
      return file_name, False
    path = f'{dir_name}/{file_name}'
    if not os.path.exists(path):
      return f'directory "{dir_name}" has no file: "{file_name}"', False
    return path, True

  def type_test(self, name, assert_type):
    item, s = self.exist(name)
    if not s:
      return item, False
    if type(item) != assert_type:
      return f'{name} must be type {assert_type} but find {type(item)}', False
    return item, True
