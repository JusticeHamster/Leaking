import numpy as np
import cv2
import matplotlib.pyplot as plt

denoise_funcs = None

def denoise(img, which=None):
  ########     四个不同的滤波器    #########
  # 均值滤波
  def mean(img):
    return cv2.blur(img, (5,5))
  # 高斯滤波
  def guassian(img):
    return cv2.GaussianBlur(img,(5,5),0)
  # 中值滤波
  def median(img):
    return cv2.medianBlur(img, 5)
  # 双边滤波
  def bilater(img):
    return cv2.bilateralFilter(img,9,75,75)
  #
  global denoise_funcs
  if denoise_funcs is None:
    denoise_funcs = {
      'original': lambda img: img,
      'mean': mean,
      'guassian': guassian,
      'median': median,
      'bilater': bilater,
    }
  if which is None:
    return map(lambda f: f(img), denoise_funcs.values())
  else:
    return denoise_funcs[which](img)