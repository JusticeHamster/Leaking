# import
import numpy as np
import cv2
import lktools
class BSOFModel:
  """
  整个模型
  """
  def __init__(self):
    self.settings = lktools.Loader.get_settings()
    self.judge_cache = None
    self.videoWriter = None
    self.clear()

  def __getattribute__(self, name):
    """
    如果self.NAME访问时，self不含属性NAME，则会在settings(在配置文件json中定义)中查找。
    所以只要self和settings中含有同名属性就会报错。

    请修复。

    例如：
      json文件中：  { "lastn": 10 }
      代码中：      self.lastn = frame
    """
    try:
      obj = super().__getattribute__(name)
    except:
      return super().__getattribute__('settings').get(name)
    else:
      setting = super().__getattribute__('settings').get(name)
      if setting is None:
        return obj
      else:
        print(BSOFModel.__getattribute__.__doc__)
        from sys import exit
        exit(-1)

  @lktools.Timer.timer_decorator
  def catch_abnormal(self, src, size):
    """
    对一帧图像进行处理，找到异常就用框圈出来。

    Args:
      src:    原图
      size:   图片尺寸，生成框使用

    Self:
      lastn:  前N帧图片，用于对齐
      last:   上一帧图片，用于光流法寻找移动物体
      fgbg:   BackgroundSubtractionMOG2方法使用的一个类

    Returns:
      rects:  框的list
    """
    frame = src
    # rect
    rect = lktools.PreProcess.get_rect_property(size) 
    # optical flow
    if self.OF:
      flow_rects, _ = lktools.OpticalFlow.optical_flow_rects(
        self.last, frame, rect,
        limit_size=self.limit_size, compression_ratio=self.compression_ratio
      )
    # sift alignment
    if self.sift:
      frame, *_ = lktools.SIFT.siftImageAlignment(self.lastn, frame)
    # MOG2 BS
    frame = self.fgbg.apply(frame)
    # Denoise
    frame = lktools.Denoise.denoise(frame, 'bilater')
    frame = lktools.Denoise.denoise(frame, 'morph_open')
    frame = lktools.Denoise.denoise(frame, 'dilation')
    frame = lktools.Denoise.denoise(frame, 'dilation')
    frame = lktools.Denoise.denoise(frame, 'erode') 
    # findObject
    bs_rects = lktools.FindObject.findObject(frame, rect)
    # rects
    rects = [rect]
    # rects
    rects.extend(bs_rects)
    if self.OF:
      rects.extend(flow_rects)
    return rects

  @lktools.Timer.timer_decorator
  def judge(self, src, rects):
    """
    对识别出的异常区域进行分类。

    Args:
      src:    原图
      rects:  框的list
    
    Self:
      judge_cache:   可长期持有的缓存，如果需要处理多帧的话
    """
    # 第一个框是检测范围，不是异常
    if len(rects) <= 1:
      return
    rects = rects[1:]
    # 对异常框进行处理
    print(rects)

  @lktools.Timer.timer_decorator
  def one_video(self, name, path):
    """
    处理一个单独的视频
    """
    # 循环
    def loop(self):
      if self.nframes >= self.frame_range[1]:
        return False
      success, frame = capture.read()
      if not success:
        return False
      self.nframes += 1
      if self.nframes < self.frame_range[0]:
        return True
      frame = cv2.resize(frame, size)
      if self.last is None:
        self.last = frame
        self.lastn = frame
        return True
      return frame
    # 写出
    def output(self, name, frame):
      if self.time_test:
        cv2.imshow(f'{name}', frame)
        cv2.waitKey(self.delay)
      else:
        # 每一帧写入图片中
        cv2.imwrite(
          f'{self.img_path}/{name}_{self.nframes}.jpg',
          frame
        )
        # 将图像保存为视频
        if self.videoWriter is None:
          fourcc = cv2.VideoWriter_fourcc(*'MJPG')
          self.videoWriter = cv2.VideoWriter(
            f'{self.video_path}/{name}.avi',
            fourcc,
            fps,
            size # WARNING：尺寸必须与图片的尺寸一致，否则保存后无法播放。
          )
        # 每一帧导入保存的视频中，uint8
        self.videoWriter.write(np.uint8(frame))
    # 更新
    def update(self, original):
      if self.nframes % self.interval == 0:
        self.lastn = original
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.fgbg.apply(self.lastn)
      self.last = original
    #
    #
    # 正式开始
    #
    #
    capture, h, w, fps, count = lktools.PreProcess.video_capture_size(path, self.height)
    size = (w, h)
    # print_info
    print(f'''
read {path}.
from frame {self.frame_range[0]} to {self.frame_range[1]}.
total {count} frames.
''')
    # 对每一帧
    while capture.isOpened():
      # 判断是否循环
      l = loop(self)
      if type(l) == bool:
        if l:
          continue
        else:
          break
      frame = l
      # 找到异常的矩形（其中第一个矩形为检测范围的矩形）
      rects = self.catch_abnormal(frame, size)
      # 分类
      _ = self.judge(frame, rects)
      # 绘制矩形
      frame_rects = lktools.PreProcess.draw(frame, rects)
      # 输出图像
      output(self, name, frame_rects)
      # 更新变量
      update(self, frame)
    capture.release()

  def clear(self):
    # 导出视频
    if (not self.time_test) and (self.videoWriter is not None):
      self.videoWriter.release()
      self.videoWriter = None
    # 销毁窗口
    if not self.linux:
      cv2.destroyAllWindows()
    self.judge_cache = []
    self.nframes = 0
    self.last = None
    self.lastn = None
    self.fgbg = cv2.createBackgroundSubtractorMOG2()

  def run(self):
    for name, video in self.videos:
      self.one_video(name, video)
      self.clear()

# run
if __name__ == '__main__':
  BSOFModel().run()