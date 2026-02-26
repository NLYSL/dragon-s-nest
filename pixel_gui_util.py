#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 通用小工具：可滚动区域等。"""


def make_scrollable(parent, use_global_wheel=True):
    """
    在 parent 内做一个可上下、左右滚动的区域。
    返回 (container, inner_frame)。
    - 垂直：鼠标滚轮上下滑动；右侧纵向滚动条。
    - 水平：Shift + 滚轮 或 底部横向滚动条 左右滑动。
    use_global_wheel: 为 True 时，鼠标在内容区任意位置用滚轮即可滚动；
                      为 False 时仅绑在 canvas/inner 上（适用于内部另有滚轮用途的页面）。
    """
    import tkinter as tk
    from tkinter import ttk

    container = ttk.Frame(parent)
    scrollbar_y = tk.Scrollbar(container)
    scrollbar_x = tk.Scrollbar(container, orient=tk.HORIZONTAL)
    canvas = tk.Canvas(
        container,
        highlightthickness=0,
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set,
    )
    scrollbar_y.config(command=canvas.yview)
    scrollbar_x.config(command=canvas.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    inner = ttk.Frame(canvas)
    wid = canvas.create_window(0, 0, window=inner, anchor=tk.NW)

    def _on_frame_configure(_event=None):
        canvas.config(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        b = canvas.bbox("all")
        w = event.width
        if b is not None:
            w = max(w, b[2] - b[0])
        canvas.itemconfig(wid, width=w)

    def _on_mousewheel(event):
        step = int(-1 * (event.delta / 120))
        if getattr(event, "state", 0) & 0x1:  # Shift 键：横向滚动
            canvas.xview_scroll(step, "units")
        else:
            canvas.yview_scroll(step, "units")

    def _on_mousewheel_global(event):
        w = event.widget
        while w:
            if w == canvas:
                _on_mousewheel(event)
                break
            try:
                w = w.master
            except AttributeError:
                break

    inner.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)
    canvas.bind("<MouseWheel>", _on_mousewheel)
    inner.bind("<MouseWheel>", _on_mousewheel)
    if use_global_wheel:
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel_global))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    return container, inner
