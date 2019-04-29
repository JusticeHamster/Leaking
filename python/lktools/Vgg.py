import torch.nn as nn
import math

'''
  参考：
  http://www.pianshen.com/article/2050135642/
'''
class VGG(nn.Module):

  def __init__(self, features, num_classes=0, init_weights=True, classify=True):
    super(VGG, self).__init__()
    self.features = features
    self.classify = classify
    self.classifier = nn.Sequential(
      nn.Linear(512 * 7 * 7, 4096),
      nn.ReLU(True),
      nn.Dropout(),
      nn.Linear(4096, 4096),
      nn.ReLU(True),
      nn.Dropout(),
      nn.Linear(4096, num_classes),
    )
    self.attributer = nn.Sequential(
      nn.Linear(512 * 7 * 7, 4096),
    )
    self.softmax = nn.Softmax(dim=1)
    if init_weights:
      self.__init_weights()

  def forward(self, x):
    x = self.features(x)
    x = x.view(x.size(0), -1)
    if self.classify:
      x = self.classifier(x)
    else:
      x = self.attributer(x)
    return x

  def __init_weights(self):
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
        m.weight.data.normal_(0, math.sqrt(2. / n))
        if m.bias is not None:
          m.bias.data.zero_()
      elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()
      elif isinstance(m, nn.Linear):
        m.weight.data.normal_(0, 0.01)
        m.bias.data.zero_()

def make(cfg, batch_norm=False):
  layers = []
  in_channels = 3
  for v in cfg:
    if v == 'M':
      layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
    else:
      layers.append(nn.Conv2d(in_channels, v, kernel_size=3, padding=1))
      if batch_norm:
        layers.append(nn.BatchNorm2d(v))
      layers.append(nn.ReLU(inplace=True))
      in_channels = v
  return nn.Sequential(*layers)

cfg = {
  '11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
  '13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
  '16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
  '19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
}

def vgg(version, **kwargs):
  """
    vgg 11/13/16/19 with or without bn
  """
  if len(version) < 2:
    return
  _cfg = cfg.get(version[:2])
  if _cfg is None:
    print(f'{version} not found.')
    return
  return VGG(
    make(_cfg, batch_norm='bn' in version),
    **kwargs
  )
