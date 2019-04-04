import cv2
import os
import xpinyin
pinyin = xpinyin.Pinyin()

import torch
from torch.utils.data import Dataset, DataLoader
from torch.autograd import Variable

class BSOFDataset(Dataset):
  """
    custom pytorch Dataset

    path不为空
  """
  def __init__(self, path, size=(224, 224)):
    if path[-1] == '/':
      path = path[:-1]

    self.path = path
    self.size = size

    self.files = [
      (name, _dir) for name, dirs in map(
      lambda d: (
        pinyin.get_pinyin(d, '_'),
        os.listdir(f'{path}/{d}')
      ),
      filter(
        lambda p: os.path.isdir(f'{path}/{p}'), 
        os.listdir(path)
      )
    ) for _dir in dirs
    ]

  def __getitem__(self, index):
    img, label = self.files[index]
    img        = cv2.imread(img)
    img        = cv2.resize(img, self.size)
    img        = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img        = torch.from_numpy(img)
    img        = Variable(img, requires_grad=True)
    return img, label

  def __len__(self):
    return len(self.files)

if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    BSOFDataset(sys.argv[1])
