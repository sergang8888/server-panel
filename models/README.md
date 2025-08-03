# AI模型文件夹

这个文件夹用于存放AI模型文件，支持以下格式：

## 支持的模型格式

- **YOLO模型**: `.weights` 文件（需要配合 `.cfg` 配置文件）
- **ONNX模型**: `.onnx` 文件
- **TensorFlow模型**: `.pb` 文件（需要配合 `.pbtxt` 配置文件）
- **PyTorch模型**: `.pt` 文件

## 模型文件放置说明

1. 将模型文件直接放置在此文件夹中
2. 如果有配置文件（如 `.cfg` 或 `.pbtxt`），请一同放置
3. 类别名称文件 `classes.txt` 已提供（COCO数据集80个类别）
4. 如果使用自定义数据集，请替换 `classes.txt` 文件

## 推荐的预训练模型

### YOLO模型
- YOLOv4: `yolov4.weights` + `yolov4.cfg`
- YOLOv5: `yolov5s.onnx`
- YOLOv8: `yolov8n.onnx`

### 下载地址
- YOLO官方: https://github.com/AlexeyAB/darknet
- Ultralytics: https://github.com/ultralytics/yolov5
- ONNX模型库: https://github.com/onnx/models

## 使用步骤

1. 下载并放置模型文件到此文件夹
2. 在Web界面的"AI功能配置"中选择模型
3. 选择正确的模型类型（YOLO/TensorFlow/ONNX）
4. 点击"加载模型"按钮
5. 启用AI检测开关
6. 调整置信度和NMS阈值（可选）
7. 保存AI配置

## 注意事项

- 模型文件较大，首次加载可能需要一些时间
- 确保有足够的内存来加载模型
- AI处理会增加CPU使用率，可能影响视频流畅度
- 建议使用GPU加速（需要安装CUDA版本的OpenCV）