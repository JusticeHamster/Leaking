
from math import sin
"""
kivy
"""
import kivy.lang
import kivy.uix.widget
import kivy.properties
from kivy.garden.graph import MeshLinePlot

class BSOFGraph(kivy.uix.widget.Widget):
  graph_test = kivy.properties.ObjectProperty(None)

  def update_graph(self):
    plot = MeshLinePlot(color=[1, 0, 0, 1])
    plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
    self.graph_test.add_plot(plot)

  @staticmethod
  def load():
    return kivy.lang.Builder.load_file('resources/views/BSOFGraph.kv')