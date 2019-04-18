"""
numpy
"""
try:
  import numpy as np
except:
  print('numpy not loaded')
"""
opencv
"""
try:
  import cv2
except:
  print('opencv not loaded')
"""
中文转拼音
"""
try:
  from xpinyin import Pinyin
  pinyin = Pinyin()
except:
  print('xpinyin not loaded')
"""
lktools
"""
import lktools.Timer
import lktools.Checker
from lktools.PreProcess   import video_capture_size, bgr_to_hsv, gray_to_bgr, subtraction, matrix_within_rect, rect_size, rect_center, union_bounds
from lktools.OpticalFlow  import optical_flow_rects
from lktools.SIFT         import siftImageAlignment
from lktools.Denoise      import denoise
from lktools.FindObject   import findObject
try:
  import lktools.Vgg
  from lktools.BSOFDataset  import BSOFDataset
except:
  print('vgg not loaded')
"""
类别
"""
from resources.data import Abnormal
"""
sklearn
"""
try:
  from sklearn import svm
  from sklearn.externals import joblib
except:
  print('sklearn not loaded')
"""
pytorch
"""
try:
  import torch.optim
  import torch.nn
  from torch.utils.data import DataLoader
except:
  print('torch not loaded')
"""
reduce
"""
from functools import reduce
from functools import partial
import os

