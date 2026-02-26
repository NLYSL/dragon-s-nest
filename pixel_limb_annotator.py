#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixel Limb Annotator - 在图片上标定手与脚的位置

图形化界面中加载像素画图片，用点击标定手部、脚部位置，将结果保存为 Python 数据
（HAND_POSITIONS / FOOT_POSITIONS），便于在生成的数据中引用。
"""

import sys
from pathlib import Path

from PIL import Image, ImageTk

# 与提取器一致的格式支持
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")
# 显示时最大边长（像素），超出则缩放
MAX_DISPLAY_SIZE = 520
# 缩放倍率范围与步进（放大上限提高便于精确标定）
ZOOM_MIN, ZOOM_MAX = 0.25, 16.0
ZOOM_STEP = 1.25
# 悬停/选中时单像素高亮颜色（手红脚蓝）
COLOR_HAND = "#E53935"
COLOR_FOOT = "#1E88E5"


def load_image(path: str) -> Image.Image:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"不支持的格式，支持: {', '.join(SUPPORTED_EXTENSIONS)}")
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def save_limb_positions(
    output_path: str,
    hand_positions: list[tuple[int, int]],
    foot_positions: list[tuple[int, int]],
    image_size: tuple[int, int] | None = None,
) -> str:
    """将手、脚位置保存为 Python 文件，便于在生成数据中引用。"""
    lines = [
        "# 手部与脚部标定位置（由 pixel_limb_annotator 生成）",
        "# 可与 PIXEL_DATA 配合使用，用于动画、碰撞等逻辑。",
        "",
    ]
    if image_size:
        lines.append(f"# 标定时的图像尺寸: {image_size[0]}x{image_size[1]}")
        lines.append("")
    lines.append("# 手部位置（图像坐标，左上为 (0,0)）")
    lines.append("HAND_POSITIONS = " + repr(hand_positions))
    lines.append("")
    lines.append("# 脚部位置（图像坐标）")
    lines.append("FOOT_POSITIONS = " + repr(foot_positions))
    lines.append("")
    code = "\n".join(lines)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(code, encoding="utf-8")
    return code


def main_gui(parent=None):
    """parent 不为 None 时在 Toplevel 中打开（供统一启动器调用）。"""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("需要 tkinter，请使用带 GUI 的 Python 环境。")
        sys.exit(1)

    hand_positions: list[tuple[int, int]] = []
    foot_positions: list[tuple[int, int]] = []
    img: Image.Image | None = None
    base_scale = 1.0   # 加载时使图像适应窗口的基准比例
    zoom_factor = 1.0  # 用户放大/缩小倍率
    photo: ImageTk.PhotoImage | None = None
    canvas_img_id = None
    marker_ids: list[int] = []
    origin_x, origin_y = 0, 0  # 图像在画布上的左上角，用于居中
    hover_rect_id = None  # 悬停时高亮的那一像素矩形

    def get_display_scale() -> float:
        return base_scale * zoom_factor

    def refresh_display():
        """根据当前 base_scale * zoom_factor 重绘画布上的图像与标定点，并保持图片居中。"""
        nonlocal photo, canvas_img_id, origin_x, origin_y
        if img is None:
            return
        w, h = img.size
        scale = base_scale * zoom_factor
        disp_w = max(1, int(w * scale))
        disp_h = max(1, int(h * scale))
        disp = img.resize((disp_w, disp_h), Image.NEAREST)
        photo = ImageTk.PhotoImage(disp)
        cvs.update_idletasks()
        cvs_w = max(1, cvs.winfo_width())
        cvs_h = max(1, cvs.winfo_height())
        # 图像居中：若显示尺寸小于画布，则留白居中
        origin_x = max(0, (cvs_w - disp_w) // 2)
        origin_y = max(0, (cvs_h - disp_h) // 2)
        total_w = max(cvs_w, origin_x + disp_w)
        total_h = max(cvs_h, origin_y + disp_h)
        if canvas_img_id is not None:
            cvs.delete(canvas_img_id)
        canvas_img_id = cvs.create_image(origin_x, origin_y, anchor=tk.NW, image=photo)
        cvs._photo = photo
        cvs.config(scrollregion=(0, 0, total_w, total_h))
        # 图像大于画布时，滚动到视口居中
        if total_w > cvs_w:
            cvs.xview_moveto(max(0, (1 - cvs_w / total_w) / 2))
        if total_h > cvs_h:
            cvs.yview_moveto(max(0, (1 - cvs_h / total_h) / 2))
        redraw_markers()
        clear_hover()

    def canvas_to_image(cx: int, cy: int) -> tuple[int, int] | None:
        """将画布坐标（含滚动）转为图像像素坐标，若在图像外返回 None。"""
        if img is None:
            return None
        real_cx = cvs.canvasx(cx)
        real_cy = cvs.canvasy(cy)
        scale = base_scale * zoom_factor
        ix = int(round((real_cx - origin_x) / scale))
        iy = int(round((real_cy - origin_y) / scale))
        w, h = img.size
        if ix < 0 or ix >= w or iy < 0 or iy >= h:
            return None
        return ix, iy

    def image_to_canvas(ix: int, iy: int) -> tuple[int, int, int, int]:
        """返回该像素在画布上的矩形 (x1, y1, x2, y2)。"""
        scale = base_scale * zoom_factor
        x1 = origin_x + int(ix * scale)
        y1 = origin_y + int(iy * scale)
        x2 = origin_x + int((ix + 1) * scale)
        y2 = origin_y + int((iy + 1) * scale)
        return x1, y1, x2, y2

    def clear_hover():
        nonlocal hover_rect_id
        if hover_rect_id is not None:
            try:
                cvs.delete(hover_rect_id)
            except Exception:
                pass
            hover_rect_id = None

    def redraw_markers():
        nonlocal marker_ids
        for mid in marker_ids:
            try:
                cvs.delete(mid)
            except Exception:
                pass
        marker_ids.clear()
        if img is None:
            return
        # 选中的像素画成对应颜色的实心矩形（手红脚蓝）
        for (ix, iy) in hand_positions:
            x1, y1, x2, y2 = image_to_canvas(ix, iy)
            marker_ids.append(cvs.create_rectangle(x1, y1, x2, y2, outline=COLOR_HAND, fill=COLOR_HAND, width=1))
        for (ix, iy) in foot_positions:
            x1, y1, x2, y2 = image_to_canvas(ix, iy)
            marker_ids.append(cvs.create_rectangle(x1, y1, x2, y2, outline=COLOR_FOOT, fill=COLOR_FOOT, width=1))

    def load_img():
        nonlocal img, base_scale, zoom_factor, photo, canvas_img_id
        path = filedialog.askopenfilename(
            title="选择像素画图像",
            filetypes=[
                ("PNG / JPEG / BMP", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
            ],
        )
        if not path:
            return
        try:
            img = load_image(path)
        except Exception as e:
            messagebox.showerror("错误", str(e))
            return
        hand_positions.clear()
        foot_positions.clear()
        w, h = img.size
        base_scale = min(MAX_DISPLAY_SIZE / w, MAX_DISPLAY_SIZE / h, 1.0)
        zoom_factor = 1.0
        refresh_display()
        update_list_display()
        status_var.set(f"已加载: {Path(path).name}，可放大/缩小后点击标定")

    def zoom_in():
        nonlocal zoom_factor
        if img is None:
            return
        zoom_factor = min(ZOOM_MAX, zoom_factor * ZOOM_STEP)
        refresh_display()
        status_var.set(f"放大 {zoom_factor * 100:.0f}%")

    def zoom_out():
        nonlocal zoom_factor
        if img is None:
            return
        zoom_factor = max(ZOOM_MIN, zoom_factor / ZOOM_STEP)
        refresh_display()
        status_var.set(f"缩小 {zoom_factor * 100:.0f}%")

    def on_canvas_click(event):
        if img is None:
            return
        pt = canvas_to_image(event.x, event.y)
        if pt is None:
            return
        ix, iy = pt
        if mode_var.get() == "hand":
            hand_positions.append((ix, iy))
        else:
            foot_positions.append((ix, iy))
        redraw_markers()
        update_list_display()

    def on_canvas_motion(event):
        """悬停时当前像素高亮为对应颜色（手红脚蓝）。"""
        nonlocal hover_rect_id
        if img is None:
            clear_hover()
            return
        pt = canvas_to_image(event.x, event.y)
        clear_hover()
        if pt is None:
            return
        ix, iy = pt
        x1, y1, x2, y2 = image_to_canvas(ix, iy)
        color = COLOR_HAND if mode_var.get() == "hand" else COLOR_FOOT
        hover_rect_id = cvs.create_rectangle(x1, y1, x2, y2, outline=color, fill=color, width=1)
        cvs.tag_raise(hover_rect_id)

    def update_list_display():
        hand_txt = ", ".join(f"({x},{y})" for (x, y) in hand_positions) or "（未标定）"
        foot_txt = ", ".join(f"({x},{y})" for (x, y) in foot_positions) or "（未标定）"
        lbl_hand_list.config(text="手: " + hand_txt)
        lbl_foot_list.config(text="脚: " + foot_txt)

    def undo_hand():
        if hand_positions:
            hand_positions.pop()
            redraw_markers()
            update_list_display()

    def undo_foot():
        if foot_positions:
            foot_positions.pop()
            redraw_markers()
            update_list_display()

    def clear_all():
        hand_positions.clear()
        foot_positions.clear()
        redraw_markers()
        update_list_display()
        status_var.set("已清空所有标定")

    def save_file():
        path = filedialog.asksaveasfilename(
            title="保存手/脚位置数据",
            defaultextension=".py",
            filetypes=[("Python 文件", "*.py")],
            initialfile="limb_positions.py",
        )
        if not path:
            return
        try:
            size = img.size if img else None
            save_limb_positions(path, hand_positions, foot_positions, image_size=size)
            status_var.set(f"已保存: {path}")
            messagebox.showinfo("完成", f"已保存:\n{path}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    from pixel_gui_util import make_scrollable

    root = tk.Toplevel(parent) if parent else tk.Tk()
    root.title("手/脚位置标定 - Pixel Limb Annotator")
    root.minsize(640, 520)
    root.geometry("720x580")

    scroll_container, content = make_scrollable(root, use_global_wheel=False)  # 保留图片区滚轮缩放
    scroll_container.pack(fill=tk.BOTH, expand=True)

    top = ttk.Frame(content, padding=10)
    top.pack(fill=tk.X)
    ttk.Button(top, text="加载图片...", command=load_img).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Label(top, text="标定模式:").pack(side=tk.LEFT, padx=(8, 4))
    mode_var = tk.StringVar(value="hand")
    ttk.Radiobutton(top, text="手（红）", variable=mode_var, value="hand").pack(side=tk.LEFT)
    ttk.Radiobutton(top, text="脚（蓝）", variable=mode_var, value="foot").pack(side=tk.LEFT, padx=(0, 12))
    ttk.Button(top, text="放大", command=zoom_in).pack(side=tk.LEFT, padx=(0, 2))
    ttk.Button(top, text="缩小", command=zoom_out).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(top, text="撤销上一个手", command=undo_hand).pack(side=tk.LEFT, padx=(0, 4))
    ttk.Button(top, text="撤销上一个脚", command=undo_foot).pack(side=tk.LEFT, padx=(0, 4))
    ttk.Button(top, text="清空全部", command=clear_all).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(top, text="保存为 .py...", command=save_file).pack(side=tk.LEFT)

    list_frm = ttk.Frame(content, padding=(10, 0))
    list_frm.pack(fill=tk.X)
    lbl_hand_list = ttk.Label(list_frm, text="手: （未标定）", wraplength=600)
    lbl_hand_list.pack(anchor=tk.W)
    lbl_foot_list = ttk.Label(list_frm, text="脚: （未标定）", wraplength=600)
    lbl_foot_list.pack(anchor=tk.W)

    cvs_frm = ttk.Frame(content, padding=10)
    cvs_frm.pack(fill=tk.BOTH, expand=True)
    # 画布 + 横向/纵向滚动条，放大后可拖动查看
    scroll_y = tk.Scrollbar(cvs_frm)
    scroll_x = tk.Scrollbar(cvs_frm, orient=tk.HORIZONTAL)
    cvs = tk.Canvas(cvs_frm, highlightthickness=0, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.config(command=cvs.yview)
    scroll_x.config(command=cvs.xview)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    cvs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    cvs.bind("<Button-1>", on_canvas_click)
    cvs.bind("<Motion>", on_canvas_motion)
    cvs.bind("<Leave>", lambda e: clear_hover())
    # 鼠标滚轮缩放
    def on_wheel(event):
        if img is None:
            return
        if event.delta > 0:
            zoom_in()
        else:
            zoom_out()
    cvs.bind("<MouseWheel>", on_wheel)

    status_var = tk.StringVar(value="请先点击「加载图片」选择像素画图像，再选择「手」或「脚」后在图上点击标定。")
    ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    if parent is None:
        root.mainloop()


if __name__ == "__main__":
    main_gui()
