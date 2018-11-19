import time

DEBUG = False

def timer_decorator(func):
  def wrapper(*args, **kwargs):
    if DEBUG:
      start = time.perf_counter()
    result = func(*args, **kwargs)
    if DEBUG:
      end = time.perf_counter()
      print('{func} time cost: {time:.2f}s'.format(func=func.__name__, time=end - start))
    return result
  return wrapper
