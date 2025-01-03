import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk
from image_processor import ImageProcessor
from image_splitter import ImageSplitter
from loguru import logger
from pathlib import Path

# 配置日志
log_path = Path("logs")
log_path.mkdir(exist_ok=True)
logger.add(
    log_path / "app_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    encoding="utf-8",
)


class ImageCropper:
    def __init__(self, root):
        logger.info("启动图片裁剪工具")
        self.root = root
        self.root.title("图片裁剪工具")

        # 初始化图像处理器
        self.processor = ImageProcessor()

        # 初始化变量
        self.photo = None
        self.canvas = None
        self.start_x = None
        self.rect = None
        self.selection = None
        self.vertical_selection = None  # 垂直分割选择

        # 创建按钮框架
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="top", fill="x", padx=5, pady=5)

        # 创建界面
        self.create_widgets()

        # 初始化按钮状态
        self.update_button_states("init")

    def create_widgets(self):
        # 创建主框架，用于左右布局
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # 创建左侧框架
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left", expand=True, fill="both")

        # 创建右侧框架
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side="right", fill="y", padx=(5, 0))

        # 创建按钮框架（放在左侧框架顶部）
        self.button_frame = tk.Frame(self.left_frame)
        self.button_frame.pack(side="top", fill="x", pady=(0, 5))

        # 创建所有按钮
        self.open_button = tk.Button(
            self.button_frame, text="打开图片", command=self.open_image
        )
        self.open_button.pack(side="left", padx=5)

        self.crop_button = tk.Button(
            self.button_frame, text="裁剪宽度", command=self.crop_width
        )
        self.crop_button.pack(side="left", padx=5)

        self.split_button = tk.Button(
            self.button_frame, text="选择分割", command=self.prepare_split
        )
        self.split_button.pack(side="left", padx=5)

        self.process_button = tk.Button(
            self.button_frame, text="处理图片", command=self.process_image
        )
        self.process_button.pack(side="left", padx=5)

        # 创建画布（放在左侧框架）
        self.canvas = tk.Canvas(self.left_frame)
        self.canvas.pack(expand=True, fill="both")

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # 添加日志文本框（放在右侧框架）
        # 添加标题标签
        tk.Label(self.right_frame, text="处理日志").pack(side="top", pady=(0, 5))

        self.log_text = tk.Text(self.right_frame, width=30, height=20)
        self.log_text.pack(side="left", fill="y")

        # 添加滚动条
        scrollbar = tk.Scrollbar(self.right_frame)
        scrollbar.pack(side="right", fill="y")

        # 关联滚动条和文本框
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # 添加进度条（放在主窗口底部）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(side="bottom", fill="x", padx=5, pady=5)
        self.progress_bar.pack_forget()  # 默认隐藏

    def update_button_states(self, state):
        """更新按钮状态"""
        states = {
            "init": {
                "open": "normal",
                "crop": "disabled",
                "split": "disabled",
                "process": "disabled",
            },
            "opened": {
                "open": "normal",
                "crop": "normal",
                "split": "disabled",
                "process": "disabled",
            },
            "cropped": {
                "open": "normal",
                "crop": "disabled",
                "split": "normal",
                "process": "disabled",
            },
            "split": {
                "open": "normal",
                "crop": "disabled",
                "split": "disabled",
                "process": "normal",
            },
        }

        self.open_button.config(state=states[state]["open"])
        self.crop_button.config(state=states[state]["crop"])
        self.split_button.config(state=states[state]["split"])
        self.process_button.config(state=states[state]["process"])

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )

        if file_path:
            logger.debug(f"选择文件：{file_path}")
            self.log_message(f"正在加载图片：{file_path}")
            # 处理图片
            preview_image, image_info = self.processor.load_image(file_path)
            self.log_message(
                f"图片加载完成，尺寸：{image_info.width}x{image_info.height}"
            )

            # 显示图片
            self.photo = ImageTk.PhotoImage(preview_image)
            self.canvas.config(
                width=image_info.preview_width, height=image_info.preview_height
            )
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

            # 重置选择状态
            self.selection = None
            self.vertical_selection = None
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = None

            # 更新按钮状态
            self.update_button_states("opened")

    def crop_width(self):
        if self.processor.original_image:
            if self.selection:
                # 使用用户选择的宽度
                start_x, end_x = self.selection
            else:
                # 使用图片的默认宽度
                start_x, end_x = 0, self.processor.original_image.width

            # 清除选择框
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = None

            print(f"裁剪后的宽度：{end_x - start_x}")

            # 更新按钮状态
            self.update_button_states("cropped")

    def prepare_split(self):
        """准备分割区域选择"""
        if not self.vertical_selection:
            messagebox.showwarning("警告", "必须选择特征区域")
            return

        # 只更新按钮状态，不进行计算
        self.update_button_states("split")

    def process_image(self):
        """处理图片"""
        if not all([self.selection, self.vertical_selection]):
            logger.warning("未选择裁剪宽度或特征区域")
            messagebox.showwarning("警告", "请先选择裁剪宽度和特征区域")
            return

        try:
            logger.info("开始处理图片")
            # 显示进度条
            self.progress_bar.pack(side="bottom", fill="x", padx=5, pady=5)
            self.progress_var.set(0)

            # 获取分割区域
            start_y, end_y = self.vertical_selection

            # 计算分割点
            self.processor.process_image(start_y, end_y)
            self.split_points = self.processor.split_points
            self.progress_var.set(30)

            if not self.split_points:
                messagebox.showwarning("警告", "未找到匹配的分割点")
                return

            self.log_message(f"找到 {len(self.split_points)} 个分割点")
            self.progress_var.set(50)

            # 获取原始图片路径
            file_path = self.processor.original_image.filename
            logger.debug(f"原始图片路径：{file_path}")

            # 创建分割器并处理
            splitter = ImageSplitter(
                image_path=file_path,
                width_range=self.selection,
                feature_range=self.vertical_selection,
                progress_callback=self.update_progress,
                log_callback=self.log_message,
            )

            splitter.process()
            self.progress_var.set(100)
            logger.success("图片处理完成")
            messagebox.showinfo("成功", "图片处理完成！")

        except Exception as e:
            logger.error(f"处理图片时出错：{str(e)}")
            messagebox.showerror("错误", f"处理图片时出错：{str(e)}")
        finally:
            # 隐藏进度条
            self.progress_bar.pack_forget()

    def update_progress(self, progress: float):
        """更新进度条"""
        self.progress_var.set(50 + progress * 0.5)  # 50-100%用于图片处理进度

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y  # 添加y坐标记录
        if self.rect:
            self.canvas.delete(self.rect)

    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)

        preview_height = (
            self.processor.image_info.preview_height
            if self.processor.image_info
            else 2000
        )

        # 根据当前激活的按钮决定是垂直还是水平选择框
        if self.crop_button["state"] == "normal":
            # 垂直选择框（全高度）
            self.rect = self.canvas.create_rectangle(
                self.start_x,
                0,
                event.x,
                preview_height,
                outline="red",
            )
        elif self.split_button["state"] == "normal":
            # 水平选择框（全宽度）
            preview_width = self.processor.image_info.preview_width
            self.rect = self.canvas.create_rectangle(
                0,
                self.start_y,
                preview_width,
                event.y,
                outline="blue",
            )

    def on_release(self, event):
        if self.processor.image_info:
            if self.crop_button["state"] == "normal":
                # 垂直选择（宽度选择）
                real_start_x = self.processor.get_real_coordinates(
                    min(self.start_x, event.x)
                )
                real_end_x = self.processor.get_real_coordinates(
                    max(self.start_x, event.x)
                )
                self.selection = (real_start_x, real_end_x)
                self.log_message(f"已选择裁剪宽度范围：{self.selection}")
            elif self.split_button["state"] == "normal":
                # 水平选择（分割选择）
                real_start_y = self.processor.get_real_coordinates(
                    min(self.start_y, event.y)
                )
                real_end_y = self.processor.get_real_coordinates(
                    max(self.start_y, event.y)
                )
                self.vertical_selection = (real_start_y, real_end_y)
                self.log_message(f"已选择特征区域范围：{self.vertical_selection}")

    def log_message(self, message: str):
        """向日志区域和文件添加消息"""
        # GUI显示
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        # 终端和文件记录
        logger.info(message)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
