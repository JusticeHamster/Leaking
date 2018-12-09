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
"""
kivy related
"""
import kivy.lang
import kivy.app
import kivy.graphics
import kivy.clock
import kivy.graphics.texture
import kivy.uix.boxlayout

class MyForm(kivy.uix.boxlayout.BoxLayout):
  """
  此处类定义虽然为空，但会将my.kv的GUI定义的相关“程序”引入，即相当于在此定义
  """
  def update(self, img_path):
    pass

class BSOFApp(kivy.app.App):
  """
  App GUI for BSOFModel
  """
  def on_start(self):
    """
    准备，并开始

    self：
      settings：        用户配置文件，settings.json
      logger：          日志，debug记录流程（默认不会打印），info及以上显示必要信息
      model：           BSOFModel模型
      textures：        缓存
      clock：           定时调用
    """
    self.settings = lktools.Loader.get_settings()
    self.logger = lktools.LoggerFactory.LoggerFactory('App').logger
    self.model = BSOFModel(False)
    self.textures = {}
    self.clock = kivy.clock.Clock.schedule_interval(self.on_clock, 1 / self.settings['app_fps'])

    self.logger.debug('设置回调函数')

    self.model.every_frame = self.every_frame
    self.model.before_every_video = self.before_every_video

    self.logger.debug('运行model')

    self.model_runner = threading.Thread(target=self.model.run)
    self.model_runner.start()

  def on_clock(self, delta_time):
    """
    计时器到时间就调用

    Args:
      delta_time:   计时时间

    由settings.json中的app_fps指定
    """
    self.logger.debug(f'on_clock: {delta_time}')
    def update(self, data, id):
      data = self.model.now.get(data)
      if data is None:
        return
      texture = self.textures.get(id)
      if texture is None:
        return
      self.logger.debug(f'处理{id}:')
      self.logger.debug('更新数据')
      data = data[::-1]
      texture.blit_buffer(data.tostring(), colorfmt='rgb', bufferfmt='ubyte')
      self.logger.debug('刷新')
      self.form.ids[id].canvas.ask_update()
    self.logger.debug('-------------')
    update(self, 'frame', 'now_image')

  def every_frame(self):
    """
    每一帧都会调用该函数

    这个函数不在主线程，不能在这里调用blit_buffer（无效）

    从self.model.now中获取model信息：
      name：          当前文件名称
      frame：         当前帧的uint8拷贝
      frame_rects：   当前帧（框出异常）
      binary：        二值图像（是一个dict，包含{'OF', 'BS'}两种，详情见BSOFModel）

    当然也可以直接读取self.model的变量，但请不要从这里修改
    """
    def try_create_texture(self, id):
      self.logger.debug('如果已经存在了就返回')
      texture = self.textures.get(id)
      if texture is not None:
        return
      self.logger.debug('创建新的texture，并存入缓存')
      size = self.model.now['frame'].shape[1::-1]
      texture = kivy.graphics.texture.Texture.create(size=size, colorfmt='rgb')
      self.textures[id] = texture
      self.logger.debug('找到id对应的widget，绑定texture，不存在就返回')
      widget = self.form.ids.get(id)
      if widget is None:
        return
      with widget.canvas:
        kivy.graphics.Rectangle(texture=texture, size=size)
    self.logger.debug('-------------')
    self.logger.debug('初始化texture')
    try_create_texture(self, 'now_image')

  def before_every_video(self):
    """
    处理每一个视频前都会调用该函数

    清空textures

    可以从self.model.now中获取model信息：
      name：          当前文件名称

    当然也可以直接读取self.model的变量，但请不要从这里修改
    """
    self.textures = {}

  def on_stop(self):
    """
    关闭时被调用
    """
    self.logger.debug('准备退出，呼叫线程关闭')
    self.model.thread_stop = True
    self.model_runner.join()

  def build(self):
    """
    创建窗口时调用

    Self:
      form    窗口类
    """
    self.form = kivy.lang.Builder.load_file('resources/views/BSOFApp.kv')
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
  except:
    """
    其它error
    """
    app.on_stop()