import cv2

def video_capture_size(path, height):
  capture = cv2.VideoCapture(path)
  if not capture.isOpened():
    raise RuntimeError('{path} not found'.format(path=path))
  m = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
  n = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
  fps = capture.get(cv2.CAP_PROP_FPS)
  scale = height / m
  m = height
  n = int(n * scale)
  return capture, m, n, fps

def get_rect_property(size):
  width, height = size
  return (
    (width // 16, height * 5 // 6),
    (width - width // 16, height // 3),
    (255, 0, 0),
    1, 0
  )

def draw_rect(img, size):
  return cv2.rectangle(img, *get_rect_property(size))

def gray_to_rgb(img):
  return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

def bgr_to_gray(img):
  return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)