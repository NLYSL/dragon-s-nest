#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
像素画工具集 - 统一入口

在一个界面中选择要使用的功能：提取、生成、合并、手/脚标定。
"""

import sys
from pathlib import Path


def main():
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("需要 tkinter。请使用: python pixel_extractor.py / pixel_generator.py 等单独运行各功能。")
        sys.exit(1)

    def run_extractor():
        from pixel_extractor import main_gui as extractor_gui
        extractor_gui(parent=root)

    def run_generator():
        from pixel_generator import main_gui as generator_gui
        generator_gui(parent=root)

    def run_merger():
        from pixel_merger import main_gui as merger_gui
        merger_gui(parent=root)

    def run_limb_annotator():
        from pixel_limb_annotator import main_gui as limb_gui
        limb_gui(parent=root)

    from pixel_gui_util import make_scrollable

    root = tk.Tk()
    root.title("像素画工具集 / Pixel Art Tools")
    root.minsize(420, 380)
    root.geometry("480x420")
    root.resizable(True, True)

    scroll_container, main = make_scrollable(root)
    scroll_container.pack(fill=tk.BOTH, expand=True)
    main.configure(padding=24)

    title = ttk.Label(main, text="像素画工具集", font=("", 18, "bold"))
    title.pack(pady=(0, 8))
    subtitle = ttk.Label(main, text="选择要使用的功能", foreground="gray")
    subtitle.pack(pady=(0, 24))

    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill=tk.BOTH, expand=True)

    tools = [
        ("提取：图像 → 代码", "从像素画图像提取坐标与颜色，输出 PIXEL_DATA .py", run_extractor),
        ("生成：代码 → 图像", "从 PIXEL_DATA .py 生成 PNG 像素画", run_generator),
        ("合并：基础 + 补丁", "将补丁数据按坐标覆盖到基础 PIXEL_DATA", run_merger),
        ("手/脚标定", "在图片上标定手、脚位置，输出 HAND_POSITIONS / FOOT_POSITIONS", run_limb_annotator),
    ]

    for i, (name, desc, cmd) in enumerate(tools):
        frm = ttk.LabelFrame(btn_frame, text=name, padding=12)
        frm.pack(fill=tk.X, pady=6)
        ttk.Label(frm, text=desc, foreground="gray", wraplength=380).pack(anchor=tk.W)
        ttk.Button(frm, text="打开", command=cmd).pack(anchor=tk.W, pady=(8, 0))

    ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12)
    hint = ttk.Label(main, text="也可在终端单独运行: python pixel_extractor.py / pixel_generator.py / pixel_merger.py / pixel_limb_annotator.py", font=("", 9), foreground="gray", wraplength=420)
    hint.pack(anchor=tk.W)

    root.mainloop()


if __name__ == "__main__":
    # 确保从项目目录加载各模块
    project_dir = Path(__file__).resolve().parent
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))
    main()
