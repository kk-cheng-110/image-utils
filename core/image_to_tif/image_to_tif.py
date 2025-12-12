import io
import os
from typing import Optional, List

import fitz  # PyMuPDF
from PIL import Image

SUPPORTED_IMAGE_SUFFIX = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.pdf'}


def preview_image(image_path) -> Image.Image:
    """
    根据文件路径加载预览图像：
    - 支持常规图片格式
    - 对于 PDF，仅返回首页的 RGB 图像，确保依赖 Poppler
    返回一个 PIL.Image 实例，调用者负责在使用后关闭它。
    """
    ext = os.path.splitext(image_path)[1].lower()
    if ext == '.pdf':
        try:
            # 使用 pdf2image 将 PDF 首页转换为图像
            img = pdf_to_image(image_path, [0])[0]
            return img
        except Exception as e:
            raise IOError(f"PDF 预览失败: {e}")
    else:
        # 常规图像直接打开
        return Image.open(image_path)


def pdf_to_image(pdf_path: str, pages: Optional[List[int]] = None, dpi: int = 200) -> List[Image.Image]:
    """
    使用 PyMuPDF 将 PDF 转为图片，不依赖 Poppler。
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    # 如果 pages 没有传，默认取所有页
    if pages is None:
        pages = list(range(total_pages))

    images = []
    for i in pages:
        if 0 <= i < total_pages:
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            images.append(image)
    doc.close()
    return images


def load_images(directory: str):
    """
    扫描目录，返回可处理的图像和 PDF 文件路径列表。
    保持文件在目录中列出的原始顺序，不进行排序。
    """
    image_paths = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        ext = os.path.splitext(filename)[1].lower()
        if os.path.isfile(file_path) and ext in SUPPORTED_IMAGE_SUFFIX:
            image_paths.append(file_path)
    return image_paths


def merge_images_to_tif(image_paths: list[str], output_path: str, compression='raw', dpi=200, jpeg_quality=None, progress_callback=None):
    """
    将按照传入的 image_paths 顺序，将图像和 PDF 页面合并为一个多页 TIFF 文件。
    PDF 文件会被拆分为单独的页面图像。
    compression 可选：'raw'（无压缩）, 'lzw', 'jpeg', 'deflate', 'packbits', 'zlib' 等
    dpi: 输出TIFF文件的分辨率，默认200
    jpeg_quality: JPEG压缩质量，1-100，仅在compression='jpeg'时有效
    progress_callback: 可选的回调函数，用于报告进度。接受两个参数：当前进度 (0-100) 和消息。
    """
    images = []
    total_images = len(image_paths)

    for i, path in enumerate(image_paths):
        if progress_callback:
            progress = int((i / total_images) * 100)
            progress_callback(progress, f"正在处理图片: {os.path.basename(path)}")

        ext = os.path.splitext(path)[1].lower()
        if ext == '.pdf':
            # 打开 PDF 并逐页转换
            pdf_images = pdf_to_image(path, dpi=dpi)
            images.extend(pdf_images)
        else:
            img = Image.open(path).convert('RGB')
            images.append(img)

    if not images:
        raise ValueError('没有找到任何可合并的图像或 PDF 页面')

    if progress_callback:
        progress_callback(90, "正在保存TIF文件...") # 保存前给一个较高的进度

    try:
        # 准备保存参数
        save_kwargs = {
            'format': 'TIFF',
            'save_all': True,
            'append_images': images[1:],
            'compression': compression,
            'dpi': (dpi, dpi)
        }
        
        # 如果是JPEG压缩且提供了质量参数，则添加quality参数
        if compression == 'jpeg' and jpeg_quality is not None:
            save_kwargs['quality'] = jpeg_quality

        images[0].save(output_path, **save_kwargs)
    finally:
        for img in images:
            img.close()

    if progress_callback:
        progress_callback(100, "TIF文件保存完成！")
