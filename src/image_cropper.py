import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk
from src.image_processor import ImageProcessor
from src.image_splitter import ImageSplitter
from loguru import logger
from pathlib import Path
import os
import subprocess
import threading
import queue  # 导入 queue 模块

# 配置日志
log_path = Path("../logs")
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

        # 设置窗口背景色
        self.root.configure(bg="#f0f0f0")

        # 定义字体
        font_family = "微软雅黑"  # 尝试使用微软雅黑，如果不存在则使用默认字体
        font_size = 9
        self.default_font = (font_family, font_size)
        self.root.option_add("*Font", self.default_font)

        # 配置按钮样式
        button_bg = "#e0e0e0"
        button_fg = "#000000"
        button_relief = "flat"

        self.root.option_add("*Button.Background", button_bg)
        self.root.option_add("*Button.Foreground", button_fg)
        self.root.option_add("*Button.relief", button_relief)

        # 配置Label样式
        self.root.option_add("*Label.Background", "#f0f0f0")

        # 计算初始窗口高度为屏幕的 80%
        screen_height = self.root.winfo_screenheight()
        initial_height = int(screen_height * 0.8)

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
        self.button_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(side="top", fill="x", padx=5, pady=5)

        # 创建界面
        self.create_widgets(initial_height)  # 传递初始高度

        # 初始化按钮状态
        self.update_button_states("init")

        # 创建一个队列用于线程间通信
        self.log_queue = queue.Queue()
        self.root.after(100, self.process_log_queue)  # 定期处理日志队列

    def create_widgets(self, initial_height):
        # 创建主框架，用于左右布局
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # 创建左侧框架
        self.left_frame = tk.Frame(
            self.main_frame, height=initial_height, bg="#f0f0f0"
        )  # 设置初始高度
        self.left_frame.pack(side="left", expand=True, fill="both")

        # 创建右侧框架
        self.right_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.right_frame.pack(side="right", fill="y", padx=(5, 0))

        # 创建按钮框架（放在左侧框架顶部）
        self.button_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
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
            self.button_frame, text="处理图片", command=self.start_process_image
        )
        self.process_button.pack(side="left", padx=5)

        # 创建画布（放在左侧框架）
        self.canvas = tk.Canvas(self.left_frame, highlightthickness=0, bg="white")
        self.canvas.pack(expand=True, fill="both")

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # 添加日志文本框（放在右侧框架）
        # 添加标题标签
        tk.Label(self.right_frame, text="处理日志", bg="#f0f0f0").pack(
            side="top", pady=(0, 5)
        )

        self.log_text = tk.Text(
            self.right_frame, width=30, height=20, bg="white", fg="black"
        )
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

            # 限制窗口高度为屏幕的 80%
            screen_height = self.root.winfo_screenheight()
            max_height = int(screen_height * 0.8)
            new_height = min(image_info.preview_height, max_height)

            # 显示图片
            self.photo = ImageTk.PhotoImage(preview_image)
            self.canvas.config(width=image_info.preview_width, height=new_height)
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

            # 更新左侧框架的高度
            self.left_frame.config(height=new_height)

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

    def start_process_image(self):
        """启动图片处理线程"""
        if not all([self.selection, self.vertical_selection]):
            logger.warning("未选择裁剪宽度或特征区域")
            messagebox.showwarning("警告", "请先选择裁剪宽度和特征区域")
            return

        # 创建并启动线程
        threading.Thread(target=self._process_image_in_thread).start()

    def _process_image_in_thread(self):
        """在线程中处理图片"""
        self.root.config(cursor="wait")  # 设置鼠标为等待状态
        self.progress_bar.pack(side="bottom", fill="x", padx=5, pady=5)
        self.progress_var.set(0)

        try:
            logger.info("开始处理图片")

            # 获取分割区域
            start_y, end_y = self.vertical_selection

            # 计算分割点
            self.processor.process_image(start_y, end_y)
            self.split_points = self.processor.split_points
            self.update_progress(30)

            if not self.split_points:
                messagebox.showwarning("警告", "未找到匹配的分割点")
                return

            self.log_message(f"找到 {len(self.split_points)} 个分割点")
            self.update_progress(50)

            # 获取原始图片路径
            file_path = self.processor.original_image.filename
            logger.debug(f"原始图片路径：{file_path}")

            # 创建分割器并处理
            splitter = ImageSplitter(
                image_path=file_path,
                width_range=self.selection,
                feature_range=self.vertical_selection,
                progress_callback=self.update_progress_from_thread,
                log_callback=self.log_message_from_thread,
            )

            pdf_path = splitter.process()
            self.update_progress(100)
            logger.success("图片处理完成")

            # 打开PDF所在文件夹
            pdf_dir = Path(pdf_path).parent
            self.log_message(f"处理完成！PDF保存在：{pdf_dir}")

            # 使用 after 方法在主线程中打开文件夹
            self.root.after(100, self.open_folder, pdf_dir)

        except Exception as e:
            logger.error(f"处理图片时出错：{str(e)}")
            messagebox.showerror("错误", f"处理图片时出错：{str(e)}")
        finally:
            self.progress_bar.pack_forget()
            self.root.config(cursor="")  # 恢复鼠标状态

    def update_progress_from_thread(self, progress: float):
        """在线程中更新进度条"""
        self.root.after(0, self.progress_var.set, 50 + progress * 0.5)

    def log_message_from_thread(self, message: str):
        """在线程中发送日志消息到队列"""
        self.log_queue.put(message)

    def process_log_queue(self):
        """处理日志队列中的消息"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_message(message)
                self.log_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)

    def open_folder(self, folder_path: Path):
        """在主线程中安全地打开文件夹"""
        try:
            if os.name == "nt":  # Windows
                os.startfile(folder_path)
            else:  # Linux/Mac
                subprocess.run(["xdg-open", str(folder_path)])
        except Exception as e:
            logger.error(f"打开文件夹时出错：{str(e)}")
            messagebox.showerror("错误", f"打开文件夹时出错：{str(e)}")

    def update_progress(self, progress: float):
        """更新进度条"""
        self.progress_var.set(progress)  # 0-100%

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


def run():
    root = tk.Tk()

    # 获取屏幕高度
    screen_height = root.winfo_screenheight()
    # 计算顶部偏移量 (5% of screen height)
    offset = int(screen_height * 0.05)
    # 设置窗口初始位置
    root.geometry(f"+0+{offset}")

    app = ImageCropper(root)
    root.mainloop()


if __name__ == "__main__":
    run()
