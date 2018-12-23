"""
kivy
"""
import kivy.uix.widget
import kivy.garden.pizza

class BSOFGraph(kivy.uix.widget.Widget):
  """
  显示类
  """
  @staticmethod
  def load(*args, **kwargs):
    """
    serie: ( ('class', percentage, 'color'), ... )
    """
    return kivy.garden.pizza.Pizza(
      serie=kwargs.get('serie'),
      legend_color=kwargs.get('legend_color', '000000'),
      legend_value_rayon=kwargs.get('legend_value_rayon', 160),
      legend_title_rayon=kwargs.get('legend_title_rayon', 320),
      chart_size=kwargs.get('chart_size', 512),
      chart_border=kwargs.get('chart_border', 2),
      font_name=kwargs.get('font_name', 'resources/fonts/msyh'),
    )