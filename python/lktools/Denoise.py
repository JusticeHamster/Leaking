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

logger = lktools.LoggerFactory.LoggerFactory('Denoise').logger

@lktools.Timer.timer_decorator()
def denoise(img, which=None, args=None):
  """
  四个不同的滤波器
  """
  def mean(img, args=(5, 5)):
    logger.debug('均值滤波')
    return cv2.blur(img, args)
  def guassian(img, args=((5, 5), 0)):
    logger.debug('高斯滤波')
    return cv2.GaussianBlur(img,*args)
  def median(img, args=5):
    logger.debug('中值滤波')
    return cv2.medianBlur(img, args)
  def bilater(img, args=(9, 75, 75)):
    logger.debug('双边滤波')
    return cv2.bilateralFilter(img,*args)
  def morph_open(img, args=(3, 3)):
    logger.debug('形态学处理——开运算')
    logger.debug('定义结构元素')

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,args)

    logger.debug('图像二值化')

    _, binary = cv2.threshold(img,64,255,cv2.THRESH_BINARY)

    logger.debug('形态学腐蚀')

    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    return binary
  def dilation(img, args=((5, 5), 1)):
    kernel = np.ones(args[0],np.uint8)
    return cv2.dilate(img, kernel, iterations=args[1])
  def erode(img, args=((5, 5), 2)):
    kernel = np.ones(args[0],np.uint8)
    return cv2.erode(img, kernel, iterations=args[1])

  denoise_funcs = {
    'mean':           mean,
    'guassian':       guassian,
    'median':         median,
    'bilater':        bilater,
    'morph_open':     morph_open,
    'dilation':       dilation,
    'erode':          erode,
  }
  if which is None:
    return map(lambda f: f(img), denoise_funcs.values())
  else:
    func = denoise_funcs.get(which)
    if func is None:
      return img
    if args is None:
      return func(img)
    else:
      return func(img, args)