"""
numpy
"""
import numpy
"""
matplotlib
"""
import matplotlib.font_manager
import matplotlib.pyplot as plt
"""
kivy
"""
import kivy.uix.widget
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.garden.matplotlib.backend_kivy import FigureCanvasKivy
"""
pizza
"""
import kivy.garden.pizza
"""
abnormal
"""
from resources.data.Abnormal import Abnormal 
"""
拼音
"""
from xpinyin import Pinyin
pinyin = Pinyin()

class BSOFGraph(kivy.uix.widget.Widget):
  """
  显示类
  """
  #''' deprecated 饼图 pizza
  @staticmethod
  def load(*args, **kwargs):
    """
    serie: ( ('class', percentage, 'color'), ... )
    """
    return kivy.garden.pizza.Pizza(
      serie=kwargs.get('serie'),
      legend_color=kwargs.get('legend_color', '000000'),
      legend_value_rayon=kwargs.get('legend_value_rayon', dp(80)),
      legend_title_rayon=kwargs.get('legend_title_rayon', dp(160)),
      chart_size=kwargs.get('chart_size', dp(256)),
      chart_border=kwargs.get('chart_border', dp(1)),
      font_name=kwargs.get('font_name', 'resources/fonts/msyh'),
    )
  #'''
  """
  serie: ( ('class', percentage, 'color'), ... )
  """
  """
  serie = ListProperty()

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    # plt settings
    plt.rcdefaults()
    _, ax = plt.subplots()

    title_font = matplotlib.font_manager.FontProperties(
      fname='resources/fonts/msyh.ttf',
      size=40
    )
    class_font = matplotlib.font_manager.FontProperties(
      fname='resources/fonts/msyh.ttf',
      size=25
    )
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    ax.invert_yaxis()  # labels read top-to-bottom
    classes = list(map(lambda c: pinyin.get_pinyin(c, ' '), Abnormal.classes()))
    y_pos = numpy.arange(len(classes))
    ax.set_yticks(y_pos)
    ax.set_yticklabels(classes, fontproperties=class_font)

    plt.title('Classes', fontproperties=title_font)
    plt.xlabel('Probability', fontproperties=title_font)

    # self
    self.ax = ax
    self.y_pos = y_pos
    self.classes = classes
    self.plt_widget = FigureCanvasKivy(plt.gcf())
    self.bind(
      serie=self.update_histogram
    )

  def update_histogram(self, *args):
    self.ax.barh(
      self.y_pos, list(map(lambda s: s[1], self.serie)),
      align='center', color='blue'
    )
    self.plt_widget.draw()

  def get_widget(self):
    return self.plt_widget
  @staticmethod
  def load(*args, **kwargs):
    return BSOFGraph(**kwargs)
  """
