"""
opencv
"""
import cv2
"""
lktools
"""
import lktools.PreProcess
import lktools.Timer
import lktools.LoggerFactory

logger = lktools.LoggerFactory.LoggerFactory('FindObject').logger

@lktools.Timer.timer_decorator
def findObject(binary, rect):

  logger.debug('计算图像中目标的轮廓并且返回彩色图像')
  _, contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  rects = []
  for c in contours:

    logger.debug('对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值')

    if cv2.contourArea(c) < 20:
      continue
    (x, y, w, h) = cv2.boundingRect(c)

    logger.debug('该函数计算矩形的边界框')

    r = ((x, y), (x + w, y + h))
    if not lktools.PreProcess.rect_in_rect(r, rect):
      continue
    rects.append((*r, (0, 0, 255), 2))
  return rects