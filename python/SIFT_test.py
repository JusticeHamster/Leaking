# import
import numpy as np
import cv2
import os
import shutil
import lktools
# load
settings = lktools.Loader.get_settings()
time_test = settings['time_test']
img_path = settings['img_path']
video_path = settings['video_path']
frame_range = settings['frame_range']
lastn_interval = settings['lastn']
def run_one_frame(normal, src, fgbg):
  # sift alignment
  sift_save = None
  if normal is None:
    sift = src
  else:
    sift, *_ = lktools.SIFT.siftImageAlignment(normal, src)
    sift_save = sift
  # MOG2 BS
  sift = fgbg.apply(sift)
  # Denoise
  if normal is None:
    return cv2.cvtColor(sift, cv2.COLOR_GRAY2RGB)
  else:
    sifts = lktools.Denoise.denoise(sift)
    # to rgb
    sifts = map(lambda img: cv2.cvtColor(img, cv2.COLOR_GRAY2RGB), sifts)
    #
    return tuple(sifts), sift_save
# 计时运行
@lktools.Timer.timer_decorator
def run(name, path):
  capture, h, w, fps = lktools.PreProcess.video_capture_size(path, settings['height'])
  # run
  print('read {path}. total: {frames:.0f} frames'.format(
    path=path, frames=capture.get(cv2.CAP_PROP_FRAME_COUNT)
  ))
  nframes = 0
  # init
  first = None
  lastn = None
  fgbg_first = cv2.createBackgroundSubtractorMOG2()
  if not time_test:
    fgbg_lastn = cv2.createBackgroundSubtractorMOG2()
    fgbg = cv2.createBackgroundSubtractorMOG2()
  # 保存视频的fps与存储位置等
  # fps = 10    #保存视频的FPS，可以适当调整
  fourcc = cv2.VideoWriter_fourcc(*'MJPG')
  # TODO: 读入的图片像素大小需要设置，由于排列方式不固定，因此尚未根据配置文件修改
  videoWriter = cv2.VideoWriter(video_path,fourcc,fps,(1620,960))#最后一个是保存图片的尺寸

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
    frame = cv2.resize(frame, (w, h))
    if first is None:
      first = frame
      lastn = frame
      continue
    if not time_test:
      original = frame
    frame_first, sift_first = run_one_frame(first, frame, fgbg_first)
    if not time_test:
      frame_lastn, sift_lastn = run_one_frame(lastn, frame, fgbg_lastn)
      frame = run_one_frame(None, frame, fgbg)
      line1 = np.hstack((
        original, frame,
        sift_first, frame_first[0],
        sift_lastn, frame_lastn[0]
      ))
      line2 = np.hstack((
        np.zeros(original.shape),
        frame_first[1], frame_first[2],
        frame_first[3], frame_first[3],
        np.zeros(original.shape),
      ))
      cv2.imwrite(
        '{path}/{name}_{n}.jpg'.format(
          path=img_path, name=name, n=nframes
        ),
        np.vstack((line1, line2))
      )
      # 每一帧导入保存的视频中，TODO:取消重新读取保存的图片这一流程
      frame = cv2.imread('{path}/{name}_{n}.jpg'.format(
          path=img_path, name=name, n=nframes
        ))
      videoWriter.write(frame)
      # 更新last
      if nframes % lastn_interval == 0:
        lastn = original
  capture.release()
  # 导出视频
  videoWriter.release()
  cv2.destroyAllWindows()

def main():
  # 清空输出文件夹
  if not time_test:
    if os.path.exists(img_path):
      shutil.rmtree(img_path)
    os.mkdir(img_path)
  for name, video in settings['videos']:
    run(name.split('.')[0], video)
# run
if __name__ == '__main__':
  main()