import json5
import shutil
import os
from lktools import LoggerFactory
from lktools import Checker

template = """{
  "path": "../video",                     // 视频路径
  "videos": [],                           // 视频列表
  "delay": 10,                            // 视频播放延迟，用于cv2.waitKey第一个参数
  "height": 480,                          // 视频高度限定，宽度会自动计算
  "frame_range": [0, 100],                // 取[a, b]帧
  "img_path": "images.tmp",               // 图片存取路径
  "video_path": "videos.tmp",             // 视频存取路径
  "time_test": false,                     // 是否测试时间，会关闭所有输出
  "interval": 10,                         // 用前N帧图片作为修正的标准（由于命名冲突，lastn修改为interval）
  "fps": 10,                              // 保存视频帧数
  "time_debug": false,                    // 是否打印每个函数耗时
  "limit_size": 10,                       // 光流法的参数
  "compression_ratio": 1,                 // 光流法的压缩率
  "linux": false,                         // 是不是linux，linux不会执行显示相关的函数
  "sift": true,                           // 是否开启sift对齐
  "OF": true,                             // 是否开启光流法
  "debug_level": "info",                  // 等级debug -> info -> warn -> error -> critical，会打印该级别级以上的Logger信息
}"""
user_settings = None

def get_settings():
  global user_settings
  if user_settings is not None:
    return user_settings

  logger = LoggerFactory.LoggerFactory('Loader')()
  checker = Checker.Checker('Loader')

  def _exist(name, containers):
    item = containers['setting'].get(name)
    if item is None:
      logger.error(f'"{name}" must exists')
    return item

  def _len_not_zero(name, containers):
    item = _exist(name, containers)
    if item is None:
      return
    if len(item) == 0:
      logger.error(f'size of "{name}" must > 0')

  def _int_plus(name, containers):
    item = _exist(name, containers)
    if item is None:
      return
    if not (item > 0):
      logger.error(f'"{name}" must > 0')

  def _range(name, containers):
    item = _exist(name, containers)
    if item is None:
      return
    if len(item) != 2:
      logger.error(f'range "{name}" must have and only have 2 elements')
    if item[0] < 0:
      logger.error(f'range {name}[0] must > 0')
    if item[0] > item[1]:
      logger.error(f'range {name}[0] must <= {name}[1]')

  def _debug_level(name, containers):
    item = _exist(name, containers)
    if item is None:
      return
    debug_list = ('debug', 'info', 'warn', 'error', 'critical')
    if item not in debug_list:
      logger.error(f'"{name}" was "{item}", not in {debug_list}')

  def _type(name, assert_type, containers):
    item = _exist(name, containers)
    if item is None:
      return
    if type(item) != assert_type:
      logger.error(
        f'{name} must be type {assert_type} but find {type(item)}'
      )

  checker.add_assert('exist',       _exist        )
  checker.add_assert('not_zero',    _len_not_zero )
  checker.add_assert('plus',        _int_plus     )
  checker.add_assert('range',       _range        )
  checker.add_assert('debug_level', _debug_level  )
  checker.add_assert('type',        _type         )

  logger.info('设置')

  with open('settings.json', encoding='utf-8') as f:
    user_settings = json5.load(f)

  logger.info('load user setting')

  checker.add_container('setting', user_settings)

  logger.info('load default')

  default_settings = json5.loads(template)
  for item in default_settings.items():
    user_settings.setdefault(*item)

  logger.info('check type')

  checker.check(
    (
      'path', 'debug_level',
      'img_path', 'video_path',
    ), str
  )
  checker.check(
    (
      'videos', 'frame_range',
    ), list
  )
  checker.check(
    (
      'time_test', 'time_debug',
      'linux', 'sift', 'OF'
    ), bool
  )
  checker.check(
    (
      'delay', 'height', 'interval',
      'fps', 'limit_size'
    ), int
  )
  checker.check('compression_ratio', float)

  logger.info('check legal')

  checker.check('videos', 'not_zero')
  checker.check('frame_range', 'range')
  checker.check('debug_level', 'debug_level')
  checker.check(
    (
      'delay', 'height',
      'interval', 'fps',
      'limit_size', 'compression_ratio',
    ), 'plus'
  )

  logger.info("去掉路径最后的'/'")

  path = user_settings['path']
  if path[-1] == '/':
    path = path[:-1]
    user_settings['path'] = path

  logger.info('将设置中的文件转换为绝对地址')

  user_settings['videos'] = tuple(map(
    lambda n: (n.split('.')[0], f'{path}/{n}'),
    user_settings['videos']
  ))

  logger.info('测试的情况下该返回了')

  if __name__ == '__main__':
    return user_settings

  logger.info('清空输出文件夹')

  if not user_settings['time_test']:
    img_path = user_settings['img_path']
    if os.path.exists(img_path):
      shutil.rmtree(img_path)
    os.mkdir(img_path)
    video_path = user_settings['video_path']

    logger.info('img和video在一个路径下就不重复做了')

    if img_path != video_path:
      if os.path.exists(video_path):
        shutil.rmtree(video_path)
      os.mkdir(video_path)
  return user_settings 

if __name__ == '__main__':
  settings = get_settings()
  print(settings)
