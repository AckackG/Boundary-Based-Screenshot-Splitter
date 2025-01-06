import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, List
from loguru import logger
from src.pdf_generator import PDFGenerator  # 添加导入


class ImageSplitter:
    def __init__(
        self,
        image_path: str,
        width_range: Tuple[int, int],
        feature_range: Tuple[int, int],
        progress_callback=None,
        log_callback=None,
    ):
        """
        初始化图片分割器

        Args:
            image_path: 原始图片路径
            width_range: 宽度裁剪范围 (start_x, end_x)
            feature_range: 特征区域范围 (start_y, end_y)
            progress_callback: 进度回调函数
            log_callback: 日志回调函数
        """
        logger.debug(f"初始化 ImageSplitter: {image_path}")
        self.image_path = image_path
        self.width_range = width_range
        self.feature_range = feature_range
        self.progress_callback = progress_callback
        self.log_callback = log_callback

        # 分离图片和PDF输出目录
        self.output_dir = Path("output/images")
        self.pdf_dir = Path("output/pdf")

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        # 获取源文件名（不含扩展名）
        self.source_name = Path(image_path).stem

        self.template_height = 0  # 初始化模板高度

    def _log(self, message: str):
        """输出日志"""
        if self.log_callback:
            self.log_callback(message)
        logger.info(message)

    def process(self):
        """执行图片处理流程"""
        logger.info("开始处理图片...")
        self._log("开始处理图片...")

        # 1. 裁剪宽度
        self._log("正在裁剪宽度...")
        cropped_image = self._crop_width()

        # 2. 提取特征模板
        self._log("正在提取特征模板...")
        template = self._extract_template(cropped_image)
        self.template_height = template.shape[0]  # 保存模板高度

        # 3. 寻找分割点
        self._log("正在寻找分割点...")
        split_points = self._find_split_points(cropped_image, template)

        # 4. 根据分割点切分图片并保存
        self._log(f"开始保存分割后的图片...")
        self._split_and_save(cropped_image, split_points)
        self._log("图片分割完成！")

        # 生成PDF
        self._log("正在生成PDF...")
        pdf_gen = PDFGenerator(self.output_dir, self.pdf_dir)
        pdf_path = pdf_gen.generate()
        self._log("PDF生成完成！")

        return pdf_path  # 返回生成的PDF路径

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
        threshold = 0.9
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
        total_points = len(split_points) - 1

        for i in range(total_points):
            start_y = split_points[i]
            end_y = split_points[i + 1]

            # 裁剪图片
            cropped_image_with_template = image[start_y:end_y]

            # 去除顶部的模板部分
            if i > 0:  # 第一张图片不需要去除顶部
                cropped_image = cropped_image_with_template[self.template_height :]
            else:
                cropped_image = cropped_image_with_template

            # 生成输出文件名
            output_path = self.output_dir / f"{self.source_name}_{i+1}.png"

            # 保存图片
            cv2.imwrite(str(output_path), cropped_image)

            # 更新进度和日志
            if self.progress_callback:
                progress = (i + 1) / total_points  # 进度值在 0 到 1 之间
                self.progress_callback(progress)
            self._log(f"已保存: {output_path}")
