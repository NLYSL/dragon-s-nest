# 像素画坐标与颜色提取 / 生成工具  
# Pixel Art Coordinate & Color Extractor / Generator

**中文** · 从本地像素画图像提取坐标与颜色为 Python 代码；从代码生成 PNG 图像；将补丁数据按坐标覆盖合并。  
**English** · Extract pixel art to Python code, generate PNG from code, and merge patch data by coordinate overlay.

---

## 功能特点 / Features

### 提取工具 (pixel_extractor.py) · Extractor

| 中文 | English |
|------|--------|
| **图形化界面 (GUI)**：选图、设置选项、一键生成数据文件 | **GUI**: Select image, set options, export data file in one click |
| **命令行 (CLI)**：支持脚本与批量处理 | **CLI**: Scriptable and batch-friendly |
| **多格式**：优先 PNG（透明），兼容 JPG、BMP | **Formats**: PNG (with alpha), JPG, BMP |
| **透明**：记为 `None` 或跳过 | **Transparency**: Mark as `None` or skip |
| **坐标系**：原点左上 (0,0)，可设坐标倍数 | **Coordinates**: Origin top-left, optional multiplier |
| **颜色**：十六进制 `#RRGGBB` 或 RGB 元组 | **Colors**: Hex `#RRGGBB` or RGB tuple |
| **输出**：`PIXEL_DATA = {(x, y): color, ...}` | **Output**: `PIXEL_DATA = {(x, y): color, ...}` |

### 生成工具 (pixel_generator.py) · Generator

| 中文 | English |
|------|--------|
| 从 `PIXEL_DATA` 的 .py 生成 PNG 像素画 | Generate PNG from .py files containing `PIXEL_DATA` |
| 支持透明（`None` / `# Transparent`） | Supports transparency (`None` / `# Transparent`) |
| 支持 `#RRGGBB`、`#RGB`、`(r,g,b)`、`(r,g,b,a)` | Supports `#RRGGBB`, `#RGB`, `(r,g,b)`, `(r,g,b,a)` |
| 可设放大倍数（每逻辑像素 N×N 显示） | Optional scale (each logical pixel as N×N) |
| GUI + CLI | GUI + CLI |

### 合并工具 (pixel_merger.py) · Merger

| 中文 | English |
|------|--------|
| 基础 `PIXEL_DATA` + 补丁（如 `PIXEL_DATA_FRAME2`）→ 合并后的 .py | Base `PIXEL_DATA` + patch (e.g. `PIXEL_DATA_FRAME2`) → merged .py |
| 支持「只含变化坐标」的 AI 输出，变量名可自动识别或 `--var` 指定 | Works with AI-style “changed coords only” patches; auto-detect or `--var` |
| 输出格式与提取器一致，可直接给生成器出图 | Output same format as extractor; ready for generator |

---

## 环境要求 / Requirements

- **Python** 3.10+
- **Pillow (PIL)**
- **tkinter**（多随 Python 安装，用于 GUI / usually bundled with Python for GUI）

---

## 安装 / Installation

```bash
cd pixel
pip install -r requirements.txt
```

---

## 使用说明 / Usage

### 图形化界面 (推荐) / GUI (recommended)

无参数运行即可打开界面。  
Run with no arguments to open the GUI.

```bash
python pixel_extractor.py   # 提取 / Extract
python pixel_generator.py   # 生成 / Generate
python pixel_merger.py     # 合并 / Merge
```

**提取器**：选图 → 设置输出路径、透明处理、坐标倍数、颜色格式 → 「提取并保存」。  
**Extractor**: Choose image → set output path, transparency, multiplier, color format → “Extract and save”.

**生成器**：选数据 .py → 设输出图像与放大倍数 → 「生成图像」。  
**Generator**: Choose data .py → set output image and scale → “Generate image”.

**合并**：选基础 .py、补丁 .py、补丁变量名 → 「合并并保存」。  
**Merger**: Choose base .py, patch .py, patch variable → “Merge and save”.

---

### 命令行 / CLI

#### 提取 / Extract

