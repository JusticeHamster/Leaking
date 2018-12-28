"""
Model Class
"""
from BSOFModel import BSOFModel
"""
Multi-Thread
"""
import threading
"""
numpy
"""
import numpy
"""
lktools
"""
import lktools.Loader
import lktools.LoggerFactory
from lktools.Translator import translate
from lktools.PreProcess import point_in_rect, trim_to_rect
"""
GUI
  warning: 必须导入，用于kivy创建类
"""
import GUI.BSOFForm
import GUI.BSOFGraph
"""
kivy related
"""
import kivy
kivy.require('1.10.1')
import kivy.app
import kivy.graphics
import kivy.clock
import kivy.core.window
import kivy.garden
from kivy.graphics.texture import Texture
from kivy.metrics import dp
"""
分类信息
"""
from resources.data import Abnormal

class BSOFApp(kivy.app.App):
  """
  App GUI for BSOFModel
  """
  def on_start(self):
    """
    准备，并开始

    self:
      settings:        用户配置文件，settings.json
      logger:          日志，debug记录流程（默认不会打印），info及以上显示必要信息
      model:           BSOFModel模型
      textures:        缓存
      clock:           定时调用
      dirty:           判断是否处理完一帧(视频)，防止定时调用重复计算
      states:          当前状态，包含暂停状态:{RUNNING, PAUSED}, 绘制蓝框的状态:{READY, DOING, FREEZE, NOT_READY}
      scale:           视频缩放
      wsize:           当前window size
      mouse_pos:       鼠标位置信息
      classes:         分类信息，格式为pizza格式( ('title', percentage, 'color'), ... )
    """
    self.settings = lktools.Loader.get_settings()
    self.logger   = lktools.LoggerFactory.LoggerFactory('App').logger
    self.model    = BSOFModel(False)
    self.textures = {}
    self.clock    = kivy.clock.Clock.schedule_interval(self.on_clock, 1 / self.settings['app_fps'])
    self.dirty    = {'frame': False, 'video': False, 'classes': False}
    self.states   = {'APP': BSOFApp.RUNNING, 'BOX': BSOFApp.READY}
    self.scale    = self.settings['scale']
    self.wsize    = None
    self.mouse_pos= None
    self.classes  = []
    self.logger.debug('设置回调函数')
    self.model.every_frame = self.every_frame
    self.model.before_every_video = self.before_every_video

    self.logger.debug('创建pizza')
    self.form.pizza(self.classes)

    self.logger.debug('运行model')
    self.model_runner = threading.Thread(target=self.model.classification)
    self.model_runner.start()

  def on_clock(self, delta_time):
    """
    计时器到时间就调用

    Args:
      delta_time:   计时时间

    由settings.json中的app_fps指定
    """
    def update(name, id):
      data = None
      for n in name.split('.'):
        data = self.model.now.get(n) if data is None else data.get(n)
        if data is None:
          return
      texture = self.textures.get(id)
      if texture is None:
        return
      self.logger.debug(f'处理{id}:')
      self.logger.debug('更新数据')
      data = data[::-1]
      texture.blit_buffer(data.tostring(), colorfmt='bgr', bufferfmt='ubyte')
      self.logger.debug('刷新canvas')
      self.form.ids[id].canvas.ask_update()
    self.logger.debug(f'------------- {delta_time}')
    if self.states['APP'] is BSOFApp.PAUSED:
      self.logger.debug('暂停中')
      return
    if self.model.state is BSOFModel.STOPPED:
      self.logger.debug('model运行结束')
      image = self.form.ids.get('image')
      if image is not None:
        image.text = translate('END')
      return
    if self.dirty['frame']:
      self.logger.debug('需要刷新frame')
      update('frame_rects', 'now_image')
      update('abnormal.BS', 'abnormal_image')
      self.dirty['frame'] = False
    if self.dirty['video']:
      self.logger.debug('需要resize')
      kivy.core.window.Window.size = self.wsize
      self.dirty['video'] = False
    if self.dirty['classes']:
      self.logger.debug('重画pizza')
      self.form.pizza(self.classes)
      self.dirty['classes'] = False

  def every_frame(self):
    """
    每一帧都会调用该函数

    这个函数不在主线程，不能在这里调用blit_buffer（无效）

    从self.model.now中获取model信息:
      name:          当前文件名称
      frame:         当前帧的uint8拷贝
      frame_rects:   当前帧（框出异常）
      binary:        二值图像（是一个dict，包含{'OF', 'BS'}两种，详情见BSOFModel）
      classes:       分类信息，格式为( ('class', probablity), ... )
      size:          图像大小

    当然也可以直接读取self.model的变量，但请不要从这里修改
    """
    def try_create_texture(id):
      self.logger.debug('如果已经存在了就返回')
      texture = self.textures.get(id)
      if texture is not None:
        return
      self.logger.debug('创建新的texture，并存入缓存')
      frame = self.model.now.get('frame')
      if frame is None:
        return
      size = frame.shape[1::-1]
      texture = Texture.create(size=size, colorfmt='bgr')
      self.textures[id] = texture
      self.logger.debug('找到id对应的widget，绑定texture，不存在就返回')
      widget = self.form.ids.get(id)
      if widget is None:
        return
      with widget.canvas:
        size = self.form.ids.get('now_image').size
        kivy.graphics.Rectangle(texture=texture, size=size, pos=widget.pos)
    self.logger.debug('初始化texture')
    try_create_texture('now_image')
    try_create_texture('abnormal_image')
    self.dirty['frame'] = True

    self.logger.debug('更新分类信息')
    classes = self.model.now['classes']
    if classes is not None:
      self.classes = tuple(map(lambda i: (*i, Abnormal.Abnormal.color(i[0])), classes))
      self.dirty['classes'] = True

  def before_every_video(self):
    """
    处理每一个视频前都会调用该函数

    清空textures，resize

    可以从self.model.now中获取model信息:
      name:          当前文件名称
      size:          视频长宽，由配置文件定义

    当然也可以直接读取self.model的变量，但请不要从这里修改
    """
    self.textures.clear()
    self.logger.debug('显示视频名称')
    image = self.form.ids.get('image')
    if image is None:
      return
    name = self.model.now.get('name')
    if name is None:
      return
    image.text = name
    """
    resize

    解释:window上大小经过严格计算
    width:300*2(两个视频宽度)+10(两视频中间spacing)+400(饼图宽度)+20(视频和饼图spacing)
    height:50(label高度)+300/1080*1920(视频高度)+100(button高度)+10(button和视频的spacing)+20(上下高度padding)
    retina:-520和-350是玄学出来的
    """
    if self.settings['Retina']:
      self.wsize = (dp(300*2+10+400+20-520),dp(50+300/1080*1920+100+10+20-350))
    else:
      self.wsize = (dp(300*2+10+400+20),dp(50+300/1080*1920+100+10+20))
    self.dirty['video'] = True
    self.logger.debug(self.wsize)

  RUNNING = 'running'
  PAUSED = 'paused'
  def pause(self):
    """
    用户点击暂停按钮
    """
    btn = self.form.ids.get('pause')
    if btn is None:
      self.logger.error('pause button not found')
      return
    if self.states['APP'] is BSOFApp.RUNNING:
      self.states['APP'] = BSOFApp.PAUSED
      btn.text = translate('Continue')
    elif self.states['APP'] is BSOFApp.PAUSED:
      self.states['APP'] = BSOFApp.RUNNING
      btn.text = translate('Pause')
    self.model.pause()

  @staticmethod
  def __mouse_pos(pos, widget_pos, widget_size):
    """
    计算鼠标在控件中的相对位置并返回

    Args:
      pos         鼠标位置
      widget_pos  控件位置
      widget_size 控件长宽
    Return:
      若在控件内，则返回相对坐标
      若在控件外，则返回None
    """
    leftdown = widget_pos
    rightup = (leftdown[0] + widget_size[0], leftdown[1] + widget_size[1])
    return point_in_rect(pos, (leftdown, rightup))

  @staticmethod
  def __rect_properties(old_pos, new_pos, widget_pos, widget_size):
    """
    计算蓝框位置的比例并返回
    """
    x0, y0 = widget_pos
    w, h = widget_size
    rect = trim_to_rect((
      (old_pos[0] + x0, old_pos[1] + y0),
      new_pos
    ), (
      widget_pos,
      (x0 + w, y0 + h)
    ))
    if rect is None:
      return
    (x1, y1), (x2, y2) = rect
    return (
      ((x1 - x0) / w, (y1 - y0) / h),
      ((x2 - x0) / w, (y2 - y0) / h)
    )

  def __mouse_pos_text(self):
    """
    用于鼠标位置的可视化
    """
    x, y = self.mouse_pos
    self.form.ids['parameter'].text = f'x:{x}\ny:{y}'

  NOT_READY = 'not_ready'
  READY     = 'ready'
  DOING     = 'doing'
  FREEZE    = 'freeze'

  def on_mouse_down(self, pos, widget_pos, widget_size):
    """
    按下鼠标左键
    """
    if self.states['BOX'] is not BSOFApp.READY:
      return
    pos = BSOFApp.__mouse_pos(pos, widget_pos, widget_size)
    if pos is None:
      return
    self.states['BOX'] = BSOFApp.DOING
    self.mouse_pos = pos
    self.__mouse_pos_text()
    if self.states['APP'] is BSOFApp.PAUSED:
      return
    self.pause()

  def on_mouse_up(self, pos, widget_pos, widget_size):
    """
    按下鼠标右键
    """
    if self.states['BOX'] is not BSOFApp.DOING:
      return
    self.states['BOX'] = BSOFApp.READY
    rect = BSOFApp.__rect_properties(self.mouse_pos, pos, widget_pos, widget_size)
    self.model.box = rect
    self.mouse_pos = None
    self.pause()

  def on_mouse_enter(self, window):
    """
    鼠标进入界面事件
    """
    if self.states['BOX'] is not BSOFApp.FREEZE:
      return
    self.states['BOX'] = BSOFApp.DOING

  def on_mouse_leave(self, window):
    """
    鼠标离开界面事件
    """
    if self.states['BOX'] is not BSOFApp.DOING:
      return
    self.states['BOX'] = BSOFApp.FREEZE

  def on_stop(self):
    """
    关闭时被调用

    Self:
      model.thread_stop     告知线程停止，线程将在这个循环完成过后退出（关闭掉输出）
      model_runner          等待线程
    """
    self.logger.debug('准备退出，呼叫线程关闭')
    self.model.thread_stop = True
    self.model_runner.join()

  def on_resize(self, window, width, height):
    """
    当窗口改变size的时候调用

    Self:
      wsize   当前视频对应的窗口应有的大小
    """
    if self.wsize is None or (width, height) == self.wsize:
      self.logger.debug('不需要改变')
      return
    self.logger.debug('又改回去')
    window.size = self.wsize

  def build(self):
    """
    创建窗口时调用

    Self:
      form    窗口类
    """
    kivy.core.window.Window.bind(on_resize=self.on_resize)
    kivy.core.window.Window.bind(on_cursor_enter=self.on_mouse_enter)
    kivy.core.window.Window.bind(on_cursor_enter=self.on_mouse_leave)
    # 设置背景色
    kivy.core.window.Window.clearcolor = (1, 1, 1, 1)
    """
    创建canvas
    """
    self.form = GUI.BSOFForm.BSOFForm.load()
    self.form.ids['abnormal'].text = translate('abnormal')
    self.form.ids['pause'].text    = translate('pause')
    return self.form

if __name__ == '__main__':
  app = BSOFApp()
  try:
    app.run()
  except KeyboardInterrupt:
    """
    用户键盘打断
    """
    app.on_stop()
  except UnicodeDecodeError as ude:
    """
    .kv文件的Unicode的问题，kivy的load_file不支持Unicode。
    """
    lktools.LoggerFactory.LoggerFactory.default().error(ude)
  except Exception as e: 
    """
    其它error
    """
    lktools.LoggerFactory.LoggerFactory.default().error(e)
