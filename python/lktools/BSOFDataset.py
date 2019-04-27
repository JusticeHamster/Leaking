import cv2
import os
import xpinyin
pinyin = xpinyin.Pinyin()

import torch
from torch.utils.data import Dataset, DataLoader

class BSOFDataset(Dataset):
  """
    custom pytorch Dataset

    path不为空
  """
  def __init__(
    self, path, size=(224, 224),
    exts=('.jpg', '.jpeg', '.png'),
    classes=None
  ):
    if path[-1] in ('\\', '/'):
      path = path[:-1]

    self.path = path
    self.size = size
    self.exts = exts

    '''
      结构：         class  site  images
        root -------- A --- a --- *.jpg
                |     | --- b --- *.png
                |
                |---- B --- a --- *.jpg
                      | --- b --- *.png
      结果：（相对路径）
        [
          (root/A/a/1.jpg, A), (root/A/b/2.png, A),
          (root/B/a/1.jpg, B), (root/B/b/2.png, B),
        ]
    '''
    self.files    = []
    if classes is None:
      self.num_classes = -1
      self.classes     = []
    else:
      self.num_classes = len(classes)
      self.classes     = classes
    for clazz in os.listdir(path):
      clazz_path = os.path.join(path, clazz)
      if not os.path.isdir(clazz_path):
        continue
      if classes is None:
        self.classes.append(clazz)
        self.num_classes += 1
      for site in os.listdir(clazz_path):
        site_path = os.path.join(clazz_path, site)
        if not os.path.isdir(site_path):
          continue
        for img in os.listdir(site_path):
          _, ext = os.path.splitext(img)
          if ext not in self.exts:
            continue
          img_path = os.path.join(site_path, img)
          if classes is None:
            label = self.num_classes
          else:
            label = classes.index(clazz)
          self.files.append((img_path, label))
    if classes is None:
      self.num_classes += 1

  def __getitem__(self, index):
    img, label = self.raw_img(index)
    img        = BSOFDataset.load_img(img, self.size)
    return img, label

  def __len__(self):
    return len(self.files)

  def raw_img(self, index):
    img, label = self.files[index]
    # PS: 最好保证路径中没有中文（可能导致opencv Assertion failed (scn == 3 || scn == 4)）
    img        = cv2.imread(img)
    return img, label

  @staticmethod
  def load_img(img, size):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, size)
    img = img.transpose((2, 0, 1))
    img = torch.from_numpy(img)
    img = img.float()
    return img

if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    dataset = BSOFDataset(sys.argv[1])
    print(dataset.files)
