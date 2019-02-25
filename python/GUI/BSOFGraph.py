"""
kivy
"""
import kivy.uix.widget
# import kivy.garden.pizza
import matplotlib.pyplot as plt

from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

class BSOFGraph(kivy.uix.widget.Widget):
  """
  显示类
  """
  ''' deprecated 饼图 pizza
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
  '''
  """
  serie: ( ('class', percentage, 'color'), ... )
  """
  serie = ListProperty()

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.serie = kwargs.get('serie')

    plt.hist(tuple(map(lambda t: t[1], self.serie)))
    plt.title('Histogram')
    plt.xlabel('Value')
    plt.ylabel('Frequency')

    gcf = plt.gcf()
    self.plt_canvas = gcf.canvas
    self.plt_widget = FigureCanvasKivyAgg(gcf)

    self.bind(
      serie=self.update_histogram
    )

  def update_histogram(self, *args):
    plt.clf()
    plt.hist(self.serie)

    self.plt_canvas.draw()

  def get_widget(self):
    return self.plt_widget

  @staticmethod
  def load(*args, **kwargs):
    return BSOFGraph(**kwargs)
