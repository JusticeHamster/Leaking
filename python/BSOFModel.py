"""
numpy
"""
import numpy as np
"""
opencv
"""
import cv2
"""
lktools
"""
import lktools.Timer
from lktools.PreProcess   import video_capture_size, bgr_to_hsv, gray_to_bgr, subtraction
from lktools.OpticalFlow  import optical_flow_rects
from lktools.SIFT         import siftImageAlignment
from lktools.Denoise      import denoise
from lktools.FindObject   import findObject
class BSOFModel:
  """
  整个模型
  """
  def __init__(self, opencv_output):
    """
    初始化必要变量

    初始化
      opencv_output:       是否利用cv2.imgshow()显示每一帧图片
      settings:            一个字典，由Loader从用户自定义json文件中读取
      judge_cache:         为judge使用的cache，每个单独的视频有一个单独的cache
      rect_mask:           做整个视频裁剪的mask
      videoWriter:         为视频输出提供video writer，每个单独的视频有一个writer，会在clear中release
      logger:              创建logger
      every_frame:         回调函数，每一帧执行完后会调用，方便其它程序处理
      before_every_video:  回调函数，每个视频开始前调用，方便其它程序处理
      thread_stop:         判断该线程是否该终止，由持有该模型的宿主修改
      state:               是否暂停
      box_scale:           蓝框的比例(<leftdown>, <rightup>)

    做一次clear
    """
    self.opencv_output = opencv_output
    self.settings = lktools.Loader.get_settings()
    self.logger = lktools.LoggerFactory.LoggerFactory(
      'BS_OF', level=self.settings['debug_level']
    ).logger
    self.judge_cache        = None
    self.rect_mask          = None
    self.videoWriter        = None
    self.every_frame        = None
    self.before_every_video = None
    self.thread_stop        = False
    self.state              = BSOFModel.RUNNING
    self.box_scale          = ((1 / 16, 1 / 4), (15 / 16, 2.9 / 4))
    self.setup()

  def __getattribute__(self, name):
    """
    为了方便访问setting的内容，做了以下修改:
      如果self.NAME访问时，self不含属性NAME，则会在settings中查找。
      所以只要self和settings中含有同名属性就会报错。

    请避免传入的settings与self中含同名property。
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
        self.logger.error(BSOFModel.__getattribute__.__doc__)
        self.logger.error(f"冲突为:self.{name}及self.settings['{name}']")
        from sys import exit
        exit(1)

  @lktools.Timer.timer_decorator
  def catch_abnormal(self, src):
    """
    对一帧图像进行处理，找到异常就用框圈出来。

    Args:
      src:    原图

    Self:
      lastn:  前N帧图片，用于对齐
      last:   上一帧图片，用于光流法寻找移动物体
      fgbg:   BackgroundSubtractionMOG2方法使用的一个类

    Returns:
      rects:  框的list
      binary: 二值图像的dict，有'OF'和'BS'两个属性
    """
    frame = src
    self.logger.debug('rect')
    rect = self.box
    self.logger.debug('optical flow')
    if self.OF:
      flow_rects, OF_binary = optical_flow_rects(
        self.last, frame, rect,
        limit_size=self.limit_size, compression_ratio=self.compression_ratio
      )
    else:
      OF_binary = None
    self.logger.debug('sift alignment')
    if self.sift:
      frame, *_ = siftImageAlignment(self.lastn, frame)
    self.logger.debug('MOG2 BS')
    frame = self.fgbg.apply(frame)
    self.logger.debug('Binary')
    _, binary = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
    self.logger.debug('Denoise')
    binary = denoise(binary, 'bilater')
    binary = denoise(binary, 'morph_open')
    binary = denoise(binary, 'dilation')
    binary = denoise(binary, 'dilation')
    binary = denoise(binary, 'erode')
    BS_binary = binary
    self.logger.debug('findObject')
    bs_rects = findObject(binary, rect)
    self.logger.debug('蓝框')
    rects = [(*rect, (0xFF, 0, 0))]
    rects.extend(bs_rects)
    if self.OF:
      rects.extend(flow_rects)
    self.logger.debug('return')
    # TODO: 先假定第一帧为正常帧，并且后面不会变化
    if self.normal_frame is None:
      self.normal_frame = src
    abnormal = {}
    if OF_binary is not None:
      abnormal['OF'] = gray_to_bgr(OF_binary) & src
    if BS_binary is not None:
      abnormal['BS'] = gray_to_bgr(BS_binary) & src
    return rects, abnormal

  """
  类别常量
  """
  '''液体异常'''
  ACID_SOLUTION     = '酸碱溶液'
  WATER             = '水'
  EDIBLE_OIL        = '食用油'
  MOTOR_OIL         = '机油'
  COAL_WATER_SLURRY = '水煤浆'
  '''气体异常'''
  WATER_VAPOR       = '水蒸气'
  SMOKE             = '烟'
  '''明火异常'''
  OPEN_FIRE         = '明火'
  ELECTRIC_SPARK    = '电火花'
  '''粉尘异常'''
  LEAKAGE_DUST      = '漏料粉尘'
  FUNNEL_COAL_ASH   = '漏斗煤灰'
  '''未知'''
  UNKNOWN           = 'unknown'

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

    Return:
      ( (class, probablity), ... )
    """
    self.logger.debug('第一个框是检测范围，不是异常')
    if len(rects) <= 1:
      return
    rects = rects[1:]
    self.logger.debug('首先准备一个该帧的HSV图像')
    # _ = bgr_to_hsv(src)
    # 测试所有类别的颜色等信息
    return (
      (BSOFModel.ACID_SOLUTION    , 9),
      (BSOFModel.WATER            , 9),
      (BSOFModel.EDIBLE_OIL       , 9),
      (BSOFModel.MOTOR_OIL        , 9),
      (BSOFModel.COAL_WATER_SLURRY, 9),
      (BSOFModel.WATER_VAPOR      , 9),
      (BSOFModel.SMOKE            , 9),
      (BSOFModel.OPEN_FIRE        , 9),
      (BSOFModel.ELECTRIC_SPARK   , 9),
      (BSOFModel.LEAKAGE_DUST     , 9),
      (BSOFModel.FUNNEL_COAL_ASH  , 10),
    )

  @lktools.Timer.timer_decorator
  def one_video(self, path):
    """
    处理一个单独的视频
    """
    def loop(size):
      """
      如果线程结束
        就返回False，即break
      如果暂停
        就返回True，即continue，不读取任何帧，也不计数

      计数frame
      如果是第一帧
        那么会返回True，即continue
      如果在[0, frame_range[0]]范围内
        那么会返回True，即continue
      如果在[frame_range[0], frame_range[1]]范围内
        那么会返回frame，即当前帧
      否则
        返回False，即break
      """
      if self.thread_stop:
        return False
      if self.state is BSOFModel.PAUSED:
        return True
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
    def save(frame, frame_trim, frame_rects, abnormal, classes):
      """
      保存相关信息至self.now，便于其它类使用（如App）

      Args:
        frame:             当前帧原始图片
        frame_trim:        裁剪过后的图片
        frame_rects:       当前帧原始图片（包含圈出异常的框）
        abnormal:          当前帧的异常图像，是一个dict，有两个值{'OF', 'BS'}
                            分别代表光流法、高斯混合模型产生的异常图像
        classes:           当前帧的类别
      """
      self.now['frame']       = frame
      self.now['frame_trim']  = frame_trim
      self.now['frame_rects'] = frame_rects
      self.now['abnormal']    = abnormal
      self.now['classes']     = classes
    def output(frame, size):
      """
      输出一帧处理过的图像（有异常框）

      如果是要写入文件@file_output:
        将图片写入文件，地址为@img_path，图片名为@name_@nframes.jpg
        将图片写入视频，videoWriter会初始化，地址为@video_path，视频名为@name.avi，格式为'MJPG'
      否则，如果要打印在opencv窗口@opencv_output:
        显示一个新窗口，名为视频名称，将图片显示，其中延迟为@delay
        ESC键退出
      """
      name = self.now['name']
      if self.file_output:
        self.logger.debug('每一帧写入图片中')

        now_img_path = f'{self.img_path}/{name}_{self.nframes}.jpg'
        cv2.imwrite(now_img_path, frame)
        self.now['now_img_path'] = now_img_path

        self.logger.debug('将图像保存为视频')
        self.logger.debug('WARNING:尺寸必须与图片的尺寸一致，否则保存后无法播放。')

        if self.videoWriter is None:
          fourcc = cv2.VideoWriter_fourcc(*'MJPG')
          self.videoWriter = cv2.VideoWriter(
            f'{self.video_path}/{name}.avi',
            fourcc,
            fps,
            size
          )

        self.logger.debug('每一帧导入保存的视频中。')
        self.logger.debug('WARNING:像素类型必须为uint8')

        self.videoWriter.write(np.uint8(frame))
      elif self.opencv_output:
        cv2.imshow(f'{name}', frame)
        cv2.imshow(f'{name}_abnormal_BS', self.now['abnormal']['BS'])
        if cv2.waitKey(self.delay) == 27:
          self.logger.debug('ESC 停止')
          self.thread_stop = True
    def update(original):
      """
      如果@nframes计数为@interval的整数倍:
        更新@lastn
        重新建立BS_MOG2模型，并将当前帧作为第一帧应用在该模型上
      所有情况下:
        更新@last
      """
      if self.nframes % self.interval == 0:
        self.lastn = original
        self.fgbg = cv2.createBackgroundSubtractorMOG2(
          varThreshold=self.varThreshold,
          detectShadows=self.detectShadows
        )
        self.fgbg.apply(self.lastn)
      self.last = original
    def trim(frame):
      """
      对图片进行裁剪
      """
      if self.rect_mask is None:
        (x1, y1), (x2, y2) = self.box
        self.rect_mask = np.zeros(frame.shape, dtype=np.uint8)
        self.rect_mask[y1:y2, x1:x2] = 255
      return self.rect_mask & frame.copy()

    self.logger.debug('----------------------')

    self.logger.debug('首先读取视频信息，包括capture类，高度h，宽度w，fps，帧数count')

    capture, h, w, fps, count = video_capture_size(path, self.height)
    size = (w, h)
    self.now['size'] = size
    self.logger.info(f'''
      read {path}.
      from frame {self.frame_range[0]} to {self.frame_range[1]}.
      total {count} frames.
    ''')

    self.logger.debug('首先是看是否有初始化动作')

    if self.before_every_video:
      self.before_every_video()

    self.logger.debug('对每一帧')

    while capture.isOpened():

      self.logger.debug('判断是否循环')

      l = loop(size)
      if type(l) == bool:
        if l:
          continue
        else:
          break
      frame = l

      self.logger.debug('裁剪原始图片')

      frame = trim(frame)

      self.logger.debug('找到异常的矩形（其中第一个矩形为检测范围的矩形）')

      rects, abnormal = self.catch_abnormal(frame)

      self.logger.debug('分类')

      classes = self.judge(frame, rects, abnormal)

      self.logger.debug('绘制矩形')

      frame_rects = lktools.PreProcess.draw(l, rects)

      self.logger.debug('存储相关信息')

      save(l, frame, frame_rects, abnormal, classes)

      self.logger.debug('输出图像')

      output(frame_rects, size)

      self.logger.debug('回调函数')

      if self.every_frame:
        self.every_frame()

      self.logger.debug('更新变量')

      update(frame)

      self.logger.debug('判断该线程是否结束')

      if self.thread_stop:
        break

    capture.release()

    self.clear()

  def clear(self):
    """
    每个视频处理完之后对相关变量的清理

    videowriter:  会在这里release，并且设置为None
    cv:           会清理所有窗口
    judge_cache:  judge使用的缓存，初始化为空list
    nframes:      计数器，为loop使用，初始化为0
    last:         上一帧
    lastn:        前N帧
    fgbg:         BS_MOG2模型
    now:          存储处理过程的当前帧等信息，是dict
    normal_frame: 正常帧
    box_cache:    缓存box的具体坐标
    """
    self.logger.debug('导出视频')
    if self.file_output and (self.videoWriter is not None):
      self.videoWriter.release()
      self.videoWriter = None
    self.logger.debug('销毁窗口')
    if self.opencv_output and not self.linux:
      cv2.destroyAllWindows()
    self.judge_cache = []
    self.nframes = 0
    self.last = None
    self.lastn = None
    self.fgbg = cv2.createBackgroundSubtractorMOG2(
      varThreshold=self.varThreshold,
      detectShadows=self.detectShadows
    )
    self.now = {}
    self.normal_frame = None
    self.box_cache = None

  @property
  def box(self):
    """
    计算当前蓝框的具体坐标
    放入缓存box_cache
    """
    if self.box_cache is not None:
      return self.box_cache
    size = self.now.get('size')
    if size is None:
      return
    (x1, y1), (x2, y2) = self.box_scale
    w, h = size
    self.box_cache = (
      (int(x1 * w), h - int(y2 * h)),
      (int(x2 * w), h - int(y1 * h))
    )
    self.logger.info(self.box_cache)
    return self.box_cache

  @box.setter
  def box(self, rect):
    """
    根据一个比例的rect改变box的位置。
    不影响其它参数（如color）

    example:
      ((0.0, 0.5), (0.5, 1.0))
        leftdown     rightup
    """
    self.box_scale = rect
    self.box_cache = None
    self.rect_mask = None

  RUNNING = 'running'
  PAUSED  = 'paused'
  STOPPED = 'stopped'
  def pause(self):
    """
    暂停
    """
    if self.state is BSOFModel.RUNNING:
      self.state = BSOFModel.PAUSED
    elif self.state is BSOFModel.PAUSED:
      self.state = BSOFModel.RUNNING

  def setup(self):
    """
    等价于clear，为了接口分离
    """
    self.clear()

  def run(self):
    """
    对每一个视频进行处理
    """
    for name, video in self.videos:
      self.now['name'] = name
      self.one_video(video)
      if self.thread_stop:
        break
    self.state = BSOFModel.STOPPED

if __name__ == '__main__':
  BSOFModel(True).run()
