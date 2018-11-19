import numpy as np
import cv2

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

def optical_flow_rects(prev, now, limit_size=10):
  prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
  now = cv2.cvtColor(now, cv2.COLOR_BGR2GRAY)
  flow = cv2.calcOpticalFlowFarneback(
    prev, now, None,
    0.5, 5, 15, 3, 5, 1.1,
    cv2.OPTFLOW_FARNEBACK_GAUSSIAN
  )
  flow = cv2.cvtColor(draw_hsv(flow), cv2.COLOR_BGR2GRAY)
  binary = cv2.threshold(flow, 25, 0xFF, cv2.THRESH_BINARY)[1]
  # 对二值图像进行膨胀
  binary = cv2.dilate(binary, None, iterations=2)
  _, cnts, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
  )
  rects = []
  for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    if w > limit_size and h > limit_size:
      rects.append(((x, y), (x + w, y + h), (0, 0xFF, 0), 4))
  return rects, binary
