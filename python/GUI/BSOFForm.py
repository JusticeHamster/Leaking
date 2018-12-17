"""
kivy
"""
import kivy.uix.boxlayout
import kivy.lang
"""
app
"""
import GUI.BSOFGraph

class BSOFForm(kivy.uix.boxlayout.BoxLayout):
  """
  此处类定义虽然为空，但会将BSOFForm.kv的GUI定义的相关“程序”引入，即相当于在此定义
  """
  @staticmethod
  def load():
    form = kivy.lang.Builder.load_file('resources/views/BSOFForm.kv')
    graph = GUI.BSOFGraph.BSOFGraph.load()
    form.ids['graph_area'].add_widget(graph)
    return form
