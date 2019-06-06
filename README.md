# Leaking

### 编译环境

1. python3.7
2. opencv
3. pytorch
4. json5
5. kivy



### 项目运行

setting.json: 配置模型参数，内容如下

``` 
// json5
{
  "path"              : "../video",       // 视频路径
  "class_info_file"   : "class_info.json",// 视频所属标签，用于分类
  "resource_path"     : "resources",      // 资源路径
  "videos"            : ["*"],            // 视频列表，"*"为通配符
  "delay"             : 10,               // 视频播放延迟，用于cv2.waitKey第一个参数
  "height"            : 480,              // 视频高度限定，宽度会自动计算
  "frame_range"       : [0, -1],          // 取[a, b]帧，b可以是负数，表示倒数第abs(b)帧
  "img_path"          : "images.tmp",     // 图片存取路径
  "video_path"        : "videos.tmp",     // 视频存取路径
  "svm_model_path"    : "svm.model",      // svm Model路径
  "vgg_model_path"    : "vgg.model",      // vgg Model路径
  "xgboost_model_path": "xgb.model",      // xgboost Model路径
  "file_output"       : false,            // 是否输出到文件夹
  "interval"          : 10,               // 用前N帧图片作为修正的标准
  "fps"               : 10,               // 保存视频帧数
  "time_debug"        : false,            // 是否打印每个函数耗时
  "limit_size"        : 10,               // 光流法的参数
  "compression_ratio" : 1.0,              // 光流法的压缩率
  "linux"             : false,            // 是不是linux，linux不会执行显示相关的函数
  "sift"              : true,             // 是否开启sift对齐
  "OF"                : true,             // 是否开启光流法
  "debug_level"       : "info",           // 等级debug -> info -> warn -> error -> critical，会打印该级别级以上的Logger信息
  "app_fps"           : 60,               // app刷新率
  "varThreshold"      : 121.0,            // 高斯混合模型的阈值，决定模型是否灵敏，越小越敏感
  "detectShadows"     : false,            // 高斯混合模型的阴影识别，True开启后影响速度
  "language"          : "Chinese",        // 所使用的语言
  "Retina"            : false,            // 是否是Retina高清屏幕，它的像素数量不一样，会影响显示的计算
  "debug_per_frame"   : false,            // model逐帧调试，回车进入下一帧
  "max_iter"          : -1,               // SVC的最大迭代次数
  "num_epochs"        : 100,              // 神经网络训练轮数
  "learning_rate"     : 0.01,             // 神经网络学习率
  "momentum"          : 0.9,              // 神经网络 SGD momentum
  "batch_size"        : 64,               // 神经网络 batch_size
  "step_size"         : 10,               // StepLR scheduler step_size
  "gamma"             : 0.5,              // StepLR scheduler gamma
  "num_workers"       : 0,                // DataLoader 线程数
  "data"              : {
    "train" : "?",
    "test"  : "?",
  },                                      // 神经网络数据集位置
  "cuda"              : true,             // 如果有cuda，就自动开启cuda
  "vgg"               : "19bn",           // 选择vgg网络的类型
  "model_t"           : "xgboost",        // 选择model类型
  "init_box_scale"    : [
    [0.0625, 0.25], [0.9375, 0.725]
  ],                                      // 框box的初始大小
  "generation_t"      : "image",          // 通过什么方式训练模型
  "nthread"           : 4,                // xgboost 线程数
  "num_round"         : 10,               // xgboost 训练轮数
}

```



BSOFApp.py: 包含了交互界面的系统，执行

```
python BSOFApp.py
```



BSOFModel.py: 是BSOFApp.py的后端，有以下功能：

1. DEBUG模式：

   ```
   python BSOFModel.py debug
   ```

2. SHOW模式：

   ```
   python BSOFModel.py show
   ```

3. MODEL模式：训练vgg、svm、xgboost模型

   ```
   python BSOFModel.py model
   ```

   

具体的参数选择在setting.model中修改