import cv2
import numpy as np
import os
import logging
from typing import Optional, Tuple, List
import json

logger = logging.getLogger(__name__)

class AIProcessor:
    """AI模型处理器"""
    
    def __init__(self):
        self.model = None
        self.model_type = None
        self.model_path = None
        self.config_path = None
        self.class_names = []
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        self.input_size = (416, 416)
        self.enabled = False
        
    def load_model(self, model_path: str, config_path: str = None, model_type: str = "yolo") -> bool:
        """加载AI模型
        
        Args:
            model_path: 模型文件路径
            config_path: 配置文件路径（可选）
            model_type: 模型类型 (yolo, tensorflow, onnx)
            
        Returns:
            bool: 是否加载成功
        """
        try:
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
                
            self.model_path = model_path
            self.config_path = config_path
            self.model_type = model_type.lower()
            
            if self.model_type == "yolo":
                return self._load_yolo_model()
            elif self.model_type == "tensorflow":
                return self._load_tensorflow_model()
            elif self.model_type == "onnx":
                return self._load_onnx_model()
            else:
                logger.error(f"Unsupported model type: {model_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def _load_yolo_model(self) -> bool:
        """加载YOLO模型"""
        try:
            # 使用OpenCV DNN模块加载YOLO模型
            if self.config_path and os.path.exists(self.config_path):
                self.model = cv2.dnn.readNetFromDarknet(self.config_path, self.model_path)
            else:
                # 尝试加载ONNX格式的YOLO模型
                self.model = cv2.dnn.readNetFromONNX(self.model_path)
            
            # 加载类别名称
            self._load_class_names()
            
            logger.info(f"YOLO model loaded successfully: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            return False
    
    def _load_tensorflow_model(self) -> bool:
        """加载TensorFlow模型"""
        try:
            self.model = cv2.dnn.readNetFromTensorflow(self.model_path, self.config_path)
            self._load_class_names()
            
            logger.info(f"TensorFlow model loaded successfully: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading TensorFlow model: {e}")
            return False
    
    def _load_onnx_model(self) -> bool:
        """加载ONNX模型"""
        try:
            self.model = cv2.dnn.readNetFromONNX(self.model_path)
            self._load_class_names()
            
            logger.info(f"ONNX model loaded successfully: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")
            return False
    
    def _load_class_names(self):
        """加载类别名称"""
        try:
            # 尝试从同目录下的classes.txt文件加载类别名称
            model_dir = os.path.dirname(self.model_path)
            classes_file = os.path.join(model_dir, "classes.txt")
            
            if os.path.exists(classes_file):
                with open(classes_file, 'r', encoding='utf-8') as f:
                    self.class_names = [line.strip() for line in f.readlines()]
            else:
                # 使用COCO数据集的默认类别名称
                self.class_names = [
                    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
                    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
                    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
                    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
                    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
                    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
                    'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
                    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
                    'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
                    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
                    'toothbrush'
                ]
                
            logger.info(f"Loaded {len(self.class_names)} class names")
            
        except Exception as e:
            logger.error(f"Error loading class names: {e}")
            self.class_names = []
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """处理单帧图像
        
        Args:
            frame: 输入图像帧
            
        Returns:
            np.ndarray: 处理后的图像帧
        """
        if not self.enabled or self.model is None:
            return frame
            
        try:
            # 获取图像尺寸
            height, width = frame.shape[:2]
            
            # 创建blob
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, self.input_size, swapRB=True, crop=False)
            
            # 设置输入
            self.model.setInput(blob)
            
            # 前向传播
            outputs = self.model.forward()
            
            # 处理检测结果
            detections = self._process_detections(outputs, width, height)
            
            # 在图像上绘制检测结果
            frame = self._draw_detections(frame, detections)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame
    
    def _process_detections(self, outputs: List[np.ndarray], width: int, height: int) -> List[dict]:
        """处理检测结果"""
        boxes = []
        confidences = []
        class_ids = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.confidence_threshold:
                    # 获取边界框坐标
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # 计算左上角坐标
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # 应用非最大抑制
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        
        detections = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                confidence = confidences[i]
                class_id = class_ids[i]
                
                detections.append({
                    'bbox': [x, y, w, h],
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': self.class_names[class_id] if class_id < len(self.class_names) else f'Class_{class_id}'
                })
        
        return detections
    
    def _draw_detections(self, frame: np.ndarray, detections: List[dict]) -> np.ndarray:
        """在图像上绘制检测结果"""
        for detection in detections:
            x, y, w, h = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # 绘制边界框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # 绘制标签背景
            cv2.rectangle(frame, (x, y - label_size[1] - 10), (x + label_size[0], y), (0, 255, 0), -1)
            
            # 绘制标签文本
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame
    
    def set_enabled(self, enabled: bool):
        """设置AI处理是否启用"""
        self.enabled = enabled
        logger.info(f"AI processing {'enabled' if enabled else 'disabled'}")
    
    def set_confidence_threshold(self, threshold: float):
        """设置置信度阈值"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.confidence_threshold}")
    
    def set_nms_threshold(self, threshold: float):
        """设置NMS阈值"""
        self.nms_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"NMS threshold set to {self.nms_threshold}")
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'model_path': self.model_path,
            'config_path': self.config_path,
            'model_type': self.model_type,
            'enabled': self.enabled,
            'confidence_threshold': self.confidence_threshold,
            'nms_threshold': self.nms_threshold,
            'class_count': len(self.class_names),
            'loaded': self.model is not None
        }

# 全局AI处理器实例
ai_processor = AIProcessor()