"""
json
"""
import json5
"""
about filesystem
"""
import shutil
import os
import glob
"""
log
"""
import logging
"""
lktools
"""
import lktools.LoggerFactory
import lktools.Checker

template = """{
  "path": "../video",                     // 视频路径
  "videos": ["*"],                        // 视频列表，"*"为通配符
  "delay": 10,                            // 视频播放延迟，用于cv2.waitKey第一个参数
  "height": 480,                          // 视频高度限定，宽度会自动计算
  "frame_range": [0, 100],                // 取[a, b]帧
  "img_path": "images.tmp",               // 图片存取路径
  "video_path": "videos.tmp",             // 视频存取路径
  "file_output": false,                   // 是否输出到文件夹
  "interval": 10,                         // 用前N帧图片作为修正的标准
  "fps": 10,                              // 保存视频帧数
  "time_debug": false,                    // 是否打印每个函数耗时
  "limit_size": 10,                       // 光流法的参数
  "compression_ratio": 1.0,               // 光流法的压缩率
  "linux": false,                         // 是不是linux，linux不会执行显示相关的函数
  "sift": true,                           // 是否开启sift对齐
  "OF": true,                             // 是否开启光流法
  "debug_level": "info",                  // 等级debug -> info -> warn -> error -> critical，会打印该级别级以上的Logger信息
  "app_fps": 60,                          // app刷新率
  "varThreshold": 121.0,                  // 高斯混合模型的阈值，决定模型是否灵敏，越小越敏感
  "detectShadows": false                  // 高斯混合模型的阴影识别，True开启后影响速度
}"""
user_settings = None

def get_settings():
  global user_settings
  if user_settings is not None:
    return user_settings

  logger = lktools.LoggerFactory.LoggerFactory('Loader', level=logging.INFO).logger

  if not os.path.exists('settings.json'):
    logger.error('settings.json not found')
    from sys import exit
    exit(1)

  checker = lktools.Checker.Checker(logger)

  logger.debug('设置')

  with open('settings.json', encoding='utf-8') as f:
    user_settings = json5.load(f)

  logger.debug('load user setting')

  checker.container = user_settings

  logger.debug('load default')

  # tuple(map(lambda item: user_settings.setdefault(*item), json5.loads(template).items()))
  default_settings = json5.loads(template)
  for item in default_settings.items():
    user_settings.setdefault(*item)

  logger.debug('check type')

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
      'file_output', 'time_debug',
      'linux', 'sift', 'OF', 'detectShadows',
    ), bool
  )
  checker.check(
    (
      'delay', 'height', 'interval',
      'fps', 'limit_size', 'app_fps',
    ), int
  )
  checker.check(
    (
      'compression_ratio', 'varThreshold', 
    ), float
  )

  logger.debug('check legal')

  checker.check('videos', checker.len_not_zero)
  checker.check('frame_range', checker.range)
  checker.check('debug_level', checker.debug_level)
  checker.check(
    (
      'delay', 'height',
      'interval', 'fps',
      'limit_size', 'compression_ratio',
      'app_fps', 'varThreshold'
    ), checker.plus
  )

  if checker.dirty:
    logger.error("参数检查失败。。。请调整后再运行")
    from sys import exit
    exit(1)

  logger.debug('将debug_level转换为logging.枚举类型')

  debug_level = user_settings['debug_level']
  user_settings['debug_level'] = {
    'debug':    logging.DEBUG,
    'info':     logging.INFO,
    'warn':     logging.WARN,
    'error':    logging.ERROR,
    'critical': logging.CRITICAL,
  }[debug_level]

  logger.debug("去掉路径最后的'/'")

  path = user_settings['path']
  if path[-1] == '/':
    path = path[:-1]
    user_settings['path'] = path

  logger.debug('将设置中的文件转换为绝对地址，匹配videos')

  videos = user_settings['videos']

  __videos = []
  for video in videos:
    for f in glob.glob(f'{path}/{video}'):
      f = f.replace('\\', '/')
      splits = f.split('.')
      if len(splits) <= 1:
        logger.debug('文件没有扩展名')
        continue
      name = splits[-2].split('/')[-1]
      if len(name) == 0:
        logger.debug('无名特殊文件')
        continue
      __videos.append((name, f))

  user_settings['videos'] = __videos

  logger.debug('测试的情况下该返回了')

  if __name__ == '__main__':
    return user_settings

  logger.debug('清空输出文件夹')

  if user_settings['file_output']:
    img_path = user_settings['img_path']
    if os.path.exists(img_path):
      shutil.rmtree(img_path)
    os.mkdir(img_path)
    video_path = user_settings['video_path']

    logger.debug('img和video在一个路径下就不重复做了')

    if img_path != video_path:
      if os.path.exists(video_path):
        shutil.rmtree(video_path)
      os.mkdir(video_path)
  return user_settings 

if __name__ == '__main__':
  settings = get_settings()
  print(settings)
