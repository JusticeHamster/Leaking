import cv2
import os

import torch
from torch.utils.data import Dataset, DataLoader

class BSOFDataset(Dataset):
  """
    custom pytorch Dataset
  """
  def __init__(self, path, size=(224, 224)):
    self.path = path
    self.size = size

    self.files = os.listdir(path)

  def __getitem__(self, index):
    img = self.files[index]
    img = cv2.imread(img)
    img = cv2.resize(img, self.size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = torch.from_numpy(img)
    return img

  def __len__(self):
    return len(self.files)

