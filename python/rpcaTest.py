# import
import numpy as np
import cv2
import os
import RPCA
# 读取设置
"""{rpca.settings 格式要求:}
path=XXX
videos=X.mp4;Y.mp4
delay=?     // 视频播放延迟，默认100
height=?    // 视频高度限定，宽度会自动计算，默认192
maxFrames=? // 取前N帧，默认100
fps=?       // 导出视频帧数，默认60
"""
settings = {}
with open('rpca.settings', encoding='utf-8') as f:
  for line in f.readlines():
    strs = line.split('=')
    settings[strs[0].strip()] = strs[1].strip()
# 设置
full_path = settings['path']
videos = settings['videos']
delay = int(settings.get('delay', 100))
  # 所需视频的高度
height = int(settings.get('height', 192))
maxFrames = int(settings.get('maxFrames', 100))
fps = int(settings.get('fps', 60))
# 将设置中的文件转换为绝对地址
def videos_path(videos):
  return map(
    lambda n: (n, '{path}/{name}'.format(
      path=full_path,
      name=n
    )),
    videos.split(';')
  )
# 运行
def run(name, path):
  if not os.path.exists(path):
    print('no such file: {path}'.format(path=path))
    return
  # init
  capture = cv2.VideoCapture(path)
  data = None
  # run
  print('read {path}'.format(path=path))
  nframes = 0
  # 放缩
  m = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
  n = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
  scale = height / m
  m = height
  n = int(n * scale)
  while capture.isOpened():
    if nframes >= maxFrames:
      break
    success, frame = capture.read()
    if not success:
      break
    nframes += 1
    frame = cv2.resize(frame, (n, m))
    # 转换为灰度图
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 加入矩阵列中
    frame = np.array(frame).reshape(-1, 1)
    if data is None:
      data = frame
    else:
      data = np.hstack((data, frame))
  capture.release()
  # 调用RPCA算法
  print('run')
  h = RPCA.rpcaADMM(data)
  print('end {path}'.format(path=path))
  # 写入文件
  size = (m, n)
  videoWriter = cv2.VideoWriter()
  videoWriter.open(
    '{name}.mp4'.format(name=name),
    cv2.VideoWriter_fourcc(*'mp4v'),
    fps,
    size,
    False
  )
  count = 0
  while count < nframes:
    X1 = h['X1_admm']
    X2 = h['X2_admm']
    X3 = h['X3_admm']
    #
    picture = np.hstack((
      (X1[:, count].reshape(size)),
      (X2[:, count].reshape(size)),
      (X3[:, count].reshape(size)),
    ))
    videoWriter.write(picture)
    #
    count += 1
  videoWriter.release()
# run
if __name__ == '__main__':
  for name, video in videos_path(videos):
    run(name, video)