"""
time
"""
import time
"""
lktools
"""
import lktools.Loader
import lktools.LoggerFactory

settings   = lktools.Loader.get_settings()
time_debug = settings['time_debug']
logger     = lktools.LoggerFactory.LoggerFactory('Timer').logger

def timer_decorator(show=None, start_info=None, end_info=None):
  def _timer_decorator(func):
    _show = time_debug if show is None else show
    def wrapper(*args, **kwargs):
      if _show:
        start = time.perf_counter()
        if start_info:
          start_info(start, args, kwargs)
        else:
          logger.info(f'"{func.__name__}" start...')
      result = func(*args, **kwargs)
      if _show:
        end = time.perf_counter()
        if end_info:
          end_info(result, start, end, args, kwargs)
        else:
          logger.info(f'"{func.__name__}" time cost: {end - start:.2f}s')
      return result
    return wrapper
  return _timer_decorator
