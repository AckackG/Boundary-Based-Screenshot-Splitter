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

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 创建打开文件按钮
        open_button = tk.Button(self.root, text="打开图片", command=self.open_image)
        open_button.pack(pady=5)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
