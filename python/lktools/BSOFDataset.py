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

    self.num_classes = 0
    '''
      结构：
        root -------- A --- a --- *.jpg
                |     | --- b --- *.png
                |
                |---- B --- a --- *.jpg
                      | --- b --- *.png
      结果：
        [
          (root/A/a/1.jpg, A), (root/A/b/2.png, A),
          (root/B/a/1.jpg, B), (root/B/b/2.png, B),
        ]
    '''
    self.files = []
    for clazz in os.listdir(path):
      clazz_path = os.path.join(path, clazz)
      if not os.path.isdir(clazz_path):
        continue
      self.num_classes += 1
      for site in os.listdir(clazz_path):
        site_path = os.path.join(clazz_path, site)
        if not os.path.isdir(site_path):
          continue
        for img in os.listdir(site_path):
          _, ext = os.path.splitext(img)
          if ext not in ('.jpg', '.jpeg'):
            continue
          img_path = os.path.join(site_path, img)
          self.files.append((img_path, clazz))

  def __getitem__(self, index):
    img, label = self.files[index]
    img        = cv2.imread(img)
    img        = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img        = cv2.resize(img, self.size)
    img        = torch.from_numpy(img)
    img        = Variable(img.float(), requires_grad=True)
    return img, label

  def __len__(self):
    return len(self.files)

if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    dataset = BSOFDataset(sys.argv[1])
    print(dataset.files)
