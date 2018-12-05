import numpy as np
import cv2
import matplotlib.pyplot as plt
from lktools import Timer
from lktools import LoggerFactory

logger = LoggerFactory.LoggerFactory('Denoise').logger

@Timer.timer_decorator
def denoise(img, which=None):
  """
  四个不同的滤波器
  """

  logger.debug('均值滤波')

  def mean(img):
    return cv2.blur(img, (5,5))

  logger.debug('高斯滤波')

  def guassian(img):
    return cv2.GaussianBlur(img,(5,5),0)

  logger.debug('中值滤波')

  def median(img):
    return cv2.medianBlur(img, 5)

  logger.debug('双边滤波')

  def bilater(img):
    return cv2.bilateralFilter(img,9,75,75)

  logger.debug('形态学处理——开运算')

  def morph_open(img):

    logger.debug('定义结构元素')

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3))

    logger.debug('图像二值化')

    _, binary = cv2.threshold(img,64,255,cv2.THRESH_BINARY)

    logger.debug('形态学腐蚀')

    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    return binary
  def dilation(img):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(img,kernel,iterations = 1)

  def erode(img):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(img,kernel,iterations = 2)

  denoise_funcs = {
    'original':       lambda img: img,
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
    return denoise_funcs[which](img)