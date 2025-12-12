import os
import shutil
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


def get_excel_sheets(excel_path):
    """获取Excel文件的所有sheet名称"""
    try:
        xl_file = pd.ExcelFile(excel_path)
        return xl_file.sheet_names
    except Exception as e:
        raise Exception(f"读取Excel文件失败: {str(e)}")


def get_sheet_columns(excel_path, sheet_name):
    """获取指定sheet的所有列名"""
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, nrows=0)
        return df.columns.tolist()
    except Exception as e:
        raise Exception(f"读取sheet列名失败: {str(e)}")


def create_image(data, output_path):
    """将一行数据创建为图片"""
    # --- Configuration ---
    FONT_SIZE = 24
    PADDING = 25
    LINE_SPACING = 15
    SEPARATOR_HEIGHT = 1
    SEPARATOR_COLOR = (220, 220, 220)  # Light grey
    FONT_COLOR = (0, 0, 0)  # Black
    BACKGROUND_COLOR = (255, 255, 255)  # White
    KEY_VALUE_SEPARATOR = " : "

    try:
        # Using STHeiti (Heiti SC) which is common on macOS and supports Chinese.
        # For Windows, 'msyh.ttc' (Microsoft YaHei) is a good alternative.
        # For Linux, a font like 'NotoSansCJK-Regular.otf' would be suitable.
        font = ImageFont.truetype("STHeiti Medium.ttc", FONT_SIZE)
    except IOError:
        try:
            # Windows fallback
            font = ImageFont.truetype("msyh.ttc", FONT_SIZE)
        except IOError:
            # Fallback to default font if the specified font is not found.
            font = ImageFont.load_default()

    # --- Calculate image dimensions ---
    max_text_width = 0
    total_height = PADDING

    lines = [f"{header}{KEY_VALUE_SEPARATOR}{value if value is not None and str(value).strip() != '' else ''}" 
             for header, value in data.items()]

    # Use a dummy image to calculate text sizes accurately
    dummy_img = Image.new('RGB', (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    for i, line in enumerate(lines):
        bbox = dummy_draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width > max_text_width:
            max_text_width = text_width

        total_height += text_height
        if i < len(lines) - 1:
            # Add space for the line and the separator
            total_height += LINE_SPACING + SEPARATOR_HEIGHT

    total_height += PADDING
    image_width = max_text_width + (PADDING * 2)

    # --- Create Image and Draw ---
    img = Image.new('RGB', (int(image_width), int(total_height)), color=BACKGROUND_COLOR)
    d = ImageDraw.Draw(img)

    y_cursor = PADDING
    for i, line in enumerate(lines):
        # Draw text
        d.text((PADDING, y_cursor), line, font=font, fill=FONT_COLOR)

        # Calculate text height for this line to advance the cursor
        bbox = d.textbbox((0, 0), line, font=font)
        text_height = bbox[3] - bbox[1]

        # Move cursor down past the text
        y_cursor += text_height

        # Draw separator line if it's not the last item
        if i < len(lines) - 1:
            y_cursor += (LINE_SPACING // 2)
            d.line([(PADDING, y_cursor), (image_width - PADDING, y_cursor)], 
                   fill=SEPARATOR_COLOR, width=SEPARATOR_HEIGHT)
            y_cursor += (LINE_SPACING // 2) + SEPARATOR_HEIGHT

    img.save(output_path)


def copy_dir_files(source, target):
    """复制共享目录中的所有文件到目标目录"""
    if not os.path.exists(source):
        return
    for filename in os.listdir(source):
        source_file = os.path.join(source, filename)
        target_file = os.path.join(target, filename)
        if os.path.isfile(source_file):
            shutil.copy(source_file, target_file)


def generate_images(excel_path, sheet_name, output_dir, naming_field=None, is_grouped=False, share_dir=None):
    """
    生成图片的核心逻辑
    
    Args:
        excel_path: Excel文件路径
        sheet_name: Sheet名称
        output_dir: 输出目录
        naming_field: 命名字段（必选，用于命名文件或分组文件夹）
        is_grouped: 是否分组（如果为True，则按naming_field分组，否则仅用其命名文件）
        share_dir: 共享文件目录（可选）
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取Excel数据
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df = df.fillna('')
    df = df.astype(str).replace(['NaT', 'nan', 'NaN'], '')
    
    if is_grouped and naming_field and naming_field in df.columns:
        # 分组模式：按 naming_field 分组，创建文件夹
        grouped = df.groupby(naming_field)
        
        for group_idx, (group_value, group) in enumerate(grouped):
            case_id = str(group_value)
            # 过滤掉非法字符
            case_id = "".join([c for c in case_id if c.isalnum() or c in (' ', '-', '_')]).strip()
            if not case_id:
                case_id = f"group_{group_idx}"

            case_dir = os.path.join(output_dir, case_id)
            
            if not os.path.exists(case_dir):
                os.makedirs(case_dir)
            
            # 复制共享文件
            if share_dir and os.path.exists(share_dir):
                copy_dir_files(share_dir, case_dir)
            
            # 为分组中的每一行生成图片
            for group_row_index, (original_row_index, row) in enumerate(group.iterrows()):
                # 文件名：分组值_索引.png
                image_name = f"{case_id}_{group_row_index + 1}.png"
                image_path = os.path.join(case_dir, image_name)
                create_image(row, image_path)
    else:
        # 非分组模式：所有图片生成在 output_dir 下
        for index, row in df.iterrows():
            if naming_field and naming_field in row:
                name_val = str(row[naming_field])
                # 过滤非法字符
                name_val = "".join([c for c in name_val if c.isalnum() or c in (' ', '-', '_')]).strip()
                if not name_val:
                     name_val = f"row_{index + 1}"
                image_name = f"{name_val}.png"
                
                # 处理重名：如果文件已存在，添加后缀
                counter = 1
                base_name = image_name
                while os.path.exists(os.path.join(output_dir, image_name)):
                    image_name = f"{os.path.splitext(base_name)[0]}_{counter}.png"
                    counter += 1
            else:
                # 兜底：使用行索引
                image_name = f"row_{index + 1}.png"
            
            image_path = os.path.join(output_dir, image_name)
            create_image(row, image_path)

