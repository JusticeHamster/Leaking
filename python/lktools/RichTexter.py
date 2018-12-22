"""
logger
"""
import lktools.LoggerFactory

logger = lktools.LoggerFactory.LoggerFactory('RichTexter').logger

"""
或者你可以直接使用富文本
"""

def bold(text):
  return f'[b]{text}[/b]'

def Italic(text):
  return f'[i]{text}[/i]'

def color(text, rgb):
  return f'[color={rgb}]{text}[/color]'
