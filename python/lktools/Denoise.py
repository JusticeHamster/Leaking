import numpy as np
import cv2
import matplotlib.pyplot as plt

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
  # 形态学处理
  def morph1(img):
    # 定义结构元素
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    # 图像二值化
    _, binary = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    # 形态学腐蚀
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    return binary
  def morph2(img):
    # 定义结构元素
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    # 图像二值化
    _, binary = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    # 形态学腐蚀两次
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    return binary
  denoise_funcs = {
    'original': lambda img: img,
    'mean': mean,
    'guassian': guassian,
    'median': median,
    'bilater': bilater,
    'morph1': morph1,
    'morph2': morph2,
  }
  if which is None:
    return map(lambda f: f(img), denoise_funcs.values())
  else:
    return denoise_funcs[which](img)