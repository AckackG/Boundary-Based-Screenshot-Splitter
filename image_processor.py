from PIL import Image
from dataclasses import dataclass
from typing import Tuple, Optional


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

    def get_real_coordinates(self, preview_x: int) -> int:
        """将预览图上的坐标转换为原图坐标"""
        if self.image_info:
            return int(preview_x / self.image_info.scale_ratio)
        return preview_x
