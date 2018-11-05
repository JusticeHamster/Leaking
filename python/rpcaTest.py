# import
import numpy as np
import cv2
import RPCA
# def
full_path = '/Users/wangyuxin/Movies/data'
videos = ['fire.mov']#, 'water.mp4']
# pre
def videos_path(videos):
  return map(
    lambda n: '{path}/{name}'.format(
      path=full_path,
      name=n
    ),
    videos
  )
# func
def run(path):
  m, n = 192, 108
  # init
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
    frame = cv2.resize(frame, (m, n), interpolation=cv2.INTER_LINEAR)
    # gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.array(gray)
    gray = gray.reshape(-1, 1)
    # stack
    if data is None:
      data = gray
    else:
      data = np.hstack((data, gray))
  capture.release()
  # cal
  print('run')
  h = RPCA.rpcaADMM(data)
  print('end {path}'.format(path=path))
  # show
  count = 0
  while count < nframes:
    X1 = h['X1_admm']
    X2 = h['X2_admm']
    X3 = h['X3_admm']
    #
    cv2.imshow('frame', X1[:, count].reshape((m, n)))
    #
    count += 1
    print(count/nframes)
    if cv2.waitKey(100) & 0xFF == ord('q'):
      break
  # free
  cv2.destroyAllWindows()
# run
if __name__ == '__main__':
  for video in videos_path(videos):
    run(video)