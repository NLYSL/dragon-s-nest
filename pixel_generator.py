#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixel Art Generator - 从 PIXEL_DATA 格式的 Python 代码生成像素画图像

读取与提取工具输出格式一致的 Python 文件（PIXEL_DATA = {(x,y): color}），
生成对应的 PNG 像素画图像，支持透明像素。
"""

import argparse
import re
import sys
from pathlib import Path

from PIL import Image


def load_pixel_data(file_path: str) -> dict:
    """
    从 Python 文件中加载 PIXEL_DATA 字典。
    支持格式：{(x, y): "#RRGGBB" | (r,g,b) | None}
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    with open(path, encoding="utf-8") as f:
        code = f.read()

    # 兼容旧版提取器输出：None  # ... 的逗号在注释内会导致语法错误，规范为 None,  # ...
    code = code.replace("None  # ", "None,  # ")

    namespace = {}
    try:
        exec(code, namespace)
    except Exception as e:
        raise ValueError(f"无法执行数据文件: {e}") from e

    if "PIXEL_DATA" not in namespace:
        raise ValueError("文件中未找到 PIXEL_DATA 变量")

    return namespace["PIXEL_DATA"]


def parse_color(value) -> tuple[int, int, int, int] | None:
    """
    将数据中的颜色值解析为 (r, g, b, a)。
    - None -> 透明，返回 None（调用方用 0,0,0,0 绘制）
    - "#RRGGBB" 或 "#RGB" -> 不透明
    - (r, g, b) 或 (r, g, b, a) -> 元组
    """
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        if s.upper() in ("NONE", "TRANSPARENT"):
            return None
        # #RRGGBB 或 #RGB
        match = re.match(r"^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$", s)
        if match:
            hex_str = match.group(1)
            if len(hex_str) == 6:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
            else:
                r = int(hex_str[0] * 2, 16)
                g = int(hex_str[1] * 2, 16)
                b = int(hex_str[2] * 2, 16)
            return (r, g, b, 255)
        raise ValueError(f"无法识别的颜色字符串: {value!r}")
    if isinstance(value, (list, tuple)):
        arr = list(value)
        if len(arr) == 3:
            return (int(arr[0]), int(arr[1]), int(arr[2]), 255)
        if len(arr) == 4:
            return (int(arr[0]), int(arr[1]), int(arr[2]), int(arr[3]))
        raise ValueError(f"颜色元组长度应为 3 或 4: {value!r}")
    raise ValueError(f"不支持的颜色类型: {type(value)}")


def pixel_data_to_image(pixel_data: dict) -> Image.Image:
    """
    将 PIXEL_DATA 字典转换为 PIL 图像 (RGBA)。
    根据坐标范围自动计算画布尺寸，支持稀疏数据。
    """
    if not pixel_data:
        raise ValueError("PIXEL_DATA 为空，无法生成图像")

    xs = [xy[0] for xy in pixel_data.keys()]
    ys = [xy[1] for xy in pixel_data.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = img.load()

    for (x, y), color_value in pixel_data.items():
        px, py = x - min_x, y - min_y
        rgba = parse_color(color_value)
        if rgba is None:
            pixels[px, py] = (0, 0, 0, 0)
        else:
            pixels[px, py] = rgba

    return img


def generate_image(
    data_file: str,
    output_path: str,
    scale: int = 1,
) -> Image.Image:
    """
    从数据文件生成像素画图像并保存。

    :param data_file: 包含 PIXEL_DATA 的 .py 文件路径
    :param output_path: 输出图像路径（建议 .png 以保留透明）
    :param scale: 每个逻辑像素放大的倍数（1=原尺寸，2=每像素 2x2）
    :return: 生成的 PIL Image
    """
    pixel_data = load_pixel_data(data_file)
    img = pixel_data_to_image(pixel_data)
    if scale > 1:
        w, h = img.size
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return img


def main_cli():
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="从 PIXEL_DATA 格式的 Python 文件生成像素画图像"
    )
    parser.add_argument(
        "data_file",
        help="包含 PIXEL_DATA 的 .py 文件路径",
    )
    parser.add_argument(
        "-o", "--output",
        default="pixel_art.png",
        help="输出图像路径（默认: pixel_art.png）",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=1,
        metavar="N",
        help="像素放大倍数，默认 1（2 即每像素 2×2 显示）",
    )
    args = parser.parse_args()
    generate_image(args.data_file, args.output, scale=args.scale)
    print(f"已生成: {args.output}")


