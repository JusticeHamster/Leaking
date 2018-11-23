import time
from lktools import Loader

settings = Loader.get_settings()
DEBUG = settings['time_debug']

def timer_decorator(func):
  def wrapper(*args, **kwargs):
    if DEBUG:
      start = time.perf_counter()
    result = func(*args, **kwargs)
    if DEBUG:
      end = time.perf_counter()
      print(f'{func.__name__} time cost: {end - start:.2f}s')
    return result
  return wrapper
