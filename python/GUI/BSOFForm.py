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
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.graph = None

  @staticmethod
  def load():
    """
    载入对应的kv文件
    """
    return kivy.lang.Builder.load_file('resources/views/BSOFForm.kv')

  def histogram(self, serie, **kwargs):
    """
    添加柱状图
    """
    if self.graph is not None:
      self.graph.serie = serie
      return

    graph_area = self.ids['graph_area']
    self.graph = GUI.BSOFGraph.BSOFGraph.load(serie=serie, **kwargs)
    # histogram
    # graph_area.add_widget(self.graph.get_widget())
    # pizza
    graph_area.add_widget(self.graph)
