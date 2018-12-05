# import
import numpy as np
import cv2
import lktools
class BSOFModel:
  """
  整个模型
  """
  def __init__(self):
    """
    初始化必要变量

    初始化
      settings：    来自于Loader，从json文件读取
      judge_cache： 为judge使用的cache，每个单独的视频有一个单独的cache
      videoWriter： 为视频输出提供video writer，每个单独的视频有一个writer，会在clear中release
      logger：      创建logger

    做一次clear
    """
    self.logger = lktools.LoggerFactory.LoggerFactory('BS_OF')()
    self.settings = lktools.Loader.get_settings()
    self.judge_cache = None
    self.videoWriter = None
    self.clear()

  def __getattribute__(self, name):
    """
    如果self.NAME访问时，self不含属性NAME，则会在settings（配置文件json）中查找。
    所以只要self和settings中含有同名属性就会报错。（详见Loader.py template的说明）

    请修复。
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
        print(f"冲突为：self.{name}及self.settings['{name}']")
        from sys import exit
        exit(1)

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
      binary: 二值图像的dict，有'OF'和'BS'两个属性
    """
    frame = src
    # rect
    rect = lktools.PreProcess.get_rect_property(size) 
    # optical flow
    if self.OF:
      flow_rects, OF_binary = lktools.OpticalFlow.optical_flow_rects(
        self.last, frame, rect,
        limit_size=self.limit_size, compression_ratio=self.compression_ratio
      )
    else:
      OF_binary = None
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
    BS_binary = frame
    # findObject
    bs_rects = lktools.FindObject.findObject(frame, rect)
    # rects
    rects = [rect]
    # rects
    rects.extend(bs_rects)
    if self.OF:
      rects.extend(flow_rects)
    # ret
    return rects, {
      'OF': OF_binary,
      'BS': BS_binary,
    }

  @lktools.Timer.timer_decorator
  def judge(self, src, rects, binary):
    """
    对识别出的异常区域进行分类。

    Args:
      src:    原图
      rects:  框的list
      binary: 二值图像的dict，有'OF'和'BS'两个属性

    Self:
      judge_cache:   可长期持有的缓存，如果需要处理多帧的话
    """
    # 第一个框是检测范围，不是异常
    if len(rects) <= 1:
      return
    rects = rects[1:]
    # 对异常框进行处理
    # print(rects)

  @lktools.Timer.timer_decorator
  def one_video(self, name, path):
    """
    处理一个单独的视频
    """
    # 循环
    def loop(self, size):
      """
      计数frame
      如果是第一帧
        那么会返回True，即Continue
      如果在[0, frame_range[0]]范围内
        那么会返回True，即continue
      如果在[frame_range[0], frame_range[1]]范围内
        那么会返回frame，即当前帧
      否则
        返回False，即break
      """
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
    def output(self, name, frame, size):
      """
      输出一帧

      如果是要实时观察@time_test：
        显示一个新窗口，名为视频名称，将图片显示，其中延迟为@delay
      否则：
        将图片写入文件，地址为@img_path，图片名为@name_@nframes.jpg
        将图片写入视频，videoWriter会初始化，地址为@video_path，视频名为@name.avi，格式为'MJPG'
      """
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
        # 每一帧导入保存的视频中。WARNING：像素类型必须为uint8
        self.videoWriter.write(np.uint8(frame))
    # 更新
    def update(self, original):
      """
      如果@nframes计数为@interval的整数倍：
        更新@lastn
        重新建立BS_MOG2模型，并将当前帧作为第一帧应用在该模型上
      所有情况下：
        更新@last
      """
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
      l = loop(self, size)
      if type(l) == bool:
        if l:
          continue
        else:
          break
      frame = l
      # 找到异常的矩形（其中第一个矩形为检测范围的矩形）
      rects, binary = self.catch_abnormal(frame, size)
      # 分类
      _ = self.judge(frame, rects, binary)
      # 绘制矩形
      frame_rects = lktools.PreProcess.draw(frame, rects)
      # 输出图像
      output(self, name, frame_rects, size)
      # 更新变量
      update(self, frame)
    capture.release()

  def clear(self):
    """
    每个视频处理完之后对相关变量的清理

    videowriter： 会在这里release，并且设置为None
    cv：          会清理所有窗口
    judge_cache： judge使用的缓存，初始化为空list
    nframes：     计数器，为loop使用，初始化为0
    last：        上一帧
    lastn：       前N帧
    fgbg：        BS_MOG2模型
    """
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
    """
    对每一个视频进行处理
    """
    for name, video in self.videos:
      self.one_video(name, video)
      self.clear()

# run
if __name__ == '__main__':
  BSOFModel().run()