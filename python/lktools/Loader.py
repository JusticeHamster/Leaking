import json5
import shutil
import os

template = """{
  "path": "../video",                     // 视频路径
  "videos": ["???.mp4"],                  // 视频列表
  "delay": 100,                           // 视频播放延迟，用于cv2.waitKey第一个参数
  "height": 480,                          // 视频高度限定，宽度会自动计算
  "frame_range": [0, 100],                // 取[a, b]帧
  "img_path": "tmp",                      // 图片存取路径
  "video_path": "tmp",                    // 视频存取路径
  "time_test": false,                     // 是否测试时间，会关闭所有输出
  "lastn": 1,                             // 用前N帧图片作为修正的标准
  "fps": 10,                              // 保存视频帧数
  "time_debug": false,                    // 是否打印每个函数耗时
  "limit_size": 10,                       // 光流法的参数
  "compression_ratio": 1,                 // 光流法的压缩率
  "linux": false                          // 是不是linux，linux不会执行显示相关的函数
}"""
user_settings = None

def get_settings():
  global user_settings
  if user_settings is not None:
    return user_settings
  # 设置
  with open('settings.json', encoding='utf-8') as f:
    user_settings = json5.load(f)
  default_settings = json5.loads(template)
  for item in default_settings.items():
    user_settings.setdefault(*item)
  # 去掉路径最后的'/'
  path = user_settings['path']
  if path[-1] == '/':
    path = path[:-1]
    user_settings['path'] = path
  # 将设置中的文件转换为绝对地址
  user_settings['videos'] = tuple(map(
    lambda n: (n.split('.')[0], '{path}/{name}'.format(
      path=path,
      name=n
    )),
    user_settings['videos']
  ))
  # 测试的情况下该返回了
  if __name__ == '__main__':
    return user_settings
  # 清空输出文件夹
  if not user_settings['time_test']:
    img_path = user_settings['img_path']
    if os.path.exists(img_path):
      shutil.rmtree(img_path)
    os.mkdir(img_path)
    video_path = user_settings['video_path']
    # img和video在一个路径下就不重复做了
    if img_path != video_path:
      if os.path.exists(video_path):
        shutil.rmtree(video_path)
      os.mkdir(video_path)
  return user_settings 

if __name__ == '__main__':
  settings = get_settings()
  print(settings)
