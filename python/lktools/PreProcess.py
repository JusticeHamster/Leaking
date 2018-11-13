import cv2

def video_capture_size(path, height):
  capture = cv2.VideoCapture(path)
  m = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
  n = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
  fps = capture.get(cv2.CAP_PROP_FPS)
  scale = height / m
  m = height
  n = int(n * scale)
  return capture, m, n, fps