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
delay = settings['delay']
linux = settings['linux']
OF = settings['OF']
sift = settings['sift']
risk_mode = settings['risk_mode']
# if risk_mode == True
# 标记当前状态是否正常，如果False说明正常，如果出现危险，则将risk_state改为True，
# 并固定lastn为正常帧的最后一帧，接下来的每一帧risk_count+1，直到系统恢复正常或者
# risk_count超过1000帧时reset。
risk_count = 0
risk_state = False
@lktools.Timer.timer_decorator
def run_one_frame(lastn, last, src, fgbg, size):
  frame = src
  # rect
  rect = lktools.PreProcess.get_rect_property(size) 
  # optical flow
  if OF:
    flow_rects, _ = lktools.OpticalFlow.optical_flow_rects(
      last, frame, rect,
      limit_size=limit_size, compression_ratio=compression_ratio
    )
  # sift alignment
  if sift:
    frame, *_ = lktools.SIFT.siftImageAlignment(lastn, frame)
  # MOG2 BS
  frame = fgbg.apply(frame)
  # Denoise
  frame = lktools.Denoise.denoise(frame, 'bilater')
  frame = lktools.Denoise.denoise(frame, 'morph_open')
  frame = lktools.Denoise.denoise(frame, 'dilation')
  frame = lktools.Denoise.denoise(frame, 'dilation')
  frame = lktools.Denoise.denoise(frame, 'erode') 
  # findObject
  bs_rects = lktools.FindObject.findObject(frame, rect)
  # draw
  src_rects = src.copy()
  cv2.rectangle(src_rects, *rect)
  # rects
  rects = bs_rects
  if OF:
    rects.extend(flow_rects)
  # risk
  def risk(r):
    if not risk_mode:
      return
    global risk_state, risk_count
    if r:
      if not risk_state:
        risk_state = True
        risk_count = 1
      else:
        risk_count = risk_count + 1
    else:
      if risk_state:
        risk_state = False
        risk_count = 0
  r = len(rects) != 0
  for rect in rects:
    cv2.rectangle(src_rects, *rect)
    risk(r)
  risk(r)
  return src_rects
# 计时运行
@lktools.Timer.timer_decorator
def run(name, path):
  capture, h, w, fps = lktools.PreProcess.video_capture_size(path, settings['height'])
  size = (w, h)
  # run
  print(f'read {path}. from frame {frame_range[0]} to {frame_range[1]}')
  nframes = 0
  # init
  last = None
  lastn = None
  risk_state = False
  fgbg = cv2.createBackgroundSubtractorMOG2()
  # 将图像保存为视频
  if not time_test:
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    videoWriter = cv2.VideoWriter(
      f'{video_path}/{name}.avi',
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
    if time_test:
      cv2.imshow(f'{name}', frame)
      cv2.waitKey(delay)
    else:
      cv2.imwrite(
        f'{img_path}/{name}_{nframes}.jpg',
        frame
      )
      # 每一帧导入保存的视频中，uint8
      videoWriter.write(np.uint8(frame))
    # 更新last
    if nframes % lastn_interval == 0:
      if risk_mode and risk_state == False and risk_count < 1000:
        pass
      else:
        lastn = original
      fgbg = cv2.createBackgroundSubtractorMOG2()
      fgbg.apply(lastn)
    last = original
  capture.release()
  # 导出视频
  if not time_test:
    videoWriter.release()
  if not linux:
    cv2.destroyAllWindows()
# run
if __name__ == '__main__':
  for name, video in settings['videos']:
    run(name, video)