def main_gui(parent=None):
    """图形界面入口。parent 不为 None 时在 Toplevel 中打开（供统一启动器调用）。"""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("未找到 tkinter，请使用 CLI: python pixel_generator.py 数据文件.py -o 输出.png")
        sys.exit(1)

    def choose_data_file():
        path = filedialog.askopenfilename(
            title="选择 PIXEL_DATA 数据文件",
            filetypes=[("Python 文件", "*.py"), ("文本文件", "*.txt")],
        )
        if path:
            entry_data.delete(0, tk.END)
            entry_data.insert(0, path)

    def choose_output():
        path = filedialog.asksaveasfilename(
            title="保存像素画图像",
            defaultextension=".png",
            filetypes=[("PNG 图像", "*.png"), ("所有文件", "*.*")],
            initialfile="pixel_art.png",
        )
        if path:
            entry_output.delete(0, tk.END)
            entry_output.insert(0, path)

    def do_generate():
        data_path = entry_data.get().strip()
        out_path = entry_output.get().strip() or "pixel_art.png"
        if not data_path:
            messagebox.showerror("错误", "请先选择数据文件（.py）")
            return
        try:
            scale = int(scale_var.get())
            if scale < 1 or scale > 32:
                raise ValueError("放大倍数请在 1～32 之间")
        except ValueError as e:
            messagebox.showerror("错误", f"放大倍数无效: {e}")
            return
        try:
            generate_image(data_path, out_path, scale=scale)
            status_var.set(f"已生成: {out_path}")
            messagebox.showinfo("完成", f"已生成:\n{out_path}")
        except Exception as e:
            status_var.set("生成失败")
            messagebox.showerror("错误", str(e))

    from pixel_gui_util import make_scrollable

    root = tk.Toplevel(parent) if parent else tk.Tk()
    root.title("像素画生成器 - 从数据文件生成图像")
    root.minsize(480, 260)
    root.geometry("520x280")
    root.resizable(True, True)

    scroll_container, main = make_scrollable(root)
    scroll_container.pack(fill=tk.BOTH, expand=True)
    main.configure(padding=16)

    ttk.Label(main, text="从 PIXEL_DATA 生成像素画", font=("", 12, "bold")).pack(
        anchor=tk.W, pady=(0, 12)
    )

    frm = ttk.LabelFrame(main, text="文件", padding=10)
    frm.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(frm, text="数据文件", width=10).grid(row=0, column=0, sticky=tk.W, pady=4)
    entry_data = ttk.Entry(frm, width=40)
    entry_data.grid(row=0, column=1, padx=6, pady=4)
    ttk.Button(frm, text="浏览...", command=choose_data_file).grid(row=0, column=2, pady=4)

    ttk.Label(frm, text="输出图像", width=10).grid(row=1, column=0, sticky=tk.W, pady=4)
    entry_output = ttk.Entry(frm, width=40)
    entry_output.insert(0, "pixel_art.png")
    entry_output.grid(row=1, column=1, padx=6, pady=4)
    ttk.Button(frm, text="另存为...", command=choose_output).grid(row=1, column=2, pady=4)

    ttk.Label(frm, text="放大倍数", width=10).grid(row=2, column=0, sticky=tk.W, pady=4)
    scale_var = tk.StringVar(value="1")
    spin = ttk.Spinbox(frm, from_=1, to=32, width=6, textvariable=scale_var)
    spin.set(1)
    spin.grid(row=2, column=1, sticky=tk.W, padx=6, pady=4)
    ttk.Label(frm, text="（每个逻辑像素的显示尺寸）", foreground="gray").grid(
        row=2, column=2, sticky=tk.W, padx=4, pady=4
    )

    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill=tk.X, pady=12)
    ttk.Button(btn_frame, text="生成图像", command=do_generate).pack(side=tk.LEFT)

    status_var = tk.StringVar(value="请选择包含 PIXEL_DATA 的 .py 文件后点击「生成图像」")
    ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
        side=tk.BOTTOM, fill=tk.X, pady=(0, 0)
    )

    if parent is None:
        root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main_gui()
    else:
        main_cli()
