#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python 2/3 compatibility
from __future__ import print_function


import numpy as np
import cv2
import time

count = 0

lk_params = dict(winSize=(22, 22),
                 maxLevel=5,
                 criteria=(cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 20, 0.01))


def draw_flow(img, flow, step=16):

    # from the beginning to position 2 (excluded channel info at position 3)
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(int)
    fx, fy = flow[y, x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), _ in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis


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


def warp_flow(img, flow):
    (h, w) = flow.shape[:2]
    flow = -flow
    flow[:, :, 0] += np.arange(w)
    flow[:, :, 1] += np.arange(h)[:, np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return res


def run_one_frame(prev, img, limit_size=10):
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, gray, None, 0.5, 5, 15, 3, 5, 1.1, cv2.OPTFLOW_FARNEBACK_GAUSSIAN)

    gray1 = cv2.cvtColor(draw_hsv(flow), cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray1, 25, 0xFF, cv2.THRESH_BINARY)[1]
    # 对二值图像进行膨胀
    binary = cv2.dilate(binary, None, iterations=2)
    cv2.imshow('binary', binary)
    _, cnts, _ = cv2.findContours(
        binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        (x, y, w, h) = cv2.boundingRect(c)
        if w > limit_size and limit_size > 10:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0xFF, 0), 4)
    return img


if __name__ == '__main__':
    import sys
    screen_size = (270, 480)
    cam = cv2.VideoCapture('/Users/wzy/Movies/data/water1.mp4')
    success, prev = cam.read()
    if success:
        prev = cv2.resize(prev, screen_size)

        while True:
            success, img = cam.read()
            if not success:
                break
            img = cv2.resize(img, screen_size)
            img = run_one_frame(prev, img, 10)
            cv2.imshow('Image', img)
            prev = img

    cv2.destroyAllWindows()
