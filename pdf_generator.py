from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from loguru import logger


class PDFGenerator:
    def __init__(self, image_dir: Path, pdf_dir: Path):
        """
        初始化PDF生成器

        Args:
            image_dir: 图片所在目录
            pdf_dir: PDF输出目录
        """
        self.image_dir = image_dir
        self.pdf_dir = pdf_dir
        self.image_files = sorted(
            list(image_dir.glob("*.png")), key=lambda x: int(x.stem.split("_")[-1])
        )

    def generate(self, output_path: str = None) -> Path:
        """
        生成PDF文件

        Args:
            output_path: PDF输出路径，默认为PDF目录下的同名PDF

        Returns:
            生成的PDF文件路径
        """
        if not self.image_files:
            logger.warning("没有找到图片文件")
            return None

        if output_path is None:
            # 使用第一张图片的名称（去掉序号）作为PDF名称
            base_name = "_".join(self.image_files[0].stem.split("_")[:-1])
            output_path = self.pdf_dir / f"{base_name}.pdf"

        logger.info(f"开始生成PDF: {output_path}")

        # 创建PDF文档
        c = canvas.Canvas(str(output_path), pagesize=A4)
        page_width, page_height = A4

        for img_path in self.image_files:
            # 打开图片
            img = Image.open(img_path)

            # 计算缩放比例，使图片适应页面宽度
            scale = page_width / img.width
            img_width = page_width
            img_height = img.height * scale

            # 如果图片高度超过页面高度，进行等比例缩小
            if img_height > page_height:
                scale = page_height / img_height
                img_width *= scale
                img_height = page_height

            # 计算居中位置
            x = (page_width - img_width) / 2
            y = (page_height - img_height) / 2

            # 将图片添加到PDF
            c.drawImage(
                str(img_path),
                x,
                y,
                width=img_width,
                height=img_height,
                preserveAspectRatio=True,
            )

            # 添加新页面
            c.showPage()

        # 保存PDF
        c.save()
        logger.success(f"PDF生成完成: {output_path}")

        return output_path
