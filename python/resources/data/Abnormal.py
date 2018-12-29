class Abnormal:
  """
  表示异常的枚举类型
  """
  '''液体异常'''
  ACID_SOLUTION     = '酸碱溶液'
  WATER             = '水'
  EDIBLE_OIL        = '食用油'
  MOTOR_OIL         = '机油'
  COAL_WATER_SLURRY = '水煤浆'
  '''气体异常'''
  WATER_VAPOR       = '水蒸气'
  SMOKE             = '烟'
  '''明火异常'''
  OPEN_FIRE         = '明火'
  ELECTRIC_SPARK    = '电火花'
  '''粉尘异常'''
  LEAKAGE_DUST      = '漏料粉尘'
  FUNNEL_COAL_ASH   = '漏斗煤灰'
  '''未知'''
  UNKNOWN           = 'unknown'
  '''反向字典，及获取的代理方法'''
  ABNORMAL = {
    # 液体异常
    'ACID_SOLUTION'     : ACID_SOLUTION,
    'WATER'             : WATER,
    'EDIBLE_OIL'        : EDIBLE_OIL,
    'MOTOR_OIL'         : MOTOR_OIL,
    'COAL_WATER_SLURRY' : COAL_WATER_SLURRY,
    # 气体异常
    'WATER_VAPOR'       : WATER_VAPOR,
    'SMOKE'             : SMOKE,
    # 明火异常
    'OPEN_FIRE'         : OPEN_FIRE,
    'ELECTRIC_SPARK'    : ELECTRIC_SPARK,
    # 粉尘异常
    'LEAKAGE_DUST'      : LEAKAGE_DUST,
    'FUNNEL_COAL_ASH'   : FUNNEL_COAL_ASH,
  }

  @staticmethod
  def abnormal(name):
    return Abnormal.ABNORMAL.get(name, Abnormal.UNKNOWN)

  @staticmethod
  def names():
    return list(Abnormal.ABNORMAL.keys())

  @staticmethod
  def classes():
    return list(Abnormal.ABNORMAL.values())

  """
  不同分类对应的颜色
  """
  COLOR = {
    # 液体异常
    ACID_SOLUTION     : 'EE00EE',
    WATER             : 'BBFFFF',
    EDIBLE_OIL        : 'EEC900',
    MOTOR_OIL         : '000000',
    COAL_WATER_SLURRY : '696969',
    # 气体异常
    WATER_VAPOR       : 'FCFCFC',
    SMOKE             : 'D9D9D9',
    # 明火异常
    OPEN_FIRE         : 'EE0000',
    ELECTRIC_SPARK    : 'EEEE00',
    # 粉尘异常
    LEAKAGE_DUST      : '00FFFF',
    FUNNEL_COAL_ASH   : '000080',
    # unknown
    UNKNOWN           : '00FF00',
  }

  @staticmethod
  def color(clazz):
    return Abnormal.COLOR.get(clazz, Abnormal.COLOR[Abnormal.UNKNOWN])
