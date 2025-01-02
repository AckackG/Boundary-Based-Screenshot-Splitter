from PIL import Image
from dataclasses import dataclass
from typing import Tuple, Optional
import cv2
import numpy as np


@dataclass
class ImageInfo:
    width: int
    height: int
    preview_width: int
    preview_height: int
    scale_ratio: float


class ImageProcessor:
    PREVIEW_HEIGHT = 4000  # 预览时截取的高度
    DISPLAY_WIDTH = 800  # 显示最大宽度
    DISPLAY_HEIGHT = 900  # 显示最大高度

    def __init__(self):
        self.original_image: Optional[Image.Image] = None
        self.preview_image: Optional[Image.Image] = None
        self.image_info: Optional[ImageInfo] = None

    def load_image(self, file_path: str) -> Tuple[Image.Image, ImageInfo]:
        """加载并处理图片"""
        # 加载原始图片
        self.original_image = Image.open(file_path)

        # 截取顶部预览部分
        self.preview_image = self.original_image.crop(
            (
                0,
                0,
                self.original_image.width,
                min(self.PREVIEW_HEIGHT, self.original_image.height),
            )
        )

        # 计算显示尺寸
        preview_width = self.preview_image.width
        preview_height = self.preview_image.height
        scale_ratio = 1.0

        # 计算缩放比例
        width_ratio = (
            self.DISPLAY_WIDTH / preview_width
            if preview_width > self.DISPLAY_WIDTH
            else 1.0
        )
        height_ratio = (
            self.DISPLAY_HEIGHT / preview_height
            if preview_height > self.DISPLAY_HEIGHT
            else 1.0
        )

        # 使用较小的缩放比例，保持宽高比
        if width_ratio < 1.0 or height_ratio < 1.0:
            scale_ratio = min(width_ratio, height_ratio)
            preview_width = int(preview_width * scale_ratio)
            preview_height = int(preview_height * scale_ratio)
            self.preview_image = self.preview_image.resize(
                (preview_width, preview_height), Image.Resampling.LANCZOS
            )

        # 创建图片信息对象
        self.image_info = ImageInfo(
            width=self.original_image.width,
            height=self.original_image.height,
            preview_width=preview_width,
            preview_height=preview_height,
            scale_ratio=scale_ratio,
        )

        return self.preview_image, self.image_info

    def get_real_coordinates(self, preview_coord: int) -> int:
        """将预览图上的坐标转换为原图坐标"""
        if self.image_info:
            return int(preview_coord / self.image_info.scale_ratio)
        return preview_coord

    def find_split_points(self, start_y: int, end_y: int) -> list[int]:
        """
        根据用户选择的特征区域，在图片中寻找所有可能的分割点

        Args:
            start_y: 特征区域的起始y坐标
            end_y: 特征区域的结束y坐标

        Returns:
            分割点y坐标列表
        """
        # 将PIL图像转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(self.original_image), cv2.COLOR_RGB2BGR)

        # 提取特征模板
        template_height = end_y - start_y
        template = cv_image[start_y:end_y, :, :]

        # 执行模板匹配
        result = cv2.matchTemplate(cv_image, template, cv2.TM_CCOEFF_NORMED)

        # 设置阈值，找到所有匹配点
        threshold = 0.8
        locations = np.where(result >= threshold)
        split_points = locations[0].tolist()

        # 对分割点进行过滤和排序
        split_points = sorted(set(split_points))  # 去重并排序

        return split_points