class BSOFModel:
  """
  整个模型
  """
  def __init__(self, opencv_output, generation, debug):
    """
    初始化必要变量

    初始化
      opencv_output:       是否利用cv2.imgshow()显示每一帧图片
      generation:          是否训练模型
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
      generation_cache     generation cache
      debug_param          debug相关参数
      debug                是否进行model debug

    做一次clear
    """
    self.opencv_output      = opencv_output
    self.generation         = generation
    self.debug              = debug
    self.settings           = lktools.Loader.get_settings()
    self.logger             = lktools.LoggerFactory.LoggerFactory(
      'BS_OF', level=self.settings['debug_level']
    ).logger
    self.checker            = lktools.Checker.Checker(self.logger)
    self.judge_cache        = None
    self.rect_mask          = None
    self.videoWriter        = None
    self.every_frame        = None
    self.before_every_video = None
    self.thread_stop        = False
    self.state              = BSOFModel.RUNNING
    self.box_scale          = ((1 / 16, 1 / 4), (15 / 16, 2.9 / 4))
    self.generation_cache   = {'X': [], 'Y': [], 'src': [], 'debug': [], 'debug_count': 0}
    self.debug_param        = {'continue': False, 'step': 0}
    self.dataset            = None
    self.dataloader         = None
    self.check()

  @lktools.Timer.timer_decorator()
  def check(self):
    """
    测试，失败就关闭
    """
    if self.cuda:
      self.checker.cuda_check()
    if not self.generation:
      self.logger.debug('测试model文件是否存在')
      path = {
        'svm': self.svm_model_path,
        'vgg': self.vgg_model_path,
      }.get(self.model_t)
      if path:
        self.checker.check(path, self.checker.exists_file)
    if self.checker.dirty:
      self.thread_stop = True
      self.state = BSOFModel.STOPPED

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

  @lktools.Timer.timer_decorator()
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
    binary = denoise(binary, 'morph_open', (2, 2))
    binary = denoise(binary, 'dilation', ((2, 2), 1))
    binary = denoise(binary, 'dilation', ((2, 2), 1))
    binary = denoise(binary, 'erode', ((2, 2), 2))
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
      abnormal['OF_Binary'] = OF_binary
      abnormal['OF'] = gray_to_bgr(OF_binary) & src
    if BS_binary is not None:
      abnormal['BS_Binary'] = BS_binary
      abnormal['BS'] = gray_to_bgr(BS_binary) & src
    return rects, abnormal

  @lktools.Timer.timer_decorator()
  def judge(self, src, rects, abnormal):
    """
    对识别出的异常区域进行分类或训练（根据self.generation）。

    Args:
      src:    原图
      rects:  框的list
      abnormal: 异常部分的dict，有'OF'和'BS'两个属性

    Self:
      judge_cache:   可长期持有的缓存，如果需要处理多帧的话

    Return:
      ( (class, probablity), ... ), (attribute)
    """
    if self.skip_first_abnormal:
      self.skip_first_abnormal = False
      return None, None
    if len(rects) <= 1:
      return None, None
    self.logger.debug('第一个框是检测范围，不是异常')
    def debug(*args, func=None):
      """
      debug
      """
      if not self.debug_per_frame:
        return
      if func is None:
        info = args
      else:
        info = func(*args)
      self.logger.info(info)
      self.debug_param['continue'] = False
    @lktools.Timer.timer_decorator()
    def attributes(src, range_rect, rects, abnormal):
      """
      生成特征
      """
      # 选择最大的矩形
      max_rect = max(rects, key=rect_size)
      mat = matrix_within_rect(abnormal['BS'], max_rect)
      if mat is None or mat.size == 0:
        self.logger.debug('矩阵没有正确取区域或是区域内为空则返回')
        return
      # ⬇️颜色
      self.logger.debug('转换为HSV')
      hsv_mat = bgr_to_hsv(mat)
      self.logger.debug('求均值')
      hsv = hsv_mat.mean(axis=(0, 1))
      debug(max_rect)
      debug(hsv, func=lambda c: f'h: {c[0]:.2f}, s: {c[1]:.2f}, v: {c[2]:.2f}')
      # ⬇️周长面积比
      binary = matrix_within_rect(abnormal['BS_Binary'], max_rect)
      _, contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      def length_of_area(c):
        length = cv2.arcLength(c, True)
        area = cv2.contourArea(c)
        if area == 0:
          return 0
        return length / area
      len_area = np.mean(tuple(map(length_of_area, contours)))
      # ⬇️面积增长率
      area = sum(map(cv2.contourArea, contours))
      last_area = self.judge_cache['area']
      if area > last_area > 0:
        self.judge_cache['max_area_rate'] = max((area - last_area) / last_area, self.judge_cache['max_area_rate'])
      self.judge_cache['area'] = area
      # ⬇️中心相对移动
      center = rect_center(max_rect)
      last_center = self.judge_cache.get('center')
      center_offset = 0.0
      if last_center is not None:
        center_offset = np.linalg.norm((center[0] - last_center[0], center[1] - last_center[1]))
      self.judge_cache['center'] = center
      # 返回
      return [hsv[0], hsv[1], len_area, self.judge_cache['max_area_rate'], center_offset]
    @lktools.Timer.timer_decorator()
    def classify(src, range_rect, rects, abnormal):
      """
      分类
      """
      if self.model_t == 'svm':
        X = [attributes(src, range_rect, rects, abnormal)]
        y = self.classifier.predict_proba(X)
        proba = dict(zip(self.classifier.classes_, y[0]))
        return self.abnormals.accumulate_abnormals(proba), X
      elif self.model_t == 'vgg':
        cache = self.generation_cache
        img = BSOFDataset.load_img(matrix_within_rect(src, union_bounds(rects)), (224, 224))
        cache['src'].append(img)
        if len(cache['src']) < 64:
          return None, None
        output = torch.stack(cache['src'])
        output = self.classifier(output)
        output = self.classifier.softmax(output)
        if self.debug:
          cache['debug'].extend(zip(cache['src'], output))
        output = output.sum(0) / len(output)
        proba  = dict(zip(self.vgg_classes, output.tolist()))
        cache['src'].clear()
        return Abnormal.Abnormal.abnormals(proba), None
      return None, None
    @lktools.Timer.timer_decorator()
    def generate(src, range_rect, rects, abnormal):
      """
      生成模型
      """
      X = attributes(src, range_rect, rects, abnormal)
      self.generation_cache['X'].append(X)
      if self.now.get('Y') is None:
        self.now['Y'] = Abnormal.Abnormal.abnormal(self.class_info[self.now['name']])
      self.generation_cache['Y'].append(self.now['Y'])
      return None, None
    func = generate if self.generation else classify
    return func(src, rects[0], rects[1:], abnormal)

  @lktools.Timer.timer_decorator()
  def one_video_classification(self, path):
    """
    处理一个单独的视频
    """
    @lktools.Timer.timer_decorator()
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
      l_range, r_range = self.frame_range
      if r_range < 0:
        r_range += self.now['count']
      if self.nframes > r_range:
        return False
      success, frame = capture.read()
      if not success:
        return False
      self.nframes += 1
      if self.nframes < l_range:
        return True
      frame = cv2.resize(frame, size)
      if self.last is None:
        self.last = frame
        self.lastn = frame
        return True
      return frame
    @lktools.Timer.timer_decorator()
    def save(frame, frame_trim, frame_rects, abnormal, classes, attributes):
      """
      保存相关信息至self.now，便于其它类使用（如App）

      Args:
        frame:             当前帧原始图片
        frame_trim:        裁剪过后的图片
        frame_rects:       当前帧原始图片（包含圈出异常的框）
        abnormal:          当前帧的异常图像，是一个dict，有两个值{'OF', 'BS'}
                            分别代表光流法、高斯混合模型产生的异常图像
        classes:           当前帧的类别
        attributes:        特征
      """
      self.now['frame']       = frame
      self.now['frame_trim']  = frame_trim
      self.now['frame_rects'] = frame_rects
      self.now['abnormal']    = abnormal
      self.now['classes']     = classes
      self.now['attributes']  = attributes
    @lktools.Timer.timer_decorator()
    def output(frame, size):
      """
      输出一帧处理过的图像（有异常框）

      如果是要写入文件@file_output:
        将图片写入文件，地址为@img_path，图片名为@name_@nframes.jpg
        将图片写入视频，videoWriter会初始化，地址为@video_path，视频名为@name.avi，格式为'MJPG'
      否则，如果要打印在opencv窗口@opencv_output:
        显示一个新窗口，名为视频名称，将图片显示，其中延迟为@delay
        ESC键退出
      如果是要进行模型的@debug:
        模型会保存值到self.generation_cache['debug']中，
        根据需要读取并使用。
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
        py = self.now['pinyin']
        cv2.imshow(f'{py}', frame)
        cv2.imshow(f'{py} abnormal BS', self.now['abnormal']['BS'])
        if cv2.waitKey(self.delay) == 27:
          self.logger.debug('ESC 停止')
          self.thread_stop = True
      elif self.debug:
        if self.model_t == 'vgg':
          cache = self.generation_cache
          items = cache['debug']
          if not os.path.exists('temp'):
            os.mkdir('temp')
          while len(items) != 0:
            img, label = items.pop(0)
            img = img.numpy().transpose((1, 2, 0))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            label = ';'.join(map(
              lambda t: f'{t[0]}_{t[1] * 100:.0f}%',
              zip(self.vgg_rclasses, label.tolist())
            ))
            cv2.imwrite(f'temp/{cache["debug_count"]}_{label}.jpg', img)
            cache['debug_count'] += 1
    @lktools.Timer.timer_decorator()
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
    @lktools.Timer.timer_decorator()
    def trim(frame):
      """
      对图片进行裁剪
      """
      if self.rect_mask is None:
        box = self.box
        if box is None:
          return
        (x1, y1), (x2, y2) = box
        self.rect_mask = np.zeros(frame.shape, dtype=np.uint8)
        self.rect_mask[y1:y2, x1:x2] = 255
      return self.rect_mask & frame.copy()
    def debug():
      """
      debug模式
      输入'n'并回车，跳到下一帧。
      直接回车，跳到下一个异常帧。
      """
      if not self.debug_per_frame:
        return
      if self.debug_param['continue']:
        return
      if self.debug_param['step'] > 0:
        self.debug_param['step'] -= 1
        return
      c = input()
      if len(c) > 0 and c[0] == 'n':
        try:
          self.debug_param['step'] = int(c[1:])
        except:
          self.debug_param['step'] = 0
      else:
        self.debug_param['continue'] = True
      if c == 'q':
        self.thread_stop = True

    self.logger.debug('----------------------')

    self.logger.debug('首先读取视频信息，包括capture类，高度h，宽度w，fps，帧数count')

    capture, h, w, fps, count = video_capture_size(path, self.height)
    size = (w, h)
    self.now['size'] = size
    self.now['count'] = count
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

      classes, attributes = self.judge(frame, rects, abnormal)

      self.logger.debug('绘制矩形')

      frame_rects = lktools.PreProcess.draw(l, rects)

      self.logger.debug('存储相关信息')

      save(l, frame, frame_rects, abnormal, classes, attributes)

      self.logger.debug('输出图像')

      output(frame_rects, size)

      self.logger.debug('回调函数')

      if self.every_frame:
        self.every_frame()

      self.logger.debug('更新变量')

      update(frame)

      self.logger.debug('判断该线程是否结束')

      debug()

      if self.thread_stop:
        break

    capture.release()

  def clear_classification(self):
    """
    每个视频处理完之后对相关变量的清理

    videowriter:         会在这里release，并且设置为None
    cv:                  会清理所有窗口
    judge_cache:         judge使用的缓存，初始化为空list
    nframes:             计数器，为loop使用，初始化为0
    last:                上一帧
    lastn:               前N帧
    normal_frame:        正常帧
    box_cache:           缓存box的具体坐标
    skip_first_abnormal: 跳过第一个异常帧，第一次会被识别为整个区域
    abnormals            异常实例
    fgbg:                BS_MOG2模型
    """
    if self.file_output and (self.videoWriter is not None):
      self.logger.debug('导出视频')
      self.videoWriter.release()
      self.videoWriter = None
    if self.opencv_output and not self.linux:
      self.logger.debug('销毁窗口')
      cv2.destroyAllWindows()
    self.judge_cache         = { 'area': 0, 'max_area_rate': 0 }
    self.nframes             = 0
    self.last                = None
    self.lastn               = None
    self.normal_frame        = None
    self.box_cache           = None
    self.skip_first_abnormal = True
    self.abnormals           = Abnormal.Abnormal()
    self.fgbg                = cv2.createBackgroundSubtractorMOG2(
      varThreshold=self.varThreshold,
      detectShadows=self.detectShadows
    )

  @property
  def is_cuda_available(self):
    return self.cuda and torch.cuda.is_available()

  @property
  def num_classes(self):
    if self.dataset is None:
      return 0
    return min(map(lambda ds: ds.num_classes, self.dataset.values()))

  @lktools.Timer.timer_decorator()
  def classification(self):
    """
    对视频做异常帧检测并分类
    """
    def svm():
      if not self.generation:
        self.classifier = joblib.load(self.model_path)
      self.foreach(self.one_video_classification, self.clear_classification)
      if not self.generation:
        return
      self.logger.debug('训练模型')
      kwargs = {
        'gamma'                   : 'scale',
        'decision_function_shape' : 'ovo',
        'max_iter'                : self.max_iter,
        'probability'             : True,
      }
      classifier = svm.SVC(**kwargs)
      self.logger.info(kwargs)
      classifier.fit(self.generation_cache['X'], self.generation_cache['Y'])
      joblib.dump(classifier, self.model_path)
    def vgg():
      # 载入模型
      def load():
        data    = torch.load(self.vgg_model_path)
        state   = data['state']
        classes = data['classes']

        model = lktools.Vgg.vgg(self.vgg, num_classes=len(classes))
        model.load_state_dict(state)
        model.eval()
        rclasses = classes
        classes = tuple(map(Abnormal.Abnormal.abnormal, rclasses))
        return model, classes, rclasses
      # 计算acc
      def acc(output, label):
        return (output.max(1)[1] == label).sum().float()
      # 载入模型并运行
      if not self.generation:
        self.classifier, self.vgg_classes, self.vgg_rclasses = load()
        self.foreach(self.one_video_classification, self.clear_classification)
        return
      # 是否测试
      need_test = os.path.exists(self.vgg_model_path)
      # 训练
      def train(data, length, model, optim, scheduler, criterion):
        # 初始化打印信息
        def start(stime, args, kwargs):
          self.logger.info(f'epoch {args[0]}')
        # 结束打印信息
        def end(result, stime, etime, args, kwargs):
          loss_sum, acc_sum, nan = result
          self.logger.info(f'avgloss: {loss_sum / length:.4f}')
          self.logger.info(f'总正确率：{acc_sum * 100 / length:.2f}%')
          self.logger.info(f'nan: {nan}')
          self.logger.info(f'花费时间：{etime - stime:.0f}s')
        # 训练一轮
        @lktools.Timer.timer_decorator(show=True, start_info=start, end_info=end)
        def train_one_epoch(epoch, data, model, optim, scheduler, criterion):
          scheduler.step()
          train_loss = 0
          train_acc  = 0
          nan        = 0
          for img, label in data:
            if self.is_cuda_available:
              img   = img.cuda()
              label = label.cuda()
            optim.zero_grad()
            output = model(img)
            loss   = criterion(output, label)
            loss.backward()
            optim.step()
            if not torch.isnan(loss.data):
              train_loss += loss.data
            else:
              nan += 1
            train_acc += acc(output, label)
          return train_loss, train_acc, nan
        for epoch in range(self.num_epochs):
          train_one_epoch(epoch, data, model, optim, scheduler, criterion)
        torch.save(
          {
            'state'  : model.state_dict(),
            'classes': data.dataset.classes,
          }, self.vgg_model_path
        )
      # 测试模型
      def test(data, length, model, classes, criterion):
        loss_sum = 0
        acc_sum  = 0
        for img, label in data:
          if self.is_cuda_available:
            img   = img.cuda()
            label = label.cuda()
          output = model(img)
          loss   = criterion(output, label)
          loss.backward()
          loss   = loss.data
          _acc   = acc(output, label)
          self.logger.info(f'loss: {loss:.4f} 正确率：{_acc * 100 / 64:.2f}%')
          loss_sum += loss
          acc_sum  += _acc
        self.logger.info(f'avgloss : {loss_sum / length:.4f}')
        self.logger.info(f'总正确率 : {acc_sum * 100 / length:.2f}%')
      self.logger.debug('测试模型' if need_test else '训练模型')
      self.dataset = {
        name: BSOFDataset(
          self.data[name]
        ) for name in ('train', 'test')
      }
      self.dataloader = {
        name: DataLoader(
          dataset, batch_size=self.batch_size, shuffle=True,
          num_workers=self.num_workers,
        ) for name, dataset in self.dataset.items()
      }
      if need_test:
        model, classes, *_ = load()
        test(
          self.dataloader['test'], len(self.dataset['test']),
          model, classes, torch.nn.CrossEntropyLoss()
        )
      else:
        model = lktools.Vgg.vgg(self.vgg, num_classes=self.num_classes)
        optim = torch.optim.SGD(model.parameters(), lr=self.learning_rate, momentum=self.momentum)
        scheduler = torch.optim.lr_scheduler.StepLR(optim, step_size=self.step_size, gamma=self.gamma)
        criterion = torch.nn.CrossEntropyLoss()
        model.train()
        train(
          self.dataloader['train'], len(self.dataset['train']),
          model, optim, scheduler, criterion
        )
    if self.thread_stop:
      return
    m = {
      'svm': svm,
      'vgg': vgg,
    }.get(self.model_t)
    if m:
      m()

  @lktools.Timer.timer_decorator()
  def foreach(self, single_func, clear_func):
    """
    对每一个视频，运行single_func去处理该视频，最后用clear_func清理变量。

    设置now dict。

    设置name、path、pinyin等信息。
    """
    if self.state is BSOFModel.STOPPED:
      self.logger.info('model has stopped.')
      return
    clear_func()
    self.now = {}
    for name, video in self.videos:
      self.now['name'] = name
      self.now['pinyin'] = pinyin.get_pinyin(name, ' ')
      single_func(video)
      clear_func()
      self.now.clear()
      if self.thread_stop:
        break
    self.state = BSOFModel.STOPPED

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

  @property
  @lktools.Timer.timer_decorator()
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
    self.box_scale           = rect
    self.box_cache           = None
    self.rect_mask           = None
    # 重新设置box scale之后，需要忽略一帧
    self.skip_first_abnormal = True

if __name__ == '__main__':
  import sys
  nothing = len(sys.argv) == 0
  show  = 'show'  in sys.argv
  model = 'model' in sys.argv
  debug = 'debug' in sys.argv
  model = BSOFModel(nothing or show, not debug and model, debug)
  model.classification()
