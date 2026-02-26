#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixel Art Coordinate and Color Extractor Tool
像素画坐标与颜色提取工具

支持从本地像素画图像中提取每个像素的坐标与颜色，并输出为 Python 代码文件。
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

# 支持的图像格式
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


def load_image(path: str) -> Image.Image:
    """加载图像，确保有 RGBA 信息以处理透明度。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"不支持的格式: {path.suffix}，支持: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    img = Image.open(path)
    # 统一转为 RGBA 以便处理透明通道
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def get_dimensions(img: Image.Image) -> tuple[int, int]:
    """获取图像尺寸 (宽, 高)。"""
    return img.size


def extract_pixels(
    img: Image.Image,
    transparent_handling: str = "mark_none",
    multiplier: int = 1,
    color_format: str = "hex",
) -> dict:
    """
    提取每个像素的坐标与颜色。

    :param img: PIL Image (RGBA)
    :param transparent_handling: "mark_none" 将透明像素记为 None，"skip" 则跳过透明像素
    :param multiplier: 坐标单位倍数，如 2 则 (1,1) 输出为 (2,2)
    :param color_format: "hex" 或 "rgb"
    :return: {(x, y): "#RRGGBB" | (r,g,b) | None}
    """
    width, height = img.size
    pixels = img.load()
    result = {}

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # 透明像素
            if a == 0:
                if transparent_handling == "skip":
                    continue
                value = None
            else:
                if color_format == "hex":
                    value = f"#{r:02X}{g:02X}{b:02X}"
                else:
                    value = (r, g, b)

            coord = (x * multiplier, y * multiplier)
            result[coord] = value

    return result


def format_value(v) -> str:
    """将单个值格式化为 Python 代码字符串（逗号在注释前以便 exec 解析）。"""
    if v is None:
        return "None,  # Transparent"
    if isinstance(v, str):
        return repr(v)
    if isinstance(v, tuple):
        return str(v)
    return repr(v)


def generate_python_code(
    pixel_data: dict,
    width: int,
    height: int,
    color_format: str = "hex",
    output_path: str | None = None,
) -> str:
    """
    生成符合文档示例的 Python 代码字符串。
    """
    comment = "Hex Color" if color_format == "hex" else "RGB tuple"
    lines = [
        "# Auto-generated pixel data (Size: {}x{})".format(width, height),
        "# Format: {(x, y): \"" + comment + "\"}",
        "PIXEL_DATA = {",
    ]
    # 按 (x,y) 排序输出，便于阅读
    for (x, y) in sorted(pixel_data.keys(), key=lambda k: (k[1], k[0])):
        v = pixel_data[(x, y)]
        lines.append("    ({}, {}): {},".format(x, y, format_value(v)))
    lines.append("}")
    code = "\n".join(lines)
    return code


def run_extraction(
    image_path: str,
    output_path: str | None = None,
    transparent_handling: str = "mark_none",
    multiplier: int = 1,
    color_format: str = "hex",
) -> str:
    """
    执行一次完整提取并返回生成的代码；若提供 output_path 则写入文件。
    """
    img = load_image(image_path)
    width, height = get_dimensions(img)
    pixel_data = extract_pixels(
        img,
        transparent_handling=transparent_handling,
        multiplier=multiplier,
        color_format=color_format,
    )
    code = generate_python_code(
        pixel_data, width, height, color_format=color_format, output_path=output_path
    )
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(code, encoding="utf-8")
    return code


def main_cli():
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="Pixel Art Coordinate and Color Extractor (CLI)"
    )
    parser.add_argument("image", help="输入图像路径 (.png / .jpg / .bmp)")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="输出 Python 文件路径（默认: pixel_data.py）",
    )
    parser.add_argument(
        "--transparent",
        choices=("mark_none", "skip"),
        default="mark_none",
        help="透明像素: mark_none=记为 None, skip=跳过",
    )
    parser.add_argument(
        "--multiplier",
        type=int,
        default=1,
        metavar="N",
        help="坐标倍数，默认 1",
    )
    parser.add_argument(
        "--format",
        choices=("hex", "rgb"),
        default="hex",
        help="颜色格式: hex 或 rgb",
    )
    args = parser.parse_args()
    output = args.output or "pixel_data.py"
    run_extraction(
        args.image,
        output_path=output,
        transparent_handling=args.transparent,
        multiplier=args.multiplier,
        color_format=args.format,
    )
    print(f"已生成: {output}")


def main_gui(parent=None):
    """GUI 入口：图形化界面选择文件并执行提取。parent 不为 None 时在 Toplevel 中打开（供统一启动器调用）。"""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("未找到 tkinter，请使用 CLI: python pixel_extractor.py <image> -o pixel_data.py")
        sys.exit(1)

    def choose_file():
        path = filedialog.askopenfilename(
            title="选择像素画图像",
            filetypes=[
                ("PNG 图像", "*.png"),
                ("JPEG 图像", "*.jpg *.jpeg"),
                ("BMP 图像", "*.bmp"),
                ("所有支持格式", "*.png *.jpg *.jpeg *.bmp"),
            ],
        )
        if path:
            entry_path.delete(0, tk.END)
            entry_path.insert(0, path)
            update_preview(path)

    def choose_output():
        path = filedialog.asksaveasfilename(
            title="保存 Python 数据文件",
            defaultextension=".py",
            filetypes=[("Python 文件", "*.py"), ("文本文件", "*.txt")],
            initialfile="pixel_data.py",
        )
        if path:
            entry_output.delete(0, tk.END)
            entry_output.insert(0, path)

    def update_preview(img_path: str):
        """更新图像预览与尺寸信息。"""
        lbl_preview.config(image="", text="")
        lbl_preview.image = None
        lbl_size.config(text="")
        if not img_path or not Path(img_path).exists():
            return
        try:
            img = load_image(img_path)
            w, h = get_dimensions(img)
            lbl_size.config(text=f"尺寸: {w} × {h} 像素")
            from PIL import ImageTk
            scale = min(120 / w, 120 / h, 1.0)
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            thumb = img.resize((new_w, new_h), Image.NEAREST)
            photo = ImageTk.PhotoImage(thumb)
            lbl_preview.config(image=photo, text="")
            lbl_preview.image = photo
        except Exception:
            lbl_preview.config(image="", text="(预览不可用)")
            lbl_preview.image = None
            lbl_size.config(text="")

    def do_extract():
        img_path = entry_path.get().strip()
        out_path = entry_output.get().strip() or "pixel_data.py"
        if not img_path:
            messagebox.showerror("错误", "请先选择输入图像")
            return
        try:
            mult = int(spin_multiplier.get())
            if mult < 1 or mult > 100:
                raise ValueError("坐标倍数请在 1～100 之间")
        except ValueError as e:
            messagebox.showerror("错误", f"坐标倍数无效: {e}")
            return
        try:
            run_extraction(
                img_path,
                output_path=out_path,
                transparent_handling=var_transparent.get(),
                multiplier=mult,
                color_format=var_format.get(),
            )
            status_var.set(f"已生成: {out_path}")
            messagebox.showinfo("完成", f"已生成:\n{out_path}")
        except Exception as e:
            status_var.set("提取失败")
            messagebox.showerror("错误", str(e))

    from pixel_gui_util import make_scrollable

    root = tk.Toplevel(parent) if parent else tk.Tk()
    root.title("Pixel Art 坐标与颜色提取工具")
    root.minsize(560, 380)
    root.geometry("600x420")
    root.resizable(True, True)

    scroll_container, main = make_scrollable(root)
    scroll_container.pack(fill=tk.BOTH, expand=True)
    main.configure(padding=16)

    # 标题
    title = ttk.Label(main, text="像素画坐标与颜色提取工具", font=("", 14, "bold"))
    title.pack(anchor=tk.W, pady=(0, 12))

    # 上半部分：文件与预览
    frm_top = ttk.LabelFrame(main, text="文件", padding=10)
    frm_top.pack(fill=tk.X, pady=(0, 10))

    frm_file = ttk.Frame(frm_top)
    frm_file.pack(fill=tk.X)
    ttk.Label(frm_file, text="输入图像", width=8).grid(row=0, column=0, sticky=tk.W, pady=4)
    entry_path = ttk.Entry(frm_file, width=42)
    entry_path.grid(row=0, column=1, padx=6, pady=4)
    ttk.Button(frm_file, text="浏览...", command=choose_file).grid(row=0, column=2, pady=4)

    ttk.Label(frm_file, text="输出文件", width=8).grid(row=1, column=0, sticky=tk.W, pady=4)
    entry_output = ttk.Entry(frm_file, width=42)
    entry_output.insert(0, "pixel_data.py")
    entry_output.grid(row=1, column=1, padx=6, pady=4)
    ttk.Button(frm_file, text="另存为...", command=choose_output).grid(row=1, column=2, pady=4)

    frm_preview = ttk.Frame(frm_top)
    frm_preview.pack(fill=tk.X, pady=(8, 0))
    lbl_preview = ttk.Label(frm_preview, text="(选择图像后显示预览)", relief=tk.SUNKEN, anchor=tk.CENTER)
    lbl_preview.pack(side=tk.LEFT, padx=(0, 10))
    lbl_size = ttk.Label(frm_preview, text="")
    lbl_size.pack(side=tk.LEFT, anchor=tk.W)

    # 下半部分：选项
    frm_opts = ttk.LabelFrame(main, text="选项", padding=10)
    frm_opts.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(frm_opts, text="透明像素", width=10).grid(row=0, column=0, sticky=tk.W, pady=4)
    var_transparent = tk.StringVar(value="mark_none")
    ttk.Radiobutton(frm_opts, text="记为 None", variable=var_transparent, value="mark_none").grid(
        row=0, column=1, sticky=tk.W, pady=4
    )
    ttk.Radiobutton(frm_opts, text="跳过透明像素", variable=var_transparent, value="skip").grid(
        row=0, column=2, sticky=tk.W, padx=(8, 0), pady=4
    )

    ttk.Label(frm_opts, text="坐标倍数", width=10).grid(row=1, column=0, sticky=tk.W, pady=4)
    spin_multiplier = ttk.Spinbox(frm_opts, from_=1, to=100, width=8)
    spin_multiplier.set(1)
    spin_multiplier.grid(row=1, column=1, sticky=tk.W, padx=6, pady=4)
    ttk.Label(frm_opts, text="（1 像素 = N 单位）", foreground="gray").grid(
        row=1, column=2, sticky=tk.W, pady=4
    )

    ttk.Label(frm_opts, text="颜色格式", width=10).grid(row=2, column=0, sticky=tk.W, pady=4)
    var_format = tk.StringVar(value="hex")
    ttk.Radiobutton(frm_opts, text="十六进制 #RRGGBB", variable=var_format, value="hex").grid(
        row=2, column=1, sticky=tk.W, pady=4
    )
    ttk.Radiobutton(frm_opts, text="RGB 元组 (r, g, b)", variable=var_format, value="rgb").grid(
        row=2, column=2, sticky=tk.W, padx=(8, 0), pady=4
    )

    # 操作按钮
    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill=tk.X, pady=12)
    ttk.Button(btn_frame, text="提取并保存", command=do_extract).pack(side=tk.LEFT, padx=(0, 8))

    # 状态栏（固定在窗口底部，不随内容滚动）
    status_var = tk.StringVar(value="请选择输入图像后点击「提取并保存」")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 0))

    if parent is None:
        root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main_gui()
    else:
        main_cli()
