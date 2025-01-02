import tkinter as tk
from tkinter import filedialog
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
        self.crop_button = None  # 裁剪按钮

        # 创建按钮框架
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="top", fill="x", padx=5, pady=5)

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 创建打开文件按钮
        open_button = tk.Button(
            self.button_frame, text="打开图片", command=self.open_image
        )
        open_button.pack(side="left", padx=5)

        # 创建画布
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(expand=True, fill="both")

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

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

            # 创建裁剪宽度按钮（如果尚未创建）
            if not self.crop_button:
                self.crop_button = tk.Button(
                    self.button_frame, text="裁剪宽度", command=self.crop_width
                )
                self.crop_button.pack(side="left", padx=5)
                self.button_frame.update()  # 强制更新按钮框架

    def on_press(self, event):
        self.start_x = event.x
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
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            0,
            event.x,
            preview_height,
            outline="red",
        )

    def on_release(self, event):
        if self.processor.image_info:
            # 转换为原图坐标
            real_start_x = self.processor.get_real_coordinates(
                min(self.start_x, event.x)
            )
            real_end_x = self.processor.get_real_coordinates(max(self.start_x, event.x))
            self.selection = (real_start_x, real_end_x)
            print(f"原图选择范围：{self.selection}")

    def crop_width(self):
        if self.processor.original_image:
            if self.selection:
                # 使用用户选择的宽度
                start_x, end_x = self.selection
            else:
                # 使用图片的默认宽度
                start_x, end_x = 0, self.processor.original_image.width

            # 裁剪图片
            cropped_image = self.processor.original_image.crop(
                (start_x, 0, end_x, self.processor.original_image.height)
            )
            cropped_image.show()  # 显示裁剪后的图片
            print(f"裁剪后的宽度：{end_x - start_x}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
