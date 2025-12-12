import os
from tkinter import Toplevel, Label

from PIL import Image, ImageTk
from core.config import SUPPORTED_FORMATS, THUMBNAIL_SIZE


def preview_image(img_path):
    top = Toplevel()
    top.title(img_path)
    img = Image.open(img_path)
    img.thumbnail((800, 800))
    img_tk = ImageTk.PhotoImage(img)

    label = Label(top, image=img_tk)
    label.image = img_tk
    label.pack()

def load_images(folder_path):
    image_list = []
    for fname in sorted(os.listdir(folder_path)):
        if os.path.splitext(fname)[-1].lower() in SUPPORTED_FORMATS:
            full_path = os.path.join(folder_path, fname)
            img = Image.open(full_path)
            img.thumbnail(THUMBNAIL_SIZE)
            img_tk = ImageTk.PhotoImage(img)
            image_list.append({
                "path": full_path,
                "filename": fname,
                "thumbnail": img_tk
            })
    return image_list