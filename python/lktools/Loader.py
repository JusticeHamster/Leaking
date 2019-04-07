"""
json
"""
import json5
"""
filesystem
"""
import os
"""
log
"""
import logging
"""
lktools
"""
import lktools.LoggerFactory
import lktools.Checker
"""
check
"""
from resources.data import check

user_settings = None

def get_settings():
  global user_settings
  if user_settings is not None:
    return user_settings

  logger = lktools.LoggerFactory.LoggerFactory('Loader', level=logging.INFO).logger

  if not os.path.exists('settings.json') or \
     not os.path.exists('resources/data/template.json'):
    logger.error('settings.json not found')
    from sys import exit
    exit(1)

  logger.debug('设置')

  with open('settings.json', encoding='utf-8') as f:
    user_settings = json5.load(f)

  with open('resources/data/template.json', encoding='utf-8') as f:
    default_settings = json5.load(f)

  logger.debug('Checker')

  checker = lktools.Checker.Checker(logger, user_settings)

  logger.debug('Default Settings')

  # tuple(map(lambda item: user_settings.setdefault(*item), json5.loads(template).items()))
  for item in default_settings.items():
    user_settings.setdefault(*item)

  return check.check(
    logger, checker, user_settings,
    __name__ == '__main__'
  )

if __name__ == '__main__':
  settings = get_settings()
  print(settings)
