# import
import numpy as np
import time
import cv2
import os

import SIFT
# 读取设置
"""{rpca.settings 格式要求:}
path=XXX
videos=X.mp4;Y.mp4
delay=?     // 视频播放延迟，默认100
height=?    // 视频高度限定，宽度会自动计算，默认192
frame_range=a-b// 取a-b帧，默认0-100
img_path=?  // 图片存取路径，默认tmp/
time_test=? // 是否测试时间，会关闭所有输出，默认false
"""
settings = {}
with open('rpca.settings', encoding='utf-8') as f:
  for line in f.readlines():
    strs = line.split('=')
    settings[strs[0].strip()] = strs[1].strip()
# 设置
full_path = settings['path']
img_path = settings.get('img_path', 'tmp/')
videos = settings['videos']
delay = int(settings.get('delay', 100))
  # 所需视频的高度
height = int(settings.get('height', 192))
frame_range = settings['frame_range']
if frame_range is None:
  frame_range = (0, 100)
else:
  frame_range = tuple(map(lambda s: int(s), frame_range.split('-')))
time_test = False
if settings.get('time_test') == 'true':
  time_test = True
# 将设置中的文件转换为绝对地址
def videos_path(videos):
  return map(
    lambda n: (n, '{path}/{name}'.format(
      path=full_path,
      name=n
    )),
    videos.split(';')
  )
# 运行
def run(name, path):
  if not os.path.exists(path):
    print('no such file: {path}'.format(path=path))
    return
  # init
  capture = cv2.VideoCapture(path)
  # run
  print('read {path}'.format(path=path))
  nframes = 0
  # 放缩
  m = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
  n = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
  scale = height / m
  m = height
  n = int(n * scale)
  # BS
  first = None
  last = None
  sift_fgbg_first = cv2.createBackgroundSubtractorMOG2()
  if not time_test:
    sift_fgbg_last = cv2.createBackgroundSubtractorMOG2()
    fgbg = cv2.createBackgroundSubtractorMOG2()
  while capture.isOpened():
    if nframes >= frame_range[1]:
      break
    success, frame = capture.read()
    if not success:
      break
    nframes += 1
    if nframes < frame_range[0]:
      continue
    frame = cv2.resize(frame, (n, m))
    if first is None:
      first = frame
      last = frame
      continue
    if not time_test:
      img = np.copy(frame)
    #
    siftimg_first, *_ = SIFT.siftImageAlignment(first, frame)
    sift_frame_first = sift_fgbg_first.apply(siftimg_first)
    sift_frame_first = cv2.cvtColor(sift_frame_first, cv2.COLOR_GRAY2RGB)
    if not time_test:
      siftimg_last, *_ = SIFT.siftImageAlignment(last, frame)
      sift_frame_last = sift_fgbg_last.apply(siftimg_last)
      sift_frame_last = cv2.cvtColor(sift_frame_last, cv2.COLOR_GRAY2RGB)
      frame = fgbg.apply(frame)
      frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
      cv2.imwrite(
        '{path}/{name}_{n}.jpg'.format(
          path=img_path, name=name, n=nframes
        ),
        np.hstack((
          img, frame,
          siftimg_first, sift_frame_first,
          siftimg_last, sift_frame_last
        ))
      )
    last = img
  capture.release()
  cv2.destroyAllWindows()
# run
if __name__ == '__main__':
  if not time_test:
    os.mkdir(img_path)
  for name, video in videos_path(videos):
    start = time.perf_counter()
    run(name.split('.')[0], video)
    end = time.perf_counter()
    print('time: {time:.2f}s'.format(time=end - start))