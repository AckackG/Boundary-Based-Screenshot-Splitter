# 网页长截图分割 / Boundary-Based Screenshot Splitter

[English](#english) | [中文](#chinese)

<h2 id="chinese">中文文档</h2>

将长图(如百度文库、道客巴巴等文档网站的整页截图)，根据图片的边界，分割成独立图片或生成多页PDF文档。

## 使用步骤

1. 下载并解压本软件
2. 双击运行 `setup.bat` 完成初始配置
3. 配置完成后，双击 `start.bat` 即可开始使用
4. 操作说明：
   - 获取网页长截图，我用的是 FastStoneCapture 的滚动截图功能
   - 先用红色框选设定保留的内容宽度
   - ⭐再用蓝色框选标记边界区域，比如PDF页面之间灰色的分割线
   - 点击处理按钮，自动完成分割

## 为什么有这个项目
在开发这个项目之前，我遇到了以下问题：

1. 很多在线文档网站采用"查看免费，下载收费"的模式，给文档获取带来不便
2. 市面上现有的长图分割工具大多采用固定距离机械分割，无法智能识别文档的自然分界点
3. 文档类网页的长截图通常在段落或章节之间有明显的视觉边界，这些边界可以作为智能分割的依据

---

## 项目文件

本项目包含以下主要组件：
* `image_cropper.py`: 图像裁剪模块
* `pdf_generator.py`: PDF 生成模块
* `image_splitter.py`: 图像分割模块

---

<h2 id="english">English Documentation</h2>

Intelligently split long screenshots (such as those from Baidu Library, Docbaoba and other document websites) into separate images or multi-page PDF documents by detecting natural content boundaries.

## Getting Started

1. Download and extract the software
2. Double-click `setup.bat` to complete initial setup
3. After setup, double-click `start.bat` to launch the application
4. Operation guide:
   - Get a long webpage screenshot (I use FastStoneCapture's scrolling capture feature)
   - First use red selection to set the content width to keep
   - ⭐Then use blue selection to mark boundary areas, such as gray dividing lines between PDF pages
   - Click the process button to complete the splitting automatically

## Why This Project

Before developing this project, I encountered several challenges:

1. Many online document platforms use a "free to view, pay to download" model, making document acquisition inconvenient
2. Existing long image splitting tools mostly use fixed-distance mechanical splitting, unable to intelligently recognize natural document boundaries
3. Document webpage screenshots usually have clear visual boundaries between paragraphs or chapters, which can serve as intelligent splitting points

---

## Project Files

This project contains the following main components:
* `image_cropper.py`: Image cropping module
* `pdf_generator.py`: PDF generation module
* `image_splitter.py`: Image splitting module