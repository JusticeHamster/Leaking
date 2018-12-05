from kivy.app import App
from kivy.lang import Builder

kv = Builder.load_string('''
Button:
  text: "I was created by kv codes"
''')

class TestApp(App):
  def build(self):
    return kv

TestApp().run()