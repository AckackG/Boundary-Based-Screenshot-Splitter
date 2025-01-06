# 网页长截图分割 / Boundary-Based Screenshot Splitter

[English](#english) | [中文](#chinese)

<h2 id="chinese">中文文档</h2>

将长图(如百度文库、道客巴巴等文档网站的整页截图)，根据图片的边界，分割成独立图片或生成多页PDF文档。

## 第一步: 安装
### exe 版 (推荐)
1. 在 [Releases](https://github.com/AckackG/Boundary-Based-Screenshot-Splitter/releases) 页面下载最新的 `BoundSplit.exe`
2. 双击运行即可，无需安装Python或其他依赖

### 源码版
1. 下载并解压本软件
2. 双击运行 `setup.bat` 完成初始配置
3. 配置完成后，双击 `start.bat` 即可开始使用

## 第二步: 使用

1. 获取网页长截图
   1. 将网页缩放调整至比屏幕宽度小一点点
   2. 用截图工具截图全网页，我用的是 FastStoneCapture 的滚动截图功能
2. 打开本软件，加载图片
   1. 在图片上框选(红色)，用于设置要保留的图片宽度。点击“裁剪宽度”按钮
   2. 再用蓝色框选标记边界区域，比如PDF页面之间灰色的分割线。点击“选择分割”按钮
   3. 点击“处理图片”按钮，自动完成分割。完成后会打开PDF输出文件夹

## 为什么有这个项目

1. 很多在线文档网站**只能看不能下载，且无法用右键打印为PDF**。所以只能用截图工具截取整页图片，然后手动裁剪。
2. 市面上现有的长图分割工具大多采用固定距离机械分割，无法智能识别文档的自然分界点
3. 文档类网页的长截图通常在段落或章节之间有明显的视觉边界，这些边界可以作为智能分割的依据


---

<h2 id="english">English Documentation</h2>

Intelligently split long screenshots (such as those from Baidu Library, Docbaoba and other document websites) into separate images or multi-page PDF documents by detecting natural content boundaries.

## Step 1: Installation
### Executable Version (Recommended)
1. Download `BoundSplit.exe` from the [Releases](https://github.com/AckackG/Boundary-Based-Screenshot-Splitter/releases) page
2. Run it directly, no Python or other dependencies required

### Source Code Version
1. Download and extract the software
2. Double-click `setup.bat` to complete initial setup
3. After setup, double-click `start.bat` to launch the application

## Step 2: Usage

1. Get a webpage screenshot
   1. Adjust webpage zoom until it's slightly narrower than your screen
   2. Capture the full webpage (I use FastStoneCapture's scrolling capture feature)
2. Open this software and load your image
   1. Make a red selection on the image to set the width to keep. Click "Crop Width" button
   2. ⭐Then use blue selection to mark boundary areas (like gray dividing lines between PDF pages). Click "Select Split" button
   3. Click "Process Image" button to complete the splitting automatically. The PDF output folder will open when finished

## Why This Project

1. **Many online document websites only allow viewing but not downloading, and right-click PDF printing is disabled**. The only option was to use screenshot tools and manually crop images.
2. Existing long image splitting tools mostly use fixed-distance mechanical splitting, unable to intelligently recognize natural document boundaries
3. Document webpage screenshots usually have clear visual boundaries between paragraphs or chapters, which can serve as intelligent splitting points
