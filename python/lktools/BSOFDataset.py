import cv2
import os

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

    self.type = os.path.split(path)[-1]
    self.files = os.listdir(path)

  def __getitem__(self, index):
    img = self.files[index]
    img = cv2.imread(img)
    img = cv2.resize(img, self.size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = torch.from_numpy(img)
    img = Variable(img, requires_grad=True)
    return img

  def __len__(self):
    return len(self.files)
