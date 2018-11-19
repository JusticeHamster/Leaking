import numpy as np
import cv2
import time


def draw_hsv(flow):
    (h, w) = flow.shape[:2]
    (fx, fy) = (flow[:, :, 0], flow[:, :, 1])
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx * fx + fy * fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[..., 0] = ang * (180 / np.pi / 2)
    hsv[..., 1] = 0xFF
    hsv[..., 2] = np.minimum(v * 4, 0xFF)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    # cv2.imshow('hsv', bgr)
    return bgr


def run_one_frame(prev, img, rect, color=(0, 0xFF, 0), thickness=4, limit_size=10, compression_ratio=1):
    """
    Params:
        @prev: 上一帧图片
        @img: 这一帧图片
        @rect: 给定检测的范围
        @color: 标识物体框的颜色
        @thickness: 标识物体框的粗细
        @limit_size: 小于此阈值的物体长宽，不予标识
        @compression_ratio: 识别时的压缩率，越小检测结果越粗糙，速度越快
    Warning:
        rect: two points same as (x1,y1),(x2,y2), and x1 <= x2 & y1 <= y2

    """
    src = img.copy()
    prev = cv2.resize(prev.copy(), None, None,
                      compression_ratio, compression_ratio)
    img = cv2.resize(img.copy(), None, None,
                     compression_ratio, compression_ratio)
    (x1, y1), (x2, y2) = rect
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, gray, None, 0.5, 5, 15, 3, 5, 1.1, cv2.OPTFLOW_FARNEBACK_GAUSSIAN)

    gray1 = cv2.cvtColor(draw_hsv(flow), cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray1, 25, 0xFF, cv2.THRESH_BINARY)[1]
    # 对二值图像进行膨胀
    binary = cv2.dilate(binary, None, iterations=2)

    _, cnts, _ = cv2.findContours(
        binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        (x, y, w, h) = cv2.boundingRect(c)
        # if x,y not in rectange, jump it
        if x < x1 or x > x2 or y < y1 or y > y2:
            continue
        if w > limit_size and h > limit_size:
            cv2.rectangle(src, (np.int(x//compression_ratio), np.int(y//compression_ratio)), (np.int(
                (x + w)//compression_ratio), np.int((y + h)//compression_ratio)), color, thickness)
    return binary, src


if __name__ == '__main__':
    import sys
    # screen_size = (270, 480)
    rect = ((20, 20), (500, 900))
    cam = cv2.VideoCapture('../video/water.mp4')
    success, prev = cam.read()
    if success:
        # prev = cv2.resize(prev, screen_size)
        while True:
            success, img = cam.read()
            if not success:
                break
            # img = cv2.resize(img, screen_size)
            binary, ans = run_one_frame(
                prev, img.copy(), rect, compression_ratio=0.6)
            cv2.rectangle(ans, *rect, (0, 0, 0xFF), 2)
            cv2.imshow('Image', ans)
            cv2.imshow('binary', binary)
            prev = img
            cv2.waitKey(10)

    cv2.destroyAllWindows()
