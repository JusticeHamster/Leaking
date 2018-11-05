# import
import numpy as np
import cv2
import RPCA
# 读取设置
"""{rpca.settings 格式要求:}
path=XXX
videos=X.mp4;Y.mp4
"""
settings = {}
with open('rpca.settings', encoding='utf-8') as f:
  for line in f.readlines():
    strs = line.split('=')
    settings[strs[0].strip()] = strs[1].strip()
# 设置
full_path = settings['path']
videos = settings['videos']
# 将设置中的文件转换为绝对地址
def videos_path(videos):
  return map(
    lambda n: '{path}/{name}'.format(
      path=full_path,
      name=n
    ),
    videos.split(';')
  )
# 运行
def run(path):
  # 视频压缩的长宽
  m, n = 192, 108
  # ini
  capture = cv2.VideoCapture(path)
  data = None
  # run
  print('read {path}'.format(path=path))
  nframes = 0
  while capture.isOpened():
    success, frame = capture.read()
    if not success:
      break
    nframes += 1
    frame = cv2.resize(frame, (n, m))
    # 转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.array(gray).reshape(-1, 1)
    # 加入矩阵列中
    if data is None:
      data = gray
    else:
      data = np.hstack((data, gray))
      print(data)
  capture.release()
  # 调用RPCA算法
  print('run')
  h = RPCA.rpcaADMM(data)
  print('end {path}'.format(path=path))
  # 展示
  count = 0
  while count < nframes:
    X1 = h['X1_admm']
    X2 = h['X2_admm']
    X3 = h['X3_admm']
    #
    cv2.imshow(path, X1[:, count].reshape((m, n)))
    #
    count += 1
    if cv2.waitKey(100) & 0xFF == ord('q'):
      break
# run
if __name__ == '__main__':
  for video in videos_path(videos):
    run(video)
    # wait
    input('<enter to continue>')
    # free
    cv2.destroyAllWindows()