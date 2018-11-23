# import
import numpy as np
import cv2
import lktools
# load
settings = lktools.Loader.get_settings()
time_test = settings['time_test']
img_path = settings['img_path']
video_path = settings['video_path']
frame_range = settings['frame_range']
lastn_interval = settings['lastn']
fps = settings['fps']
limit_size = settings['limit_size']
compression_ratio = settings['compression_ratio']
linux = settings['linux']
@lktools.Timer.timer_decorator
def run_one_frame(lastn, last, src, fgbg, size):
  frame = src
  # rect
  rect = lktools.PreProcess.get_rect_property(size)
  # optical flow
  flow_rects, _ = lktools.OpticalFlow.optical_flow_rects(
    last, frame, rect,
    limit_size=limit_size, compression_ratio=compression_ratio
  )
  # sift alignment
  # frame, *_ = lktools.SIFT.siftImageAlignment(lastn, frame)
  # MOG2 BS
  frame = fgbg.apply(frame)
  # Denoise
  frame = lktools.Denoise.denoise(frame, 'bilater')
  # findObject
  bs_rects = lktools.FindObject.findObject(frame, rect)
  # draw
  src_rects = src.copy()
  cv2.rectangle(src_rects, *rect)
  for rect in (*flow_rects, *bs_rects):
    cv2.rectangle(src_rects, *rect)
  return src_rects
# 计时运行
@lktools.Timer.timer_decorator
def run(name, path):
  capture, h, w, fps = lktools.PreProcess.video_capture_size(path, settings['height'])
  size = (w, h)
  # run
  print('read {path}. from frame {frames[0]} to {frames[1]}'.format(
    path=path, frames=frame_range
  ))
  nframes = 0
  # init
  last = None
  lastn = None
  fgbg = cv2.createBackgroundSubtractorMOG2()
  # 将图像保存为视频
  fourcc = cv2.VideoWriter_fourcc(*'MJPG')
  videoWriter = cv2.VideoWriter(
    '{path}/{name}.avi'.format(path=video_path, name=name),
    fourcc,
    fps,
    size # WARNING：尺寸必须与图片的尺寸一致，否则保存后无法播放。
  )
  # 对每一帧
  while capture.isOpened():
    if nframes >= frame_range[1]:
      break
    success, frame = capture.read()
    if not success:
      break
    nframes += 1
    if nframes < frame_range[0]:
      continue
    frame = cv2.resize(frame, size)
    if last is None:
      last = frame
      lastn = frame
      continue
    # 上面是循环变量，下面是正式计算
    # 保存原图
    original = frame
    frame = run_one_frame(lastn, last, frame, fgbg, size)
    if not time_test:
      cv2.imwrite(
        '{path}/{name}_{n}.jpg'.format(
          path=img_path, name=name, n=nframes
        ),
        frame
      )
    # 每一帧导入保存的视频中，uint8
    videoWriter.write(np.uint8(frame))
    # 更新last
    if nframes % lastn_interval == 0:
      lastn = original
      fgbg = cv2.createBackgroundSubtractorMOG2()
      fgbg.apply(lastn)
  capture.release()
  # 导出视频
  videoWriter.release()
  if not linux:
    cv2.destroyAllWindows()
# run
if __name__ == '__main__':
  for name, video in settings['videos']:
    run(name, video)
