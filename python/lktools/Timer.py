import time

def timer_decorator(func):
  def wrapper(*args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    print('{func} time cost: {time:.2f}s'.format(func=func.__name__, time=end - start))
    return result
  return wrapper