```bash
python pixel_extractor.py image.png                    # 输出 pixel_data.py
python pixel_extractor.py image.png -o out.py --transparent skip --multiplier 2 --format rgb
```

| 参数 / Arg | 中文 | English |
|------------|------|--------|
| `image` | 输入图像（必填） | Input image (required) |
| `-o, --output` | 输出路径，默认 `pixel_data.py` | Output path, default `pixel_data.py` |
| `--transparent` | `mark_none` 或 `skip` | `mark_none` or `skip` |
| `--multiplier` | 坐标倍数 | Coordinate multiplier |
| `--format` | `hex` 或 `rgb` | `hex` or `rgb` |

#### 生成 / Generate

```bash
python pixel_generator.py pixel_data.py -o pixel_art.png --scale 2
```

| 参数 / Arg | 中文 | English |
|------------|------|--------|
| `data_file` | 含 `PIXEL_DATA` 的 .py（必填） | .py with `PIXEL_DATA` (required) |
| `-o, --output` | 输出图像，默认 `pixel_art.png` | Output image, default `pixel_art.png` |
| `--scale` | 像素放大倍数 | Pixel scale factor |

#### 合并 / Merge

```bash
python pixel_merger.py base.py patch.py -o merged.py
python pixel_merger.py base.py patch.py -o merged.py --var PIXEL_DATA_FRAME2
```

| 参数 / Arg | 中文 | English |
|------------|------|--------|
| `base_file` | 基础数据（须含 `PIXEL_DATA`） | Base file (must contain `PIXEL_DATA`) |
| `patch_file` | 补丁文件（含 `PIXEL_DATA_FRAME2` 等） | Patch file (e.g. `PIXEL_DATA_FRAME2`) |
| `-o, --output` | 输出 .py，默认 `pixel_data_merged.py` | Output .py, default `pixel_data_merged.py` |
| `--var` | 补丁变量名，不填则自动检测 | Patch variable name; auto-detect if omitted |
| `--output-var` | 输出变量名，默认 `PIXEL_DATA` | Output variable name, default `PIXEL_DATA` |

---

## 输出示例 / Output Example

生成的 Python 格式 / Generated Python format:

```python
# Auto-generated pixel data (Size: 32x32)
# Format: {(x, y): "Hex Color"}
PIXEL_DATA = {
    (0, 0): '#FFFFFF',
    (1, 0): '#000000',
    (2, 0): None,  # Transparent
    (0, 1): '#FF0000',
    # ...
}
```

在代码中使用 / Use in code:

```python
from pixel_data import PIXEL_DATA

for (x, y), color in PIXEL_DATA.items():
    if color is not None:
        print(f"({x}, {y}) -> {color}")
```

---

## 项目结构 / Project Structure

```
pixel/
├── pixel_extractor.py   # 提取：图像 → .py  /  Extract: image → .py
├── pixel_generator.py   # 生成：.py → 图像  /  Generate: .py → image
├── pixel_merger.py      # 合并：基础 + 补丁 → .py  /  Merge: base + patch → .py
├── requirements.txt
└── README.md
```

---

## 技术栈 / Tech Stack

- **Python** · Pillow (PIL) · tkinter

---

## 常见问题 / FAQ

| 中文 | English |
|------|--------|
| **没有弹出窗口**：无 tkinter 时用 CLI：`python pixel_extractor.py 图.png -o pixel_data.py` | **No window**: Use CLI if tkinter missing: `python pixel_extractor.py image.png -o pixel_data.py` |
| **大图较慢**：像素多时提取/写入会慢，属正常 | **Large images**: Extraction/write can be slow; normal. |
| **透明**：仅 PNG 支持透明；JPG/BMP 无透明通道 | **Transparency**: Only PNG has alpha; JPG/BMP have no transparency. |
| **「跳过」透明**：生成的数据不含透明像素，用生成器出图时画布按实际坐标范围计算，可能比原图小；要保留原尺寸请选「记为 None」。 | **“Skip” transparent**: Output has no transparent pixels; regenerated image size is from key range (may be smaller). Use “Mark as None” to keep full canvas. |
