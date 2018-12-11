"""
json5
"""
import json5
"""
logger
"""
import lktools.LoggerFactory

dictionaries = {}
logger = lktools.LoggerFactory.LoggerFactory('Translator').logger

def translate(raw, language):
  if type(language) != str:
    logger.error(f'"{language}" must be str')
    return
  language = language.lower()
  if language == 'english':
    return raw
  raw = raw.lower()
  dictionary = dictionaries.get(language)
  if dictionary is None:
    with open(f'resources/strings/{language}.json', encoding='utf-8') as f:
      dictionary = json5.load(f)
    dictionaries[language] = dictionary
  return dictionary.get(raw)
