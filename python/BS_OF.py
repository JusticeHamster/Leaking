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
def run_one_frame(normal, src, fgbg, size):
  frame = src
  # optical flow
  flow_rects, _ = lktools.OpticalFlow.optical_flow_rects(normal, frame)
  # sift alignment
  frame, *_ = lktools.SIFT.siftImageAlignment(normal, frame)
  # MOG2 BS
  frame = fgbg.apply(frame)
  # Denoise
  frame = lktools.Denoise.denoise(frame, 'bilater')
  # findObject
  bs_rects = lktools.FindObject.findObject(frame)
  # draw
  src_rects = src.copy()
  lktools.PreProcess.draw_rect(src_rects, size)
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
  first = None
  lastn = None
  fgbg_first = cv2.createBackgroundSubtractorMOG2()
  if not time_test:
    fgbg_lastn = cv2.createBackgroundSubtractorMOG2()
  # 将图像保存为视频
  fourcc = cv2.VideoWriter_fourcc(*'MJPG')
  # fps = 10    #保存视频的FPS，可以适当调整
  # TODO: 读入的图片像素大小需要设置，由于排列方式不固定，因此尚未根据配置文件修改
  # 显示所有结果时的分辨率
  videoWriter = cv2.VideoWriter(
    '{path}/{name}.avi'.format(path=video_path, name=name),
    fourcc,
    fps,
    (1620, 960)
  ) # 最后一个是保存图片的尺寸
  # 只显示原图与双边滤波结果的分辨率
  ''' videoWriter = cv2.VideoWriter(
    '{path}/{name}.avi'.format(path=video_path, name=name),
    fourcc,
    fps,
    (540, 480)
  ) # 最后一个是保存图片的尺寸
  '''
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
    if first is None:
      first = frame
      lastn = frame
      continue
    # 上面是循环变量，下面是正式计算
    # 保存原图
    if not time_test:
      original = frame
    # 处理一帧
    frame_first = run_one_frame(first, frame, fgbg_first, size)
    if not time_test:
      frame_lastn = run_one_frame(lastn, frame, fgbg_lastn, size)
      img = np.hstack((frame_first, frame_lastn))
      cv2.imwrite(
        '{path}/{name}_{n}.jpg'.format(
          path=img_path, name=name, n=nframes
        ),
        img
      )
      # 每一帧导入保存的视频中，uint8
      videoWriter.write(np.uint8(img))
      # 更新last
      if nframes % lastn_interval == 0:
        lastn = original
  capture.release()
  # 导出视频
  videoWriter.release()
  cv2.destroyAllWindows()
# run
if __name__ == '__main__':
  for name, video in settings['videos']:
    run(name, video)