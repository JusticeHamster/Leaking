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
    return lktools.FindObject.findObject(sift)
  else:
    # 仅显示原图与滤波后结果
    # sift = lktools.Denoise.denoise(sift,which='bilater')
    # sift = lktools.FindObject.findObject(sift)
    # return sift, sift_save
    # 显示所有结果
    sifts = lktools.Denoise.denoise(sift)
    sifts = map(lambda img: lktools.FindObject.findObject(img), sifts)
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
  # 将图像保存为视频
  fourcc = cv2.VideoWriter_fourcc(*'MJPG')
  # fps = 10    #保存视频的FPS，可以适当调整
  # TODO: 读入的图片像素大小需要设置，由于排列方式不固定，因此尚未根据配置文件修改
  # 显示所有结果时的分辨率
  videoWriter = cv2.VideoWriter(video_path,fourcc,fps,(1620,960))#最后一个是保存图片的尺寸
  # 只显示原图与双边滤波结果的分辨率
  # videoWriter = cv2.VideoWriter(video_path,fourcc,fps,(540,480))#最后一个是保存图片的尺寸
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
      # 显示所有结果
      line1 = np.hstack((
        original, frame,
        sift_first, frame_first[0],
        sift_lastn, frame_lastn[0]
      ))
      line2 = np.hstack((
        frame_first[1], frame_first[2],
        frame_first[3], frame_first[4],
        frame_first[5], frame_first[6],
      ))
      cv2.imwrite(
        '{path}/{name}_{n}.jpg'.format(
          path=img_path, name=name, n=nframes
        ),
        np.vstack((line1, line2))
      )
      # 只显示原图与滤波后结果
      # line = np.hstack((
      #   original,frame_first
      # ))
      # cv2.imwrite(
      #   '{path}/{name}_{n}.jpg'.format(
      #     path=img_path, name=name, n=nframes
      #   ),
      #   line
      # )
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