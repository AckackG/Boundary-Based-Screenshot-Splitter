import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from image_processor import ImageProcessor


class ImageCropper:
    def __init__(self, root):
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

        # 创建画布
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(expand=True, fill="both")

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

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
            # 处理图片
            preview_image, image_info = self.processor.load_image(file_path)

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
        """准备分割"""
        if not self.vertical_selection:
            messagebox.showwarning("警告", "必须选择特征区域")
            return

        start_y, end_y = self.vertical_selection
        split_points = self.processor.find_split_points(start_y, end_y)

        if not split_points:
            messagebox.showwarning("警告", "未找到匹配的分割点")
            return

        # 存储找到的分割点
        self.split_points = split_points
        print(f"找到 {len(split_points)} 个分割点")

        # 更新按钮状态
        self.update_button_states("split")

    def process_image(self):
        """处理图片"""
        if not all([self.selection, self.vertical_selection, self.split_points]):
            messagebox.showwarning("警告", "缺少必要的处理参数")
            return

        try:
            from image_splitter import ImageSplitter

            # 获取原始图片路径
            file_path = self.processor.original_image.filename

            # 创建分割器并处理
            splitter = ImageSplitter(
                image_path=file_path,
                width_range=self.selection,
                feature_range=self.vertical_selection,
            )

            splitter.process()
            messagebox.showinfo("成功", "图片处理完成！")

        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错：{str(e)}")

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
                print(f"宽度选择范围：{self.selection}")
            elif self.split_button["state"] == "normal":
                # 水平选择（分割选择）
                real_start_y = self.processor.get_real_coordinates(
                    min(self.start_y, event.y)
                )
                real_end_y = self.processor.get_real_coordinates(
                    max(self.start_y, event.y)
                )
                self.vertical_selection = (real_start_y, real_end_y)
                print(f"水平分割范围：{self.vertical_selection}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
