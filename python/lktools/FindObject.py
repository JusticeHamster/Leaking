import cv2

# 计算图像中目标的轮廓并且返回彩色图像
def findObject(gray):
    # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # 图像二值化
    _, binary = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    for c in contours:
        # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
        if cv2.contourArea(c) < 20:
            continue
        (x, y, w, h) = cv2.boundingRect(c) # 该函数计算矩形的边界框
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow('fuck',img)
    # while True:
    #     key = cv2.waitKey(1) & 0xFF
    #     # 按'q'健退出循环
    #     if key == ord('q'):
    #         break
    return img