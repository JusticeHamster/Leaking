"""
opencv
"""
import cv2
"""
lktools
"""
import lktools.LoggerFactory

logger = lktools.LoggerFactory.LoggerFactory('PreProcess').logger

def video_capture_size(path, height):
  capture = cv2.VideoCapture(path)
  if not capture.isOpened():
    logger.error(f'{path} not found')
    from sys import exit
    exit(1)
  m = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
  n = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
  fps = capture.get(cv2.CAP_PROP_FPS)
  count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
  scale = height / m
  m = height
  n = int(n * scale)
  return capture, m, n, fps, count

def get_rect_property(size):
  width, height = size
  return (
    # 低处落下相关视频
    # (width // 16, int(height * 2.9) // 4),
    # (width * 15 // 16, height // 2),
    # 高处落下相关视频
    (width // 16, int(height * 2.9) // 4),
    (width * 15 // 16, height // 4),
    (255, 0, 0),
    1, 0
  )

def trim_to_rect(rect1, rect2):
  """
  将rect1缩到rect2内部，裁剪掉外部多余部分
  """
  (x11, y11), (x12, y12), *_ = rect1
  (x21, y21), (x22, y22), *_ = rect2
  if x11 < x21:
    x11 = x21
  if x12 > x22:
    x12 = x22
  if y12 > y21:
    y12 = y21
  if y11 < y22:
    y11 = y22
  if x11 >= x12:
    return
  if y11 >= y12:
    return
  return (x11, y11), (x12, y12)

def rect_in_rect(rect1, rect2):
  """
  判断矩形rect1是否在矩形rect2中。
  """
  logger.warning_times('this func is deprecated, please use trim_to_rect instead')
  (x11, y11), (x12, y12), *_ = rect1
  (x21, y21), (x22, y22), *_ = rect2
  return x11 >= x21 and x12 <= x22 and y12 <= y21 and y11 >= y22

def gray_to_bgr(img):
  """
  cv2.cvtColor(*, cv2.COLOR_GRAY2BGR) helper
  """
  return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def bgr_to_gray(img):
  """
  cv2.cvtColor(*, cv2.COLOR_BGR2GRAY) helper
  """
  return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def draw(frame, rects):
  """
  将rects中的矩形绘制在frame上
  """
  img = frame.copy()
  for rect in rects:
    cv2.rectangle(img, *rect)
  return img
