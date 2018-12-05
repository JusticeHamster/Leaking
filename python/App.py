from BSOFModel import BSOFModel
import lktools.Loader
import lktools.LoggerFactory
import kivy.lang
import kivy.app

kv = kivy.lang.Builder.load_string('''
Button:
  text: "I was created by kv codes"
''')

class App(kivy.app.App):
  """
  App GUI for BSOFModel
  """

  def __init__(self):
    super().__init__()
    self.settings = lktools.Loader.get_settings()
    self.logger = lktools.LoggerFactory.LoggerFactory('App').logger
    self.model = BSOFModel(False)

  def build(self):
    self.logger.info('build')
    return kv

if __name__ == '__main__':
  App().run()