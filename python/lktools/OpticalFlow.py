"""
numpy
"""
import numpy as np
"""
opencv
"""
import cv2
"""
lktools
"""
import lktools.Timer
import lktools.LoggerFactory
from lktools.PreProcess import trim_to_rect

logger = lktools.LoggerFactory.LoggerFactory('OpticalFlow').logger

def draw_hsv(flow):
  (h, w) = flow.shape[:2]
  (fx, fy) = (flow[:, :, 0], flow[:, :, 1])
  ang = np.arctan2(fy, fx) + np.pi
  v = np.sqrt(fx * fx + fy * fy)
  hsv = np.zeros((h, w, 3), np.uint8)
  hsv[..., 0] = ang * (90 / np.pi)
  hsv[..., 1] = 0xFF
  hsv[..., 2] = np.minimum(v * 4, 0xFF)
  return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

@lktools.Timer.timer_decorator()
def optical_flow_rects(prev, now, rect, color=(0, 0xFF, 0), thickness=4, limit_size=1, compression_ratio=1):
  """
  Params:
    @prev: 上一帧图片
    @now: 这一帧图片
    @rect: 给定检测的范围
    @color: 标识物体框的颜色
    @thickness: 标识物体框的粗细
    @limit_size: 小于此阈值的物体长宽，不予标识
    @compression_ratio: 识别时的压缩率，越小检测结果越粗糙，速度越快
  Warning:
    rect: two points same as (x1,y1),(x2,y2), and x1 <= x2 & y1 <= y2
  """
  prev = cv2.resize(
    prev, None, None,
    compression_ratio,
    compression_ratio
  )
  now = cv2.resize(
    now, None, None,
    compression_ratio,
    compression_ratio
  )
  prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
  now = cv2.cvtColor(now, cv2.COLOR_BGR2GRAY)
  flow = cv2.calcOpticalFlowFarneback(
    prev, now, None,
    0.5, 5, 15, 3, 5, 1.1,
    cv2.OPTFLOW_FARNEBACK_GAUSSIAN
  )
  flow = cv2.cvtColor(draw_hsv(flow), cv2.COLOR_BGR2GRAY)
  binary = cv2.threshold(flow, 25, 0xFF, cv2.THRESH_BINARY)[1]

  logger.debug('对二值图像进行膨胀')

  binary = cv2.dilate(binary, None, iterations=2)
  _, cnts, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
  )
  rects = []
  for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    r = np.array([[x, y], [(x + w), (y + h)]])
    r = (r / compression_ratio).astype(int)
    r = trim_to_rect(r, rect)
    if r is None:
      continue
    if w > limit_size and h > limit_size:
      rects.append((*map(tuple, r), color, thickness))
  return rects, binary
