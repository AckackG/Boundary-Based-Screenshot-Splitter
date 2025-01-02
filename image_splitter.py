import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, List


class ImageSplitter:
    def __init__(
        self,
        image_path: str,
        width_range: Tuple[int, int],
        feature_range: Tuple[int, int],
    ):
        """
        初始化图片分割器

        Args:
            image_path: 原始图片路径
            width_range: 宽度裁剪范围 (start_x, end_x)
            feature_range: 特征区域范围 (start_y, end_y)
        """
        self.image_path = image_path
        self.width_range = width_range
        self.feature_range = feature_range
        self.output_dir = Path("OUTPUT")

        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True)

        # 获取源文件名（不含扩展名）
        self.source_name = Path(image_path).stem

    def process(self):
        """执行图片处理流程"""
        # 1. 裁剪宽度
        cropped_image = self._crop_width()

        # 2. 提取特征模板
        template = self._extract_template(cropped_image)

        # 3. 寻找分割点
        split_points = self._find_split_points(cropped_image, template)

        # 4. 根据分割点切分图片并保存
        self._split_and_save(cropped_image, split_points)

    def _crop_width(self) -> np.ndarray:
        """裁剪图片宽度"""
        # 读取原始图片
        image = cv2.imread(self.image_path)
        start_x, end_x = self.width_range

        # 裁剪指定宽度
        return image[:, start_x:end_x]

    def _extract_template(self, image: np.ndarray) -> np.ndarray:
        """提取特征模板"""
        start_y, end_y = self.feature_range
        return image[start_y:end_y, :]

    def _find_split_points(self, image: np.ndarray, template: np.ndarray) -> List[int]:
        """
        使用模板匹配找到所有分割点
        """
        # 执行模板匹配
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

        # 设置阈值，找到所有匹配点
        threshold = 0.8
        locations = np.where(result >= threshold)[0]

        # 过滤和处理分割点
        split_points = []
        min_distance = template.shape[0] // 2  # 最小间距

        # 添加起始点
        split_points.append(0)

        # 过滤太近的点
        for loc in locations:
            if not split_points or loc - split_points[-1] >= min_distance:
                split_points.append(loc)

        # 添加结束点
        if split_points[-1] < image.shape[0] - template.shape[0]:
            split_points.append(image.shape[0])

        return split_points

    def _split_and_save(self, image: np.ndarray, split_points: List[int]):
        """根据分割点切分图片并保存"""
        for i in range(len(split_points) - 1):
            start_y = split_points[i]
            end_y = split_points[i + 1]

            # 裁剪图片
            cropped_image = image[start_y:end_y]

            # 生成输出文件名
            output_path = self.output_dir / f"{self.source_name}_{i+1}.png"

            # 保存图片
            cv2.imwrite(str(output_path), cropped_image)
            print(f"已保存: {output_path}")
