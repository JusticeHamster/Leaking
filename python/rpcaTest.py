# import
import numpy as np
import cv2
from os.path import abspath

import RPCA
# def
videos = ['火花.mov', '流水.mp4']
# pre
def videos_path(videos):
  return map(
    lambda n: '{path}/{name}'.format(
      path=abspath('../video'),
      name=n
    ),
    videos
  )
# func
def run(path):
  # init
  capture = cv2.VideoCapture(path)
  data = np.array([])
  # run
  print('start')
  while capture.isOpened():
    _, frame = capture.read()
    # gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.array(gray)
    #
    cv2.imshow('frame', gray)
  capture.release()
  # cal
  # RPCA.rpcaADMM(data)
  # free
  cv2.destroyAllWindows()
# run
if __name__ == '__main__':
  for video in videos_path(videos):
    run(video)