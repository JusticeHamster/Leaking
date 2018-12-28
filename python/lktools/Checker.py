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
    if isinstance(name, (tuple, list)):
      for n in name:
        __check(n, assert_type, *args)
    elif isinstance(name, str):
      __check(name, assert_type, *args)
    else:
      self.logger.error(f'error attribute name: {name}')

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

  def debug_level(self, name):
    item, s = self.exist(name)
    if not s:
      return item, False
    debug_list = ('debug', 'info', 'warn', 'error', 'critical')
    if item not in debug_list:
      return f'"{name}" was "{item}", not in {debug_list}', False
    return item, True

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
