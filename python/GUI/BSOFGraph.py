"""
kivy
"""
import kivy.uix.widget
import kivy.garden.pizza
from kivy.metrics import dp

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
