import numpy as np
import cv2
import matplotlib.pyplot as plt
########     四个不同的滤波器    #########
img = cv2.imread('frash.jpg')

# 均值滤波
img_mean = cv2.blur(img, (5,5))
print("均值滤波")
# 高斯滤波
img_Guassian = cv2.GaussianBlur(img,(5,5),0)
print("高斯滤波")
# 中值滤波
img_median = cv2.medianBlur(img, 5)
print("中值滤波")
# 双边滤波
img_bilater = cv2.bilateralFilter(img,9,75,75)
print("双边滤波")
# 展示不同的图片
titles = ['srcImg','mean', 'Gaussian', 'median', 'bilateral']
imgs = [img, img_mean, img_Guassian, img_median, img_bilater]

for i in range(5):
    plt.subplot(2,3,i+1)#注意，这和matlab中类似，没有0，数组下标从1开始
    plt.imshow(imgs[i])
    plt.title(titles[i])
plt.show()