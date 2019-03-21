"""
json5
"""
import json5
"""
logger
"""
import lktools.LoggerFactory

dictionaries = {}
settings = lktools.Loader.get_settings()
logger = lktools.LoggerFactory.LoggerFactory('Translator').logger

def translate(raw, language=None):
  if language is None:
    language = settings['language'].lower()
  elif type(language) != str:
    logger.error(f'language {language} must be str')
    return
  if language == 'english':
    return raw
  raw = raw.lower()
  dictionary = dictionaries.get(language)
  if dictionary is None:
    with open(f'resources/strings/{language}.json', encoding='utf-8') as f:
      dictionary = json5.load(f)
    if dictionary is None:
      logger.error(f'cannot read language ({language}) file.')
      return
    dictionaries[language] = dictionary
  return dictionary.get(raw)
