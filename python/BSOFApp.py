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
import kivy.graphics.texture
import kivy.uix.boxlayout
from kivy.properties import ObjectProperty, StringProperty

texture = None

class MyForm(kivy.uix.boxlayout.BoxLayout):  # 此处类定义虽然为空，但会将my.kv的GUI定义的相关“程序”引入，即相当于在此定义
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
    """
    self.settings = lktools.Loader.get_settings()
    self.logger = lktools.LoggerFactory.LoggerFactory('App').logger
    self.model = BSOFModel(False)

    self.logger.debug('设置回调函数')

    self.model.every_frame = lambda: self.every_frame()

    self.logger.debug('运行model')

    self.model_runner = threading.Thread(target=self.model.run)
    self.model_runner.start()

  def every_frame(self):
    """
    每一帧都会调用该函数

    从self.model.now中获取model信息：
      name：          当前文件名称
      frame：         当前帧的uint8拷贝
      frame_rects：   当前帧（框出异常）
      binary：        二值图像（是一个dict，包含{'OF', 'BS'}两种，详情见BSOFModel）

    当然也可以直接读取self.model的变量，但请不要从这里修改
    """
    frame = self.model.now['frame']
    size = frame.shape[1::-1]
    global texture
    if texture is None:
      texture = kivy.graphics.texture.Texture.create(size=size, colorfmt='rgb')
      with self.Form.ids.now_image.canvas:
        kivy.graphics.Rectangle(texture=texture, size=size)
    texture.blit_buffer(frame.tostring(), colorfmt='rgb', bufferfmt='ubyte')
    self.Form.ids.now_image.canvas.ask_update()

  def on_stop(self):
    self.model.thread_stop = True
    self.model_runner.join()

  def build(self):
    self.Form = kivy.lang.Builder.load_file('resources/views/BSOFApp.kv')
    return self.Form

if __name__ == '__main__':
  BSOFApp().run()