#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixel Data Merger - 将「补丁」数据按坐标覆盖到基础 PIXEL_DATA 上

用于 AI 返回的帧差异格式（如 PIXEL_DATA_FRAME2 = { (x,y): color, ... }）：
选定基础数据和补丁数据后，用补丁中的坐标直接替换基础中对应位置，输出合并后的 PIXEL_DATA 文件。
"""

import argparse
import re
import sys
from pathlib import Path


def _normalize_code(code: str) -> str:
    """兼容 None  # ... 的逗号在注释内导致的语法错误。"""
    return code.replace("None  # ", "None,  # ")


def load_pixel_dict_from_file(
    file_path: str,
    variable_name: str | None = None,
) -> tuple[dict, str]:
    """
    从 Python 文件中加载像素数据字典。
    若 variable_name 为 None，则自动查找 PIXEL_DATA 或 PIXEL_DATA_* 的变量（优先 PIXEL_DATA）。
    返回 (data_dict, actual_variable_name)。
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    with open(path, encoding="utf-8") as f:
        code = f.read()

    code = _normalize_code(code)
    namespace = {}
    try:
        exec(code, namespace)
    except Exception as e:
        raise ValueError(f"无法执行数据文件: {e}") from e

    if variable_name is not None:
        if variable_name not in namespace:
            raise ValueError(f"文件中未找到变量: {variable_name}")
        obj = namespace[variable_name]
        if not isinstance(obj, dict):
            raise ValueError(f"{variable_name} 不是字典类型")
        return obj, variable_name

    # 自动查找：PIXEL_DATA 优先，否则任意 PIXEL_DATA_*
    if "PIXEL_DATA" in namespace and isinstance(namespace["PIXEL_DATA"], dict):
        return namespace["PIXEL_DATA"], "PIXEL_DATA"
    candidates = [
        (k, v) for k, v in namespace.items()
        if isinstance(k, str) and k.startswith("PIXEL_DATA") and isinstance(v, dict)
    ]
    if not candidates:
        raise ValueError(
            "文件中未找到 PIXEL_DATA 或 PIXEL_DATA_* 变量，请用 --var 指定变量名"
        )
    # 按变量名排序，取第一个（可预测）
    name, data = sorted(candidates, key=lambda x: x[0])[0]
    return data, name


def load_base(file_path: str) -> dict:
    """加载基础 PIXEL_DATA（通常为完整帧）。"""
    data, _ = load_pixel_dict_from_file(file_path, "PIXEL_DATA")
    return data


def load_patch(
    file_path: str,
    variable_name: str | None = None,
) -> dict:
    """加载补丁数据（仅包含要覆盖的坐标，如 PIXEL_DATA_FRAME2）。"""
    data, _ = load_pixel_dict_from_file(file_path, variable_name)
    return data


def merge(base: dict, patch: dict) -> dict:
    """将 patch 中的坐标覆盖到 base 上，返回新字典（不修改原 base）。"""
    result = dict(base)
    result.update(patch)
    return result


def _format_value(v) -> str:
    """与提取器一致的输出格式。"""
    if v is None:
        return "None,  # Transparent"
    if isinstance(v, str):
        return repr(v)
    if isinstance(v, tuple):
        return str(v)
    return repr(v)


def _infer_size(pixel_data: dict) -> tuple[int, int]:
    """根据坐标范围推断宽高。"""
    if not pixel_data:
        return 0, 0
    xs = [k[0] for k in pixel_data.keys()]
    ys = [k[1] for k in pixel_data.keys()]
    w = max(xs) - min(xs) + 1
    h = max(ys) - min(ys) + 1
    return w, h


def save_merged(
    output_path: str,
    merged: dict,
    output_var: str = "PIXEL_DATA",
) -> str:
    """将合并后的字典保存为与提取器格式一致的 Python 文件。"""
    w, h = _infer_size(merged)
    lines = [
        f"# Merged pixel data (Size: {w}x{h})",
        f"# Format: {{(x, y): \"Hex Color\"}}",
        f"{output_var} = {{",
    ]
    for (x, y) in sorted(merged.keys(), key=lambda k: (k[1], k[0])):
        v = merged[(x, y)]
        lines.append("    ({}, {}): {},".format(x, y, _format_value(v)))
    lines.append("}")
    code = "\n".join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(code, encoding="utf-8")
    return code


def run_merge(
    base_file: str,
    patch_file: str,
    output_file: str,
    patch_variable: str | None = None,
    output_variable: str = "PIXEL_DATA",
) -> dict:
    """
    执行一次合并：用 patch 覆盖 base 中对应坐标，并保存到 output_file。
    返回合并后的字典。
    """
    base = load_base(base_file)
    patch = load_patch(patch_file, variable_name=patch_variable)
    merged = merge(base, patch)
    save_merged(output_file, merged, output_var=output_variable)
    return merged


def list_pixel_data_variables(file_path: str) -> list[str]:
    """列出文件中所有 PIXEL_DATA / PIXEL_DATA_* 变量名，供 GUI 选择。"""
    path = Path(file_path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        code = _normalize_code(f.read())
    namespace = {}
    try:
        exec(code, namespace)
    except Exception:
        return []
    return sorted(
        k for k, v in namespace.items()
        if isinstance(k, str) and k.startswith("PIXEL_DATA") and isinstance(v, dict)
    )


def main_cli():
    parser = argparse.ArgumentParser(
        description="将补丁 PIXEL_DATA_* 按坐标覆盖到基础 PIXEL_DATA，输出合并文件"
    )
    parser.add_argument("base_file", help="基础数据文件（含 PIXEL_DATA）")
    parser.add_argument("patch_file", help="补丁数据文件（含 PIXEL_DATA_FRAME2 等）")
    parser.add_argument("-o", "--output", default="pixel_data_merged.py", help="输出文件路径")
    parser.add_argument(
        "--var",
        dest="patch_var",
        default=None,
        help="补丁文件中的变量名（如 PIXEL_DATA_FRAME2），不指定则自动检测",
    )
    parser.add_argument(
        "--output-var",
        default="PIXEL_DATA",
        help="输出文件中的变量名，默认 PIXEL_DATA",
    )
    args = parser.parse_args()
    run_merge(
        args.base_file,
        args.patch_file,
        args.output,
        patch_variable=args.patch_var,
        output_variable=args.output_var,
    )
    print(f"已合并并保存: {args.output}")


def main_gui():
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("未找到 tkinter，请使用 CLI。")
        sys.exit(1)

    def choose_base():
        path = filedialog.askopenfilename(
            title="选择基础数据文件（完整 PIXEL_DATA）",
            filetypes=[("Python 文件", "*.py"), ("文本文件", "*.txt")],
        )
        if path:
            entry_base.delete(0, tk.END)
            entry_base.insert(0, path)

    def choose_patch():
        path = filedialog.askopenfilename(
            title="选择补丁数据文件（如含 PIXEL_DATA_FRAME2）",
            filetypes=[("Python 文件", "*.py"), ("文本文件", "*.txt")],
        )
        if path:
            entry_patch.delete(0, tk.END)
            entry_patch.insert(0, path)
            # 刷新补丁变量列表
            vars_list = list_pixel_data_variables(path)
            combo_var["values"] = vars_list
            if vars_list:
                combo_var.set(vars_list[0])

    def choose_output():
        path = filedialog.asksaveasfilename(
            title="保存合并结果",
            defaultextension=".py",
            filetypes=[("Python 文件", "*.py")],
            initialfile="pixel_data_merged.py",
        )
        if path:
            entry_output.delete(0, tk.END)
            entry_output.insert(0, path)

    def do_merge():
        base_path = entry_base.get().strip()
        patch_path = entry_patch.get().strip()
        out_path = entry_output.get().strip() or "pixel_data_merged.py"
        if not base_path:
            messagebox.showerror("错误", "请选择基础数据文件")
            return
        if not patch_path:
            messagebox.showerror("错误", "请选择补丁数据文件")
            return
        patch_var = combo_var.get().strip() or None
        if patch_var == "":
            patch_var = None
        try:
            run_merge(base_path, patch_path, out_path, patch_variable=patch_var)
            status_var.set(f"已合并并保存: {out_path}")
            messagebox.showinfo("完成", f"已合并并保存:\n{out_path}")
        except Exception as e:
            status_var.set("合并失败")
            messagebox.showerror("错误", str(e))

    root = tk.Tk()
    root.title("像素数据合并 - 补丁覆盖基础")
    root.minsize(520, 280)
    root.geometry("580x320")
    root.resizable(True, True)

    main = ttk.Frame(root, padding=16)
    main.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main, text="将补丁中的坐标覆盖到基础 PIXEL_DATA", font=("", 12, "bold")).pack(
        anchor=tk.W, pady=(0, 10)
    )

    frm = ttk.LabelFrame(main, text="文件", padding=10)
    frm.pack(fill=tk.X, pady=(0, 8))

    ttk.Label(frm, text="基础数据", width=12).grid(row=0, column=0, sticky=tk.W, pady=4)
    entry_base = ttk.Entry(frm, width=42)
    entry_base.grid(row=0, column=1, padx=6, pady=4)
    ttk.Button(frm, text="浏览...", command=choose_base).grid(row=0, column=2, pady=4)

    ttk.Label(frm, text="补丁数据", width=12).grid(row=1, column=0, sticky=tk.W, pady=4)
    entry_patch = ttk.Entry(frm, width=42)
    entry_patch.grid(row=1, column=1, padx=6, pady=4)
    ttk.Button(frm, text="浏览...", command=choose_patch).grid(row=1, column=2, pady=4)

    ttk.Label(frm, text="补丁变量", width=12).grid(row=2, column=0, sticky=tk.W, pady=4)
    combo_var = ttk.Combobox(frm, width=28, state="readonly")
    combo_var.grid(row=2, column=1, sticky=tk.W, padx=6, pady=4)
    ttk.Label(frm, text="（如 PIXEL_DATA_FRAME2，选补丁后自动列出）", foreground="gray").grid(
        row=2, column=2, sticky=tk.W, padx=4, pady=4
    )

    ttk.Label(frm, text="输出文件", width=12).grid(row=3, column=0, sticky=tk.W, pady=4)
    entry_output = ttk.Entry(frm, width=42)
    entry_output.insert(0, "pixel_data_merged.py")
    entry_output.grid(row=3, column=1, padx=6, pady=4)
    ttk.Button(frm, text="另存为...", command=choose_output).grid(row=3, column=2, pady=4)

    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill=tk.X, pady=10)
    ttk.Button(btn_frame, text="合并并保存", command=do_merge).pack(side=tk.LEFT)

    status_var = tk.StringVar(value="选择基础数据与补丁数据后点击「合并并保存」")
    ttk.Label(main, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
        side=tk.BOTTOM, fill=tk.X, pady=(8, 0)
    )

    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main_gui()
    else:
        main_cli()
