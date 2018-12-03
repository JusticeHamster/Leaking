import cv2

def video_capture_size(path, height):
  capture = cv2.VideoCapture(path)
  if not capture.isOpened():
    raise RuntimeError(f'{path} not found')
  m = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
  n = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
  fps = capture.get(cv2.CAP_PROP_FPS)
  count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
  scale = height / m
  m = height
  n = int(n * scale)
  return capture, m, n, fps, count

def get_rect_property(size):
  width, height = size
  return (
    (width // 16, height * 5 // 6),
    (width * 15 // 16, height // 6),
    (255, 0, 0),
    1, 0
  )

def rect_in_rect(rect1, rect2):
  """
  判断矩形rect1是否在矩形rect2中。
  """
  (x11, y11), (x12, y12) = rect1
  (x21, y21), (x22, y22), *_ = rect2
  return x11 >= x21 and x12 <= x22 and y12 <= y21 and y11 >= y22

def gray_to_rgb(img):
  """
  cv2.cvtColor(*, cv2.COLOR_GRAY2RGB) helper
  """
  return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

def bgr_to_gray(img):
  """
  cv2.cvtColor(*, cv2.COLOR_BGR2GRAY) helper
  """
  return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def draw(frame, rects):
  """
  将rects中的矩形绘制在frame上
  """
  img = frame.copy()
  for rect in rects:
    cv2.rectangle(img, *rect)
  return img
