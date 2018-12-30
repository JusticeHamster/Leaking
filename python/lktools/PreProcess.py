"""
opencv
"""
import cv2
"""
numpy
"""
import numpy
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

def subtraction(mat1, mat2, distance=0):
  """
  两帧做差（保证不溢出），把距离小于distance的置零，返回。
  """
  mat = numpy.abs(mat1.astype(numpy.int8) - mat2.astype(numpy.int8))
  if distance > 0:
    mat[mat < distance] = 0
  return mat.astype(numpy.uint8)

def trim_to_rect(rect1, rect2):
  """
  将rect1缩到rect2内部，裁剪掉外部多余部分
  rect1与rect2为一个矩形的任意两个对角点
  """
  def min_max(rect):
    (x1, y1), (x2, y2), *_ = rect
    if x1 == x2 or y1 == y2:
      return
    if x1 < x2:
      x_min = x1
      x_max = x2
    else:
      x_min = x2
      x_max = x1
    if y1 < y2:
      y_min = y1
      y_max = y2
    else:
      y_min = y2
      y_max = y1
    return (x_min, y_min), (x_max, y_max)
  mm1 = min_max(rect1)
  if mm1 is None:
    return
  mm2 = min_max(rect2)
  if mm2 is None:
    return
  (x11, y11), (x12, y12) = mm1
  (x21, y21), (x22, y22) = mm2
  if x11 < x21:
    x11 = x21
  if x12 > x22:
    x12 = x22
  if y11 < y21:
    y11 = y21
  if y12 > y22:
    y12 = y22
  if x11 >= x12:
    return
  if y11 >= y12:
    return
  return (x11, y11), (x12, y12)

def rect_wh(rect):
  """
  计算一个矩形的宽高比
  """
  (x0, y0), (x1, y1), *_ = rect
  return abs((x0 - x1) / (y0 - y1))

def point_in_rect(point, rect):
  """
  判断一个点是否在一个矩形中

  若是，返回点在矩形中的相对坐标
  否则返回None
  """
  leftdown, rightup = rect
  x, y = point
  if x < leftdown[0] or y < leftdown[1]:
    return
  if x > rightup[0] or y > rightup[1]:
    return
  return x - leftdown[0], y - leftdown[1]

def rect_in_rect(rect1, rect2):
  """
  判断矩形rect1是否在矩形rect2中。
  矩形点有要求，不支持任意的两个对角点。
  """
  logger.warning_times('this func is deprecated, please use trim_to_rect instead')
  (x11, y11), (x12, y12), *_ = rect1
  (x21, y21), (x22, y22), *_ = rect2
  return x11 >= x21 and x12 <= x22 and y12 <= y21 and y11 >= y22

def gray_to_bgr(img):
  """
  cv2.cvtColor(*, cv2.COLOR_GRAY2BGR) helper
  """
  if img is None:
    return
  return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def bgr_to_gray(img):
  """
  cv2.cvtColor(*, cv2.COLOR_BGR2GRAY) helper
  """
  if img is None:
    return
  return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def bgr_to_hsv(img):
  """
  cv2.cvtColor(*, cv2.COLOR_BGR2HSV) helper
  """
  if img is None:
    return
  return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def draw(frame, rects):
  """
  将rects中的矩形绘制在frame上
  """
  img = frame.copy()
  for rect in rects:
    cv2.rectangle(img, *rect)
  return img
