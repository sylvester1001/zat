"""
图像识别工具
使用 PaddleOCR 进行文字识别，OpenCV 进行模板匹配
"""
import os
import logging
from typing import Optional, Tuple, List
import numpy as np
import cv2

# 跳过模型源检查，加快启动速度
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"

logger = logging.getLogger("zat.image")

# 模板图片目录
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

# 延迟加载 OCR（因为初始化较慢）
_ocr_instance = None


def get_ocr():
    """获取 OCR 实例（延迟加载）"""
    global _ocr_instance
    if _ocr_instance is None:
        logger.info("正在初始化 PaddleOCR（首次运行需要下载模型，请稍候）...")
        from paddleocr import PaddleOCR
        _ocr_instance = PaddleOCR(
            lang='ch',            # 中文
            device='cpu',         # 使用 CPU
        )
        logger.info("PaddleOCR 初始化完成")
    return _ocr_instance


class ImageMatcher:
    """图像匹配器"""
    
    def __init__(self):
        self.templates: dict[str, np.ndarray] = {}
        self._load_templates()
    
    def _load_templates(self, directory: str = None, prefix: str = ""):
        """
        递归加载所有模板图片
        
        子目录中的模板会以 "目录名/文件名" 的格式命名
        例如: daily_dungeon/world_tree
        """
        if directory is None:
            directory = TEMPLATES_DIR
            
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"创建模板目录: {directory}")
            return
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            # 如果是目录，递归加载
            if os.path.isdir(filepath):
                subdir_prefix = f"{prefix}{filename}/" if prefix else f"{filename}/"
                self._load_templates(filepath, subdir_prefix)
                continue
            
            # 加载图片文件
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(filename)[0]
                template_name = f"{prefix}{name}" if prefix else name
                img = cv2.imread(filepath)
                if img is not None:
                    self.templates[template_name] = img
                    logger.info(f"已加载模板: {template_name}")
    
    def match_template(
        self,
        screen: np.ndarray,
        template_name: str,
        threshold: float = 0.8,
    ) -> Optional[Tuple[int, int, float]]:
        """模板匹配"""
        if template_name not in self.templates:
            logger.debug(f"模板不存在: {template_name}")
            return None
        
        template = self.templates[template_name]
        th, tw = template.shape[:2]
        sh, sw = screen.shape[:2]
        
        # 检查模板尺寸是否小于截图
        if th > sh or tw > sw:
            logger.warning(f"模板 {template_name} ({tw}x{th}) 大于截图 ({sw}x{sh})，跳过匹配")
            return None
        
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            center_x = max_loc[0] + tw // 2
            center_y = max_loc[1] + th // 2
            logger.debug(f"模板匹配成功: {template_name}, 置信度: {max_val:.3f}, 位置: ({center_x}, {center_y})")
            return (center_x, center_y, max_val)
        return None
    
    def ocr_find_text(
        self,
        screen: np.ndarray,
        target_text: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        confidence_threshold: float = 0.5
    ) -> Optional[Tuple[int, int, float]]:
        """
        使用 OCR 查找指定文字的位置
        
        Args:
            screen: 屏幕截图 (BGR)
            target_text: 要查找的文字（支持部分匹配）
            region: 搜索区域 (x, y, w, h)，可选，限制搜索范围提高速度
            confidence_threshold: 置信度阈值
        
        Returns:
            找到返回 (center_x, center_y, confidence)，否则返回 None
        """
        ocr = get_ocr()
        
        # 如果指定了区域，裁剪图片
        offset_x, offset_y = 0, 0
        if region:
            x, y, w, h = region
            screen = screen[y:y+h, x:x+w]
            offset_x, offset_y = x, y
        
        # 执行 OCR (PaddleOCR 3.x 使用 predict 方法)
        result = ocr.predict(screen)
        
        if not result:
            logger.debug("OCR 返回空结果")
            return None
        
        # PaddleOCR 3.x 返回格式: [{'rec_texts': [...], 'rec_scores': [...], 'rec_polys': [...]}]
        for item in result:
            texts = item.get('rec_texts', [])
            scores = item.get('rec_scores', [])
            polys = item.get('rec_polys', [])
            
            logger.debug(f"OCR 识别到 {len(texts)} 个文字: {texts[:5]}...")  # 只显示前5个
            
            for i, text in enumerate(texts):
                confidence = scores[i] if i < len(scores) else 0
                
                # 检查是否包含目标文字
                if target_text in text and confidence >= confidence_threshold:
                    # 计算文字框中心点
                    if i < len(polys) and len(polys[i]) >= 4:
                        poly = polys[i]
                        x_coords = [p[0] for p in poly]
                        y_coords = [p[1] for p in poly]
                        center_x = int(sum(x_coords) / len(x_coords)) + offset_x
                        center_y = int(sum(y_coords) / len(y_coords)) + offset_y
                    else:
                        # 如果没有坐标，返回图片中心
                        h, w = screen.shape[:2]
                        center_x = w // 2 + offset_x
                        center_y = h // 2 + offset_y
                    
                    logger.info(f"OCR 找到文字: '{text}', 置信度: {confidence:.3f}, 位置: ({center_x}, {center_y})")
                    return (center_x, center_y, confidence)
        
        return None
    
    def ocr_get_all_text(
        self,
        screen: np.ndarray,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> List[Tuple[str, float, Tuple[int, int]]]:
        """
        获取屏幕上所有识别到的文字
        
        Returns:
            列表 [(text, confidence, (center_x, center_y)), ...]
        """
        ocr = get_ocr()
        
        offset_x, offset_y = 0, 0
        if region:
            x, y, w, h = region
            screen = screen[y:y+h, x:x+w]
            offset_x, offset_y = x, y
        
        result = ocr.predict(screen)
        
        texts_list = []
        if result:
            for item in result:
                texts = item.get('rec_texts', [])
                scores = item.get('rec_scores', [])
                polys = item.get('rec_polys', [])
                
                for i, text in enumerate(texts):
                    confidence = scores[i] if i < len(scores) else 0
                    
                    if i < len(polys) and len(polys[i]) >= 4:
                        poly = polys[i]
                        x_coords = [p[0] for p in poly]
                        y_coords = [p[1] for p in poly]
                        center_x = int(sum(x_coords) / len(x_coords)) + offset_x
                        center_y = int(sum(y_coords) / len(y_coords)) + offset_y
                    else:
                        center_x, center_y = 0, 0
                    
                    texts_list.append((text, confidence, (center_x, center_y)))
        
        return texts_list


# 全局实例
image_matcher = ImageMatcher()
