import kivy.uix.boxlayout
import kivy.lang

class BSOFForm(kivy.uix.boxlayout.BoxLayout):
  """
  此处类定义虽然为空，但会将my.kv的GUI定义的相关“程序”引入，即相当于在此定义
  """
  @staticmethod
  def load():
    return kivy.lang.Builder.load_file('resources/views/BSOFForm.kv')
