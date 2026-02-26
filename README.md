# 像素画坐标与颜色提取 / 生成工具  
# Pixel Art Coordinate & Color Extractor / Generator

**中文** · 从本地像素画图像提取坐标与颜色为 Python 代码；从代码生成 PNG 图像；将补丁数据按坐标覆盖合并；在图片上标定手/脚位置。支持统一入口启动，各窗口可上下、左右滚动。  
**English** · Extract pixel art to Python code, generate PNG from code, merge patch data, and annotate hand/foot positions. Unified launcher; all tool windows support vertical and horizontal scrolling.

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
| 补丁文件含杂项或语法错误时，可自动提取 `PIXEL_DATA* = { ... }` 块再执行 | If patch file has extra text or syntax errors, extracts and runs only `PIXEL_DATA* = { ... }` blocks |
| 输出格式与提取器一致，可直接给生成器出图 | Output same format as extractor; ready for generator |

### 手/脚位置标定 (pixel_limb_annotator.py) · Limb Annotator

| 中文 | English |
|------|--------|
| 在图片上**点击标定**手部、脚部位置（红=手，蓝=脚） | **Click** on image to mark hand (red) and foot (blue) positions |
| **悬停**时当前像素高亮为对应颜色；**选中**后该像素显示为红/蓝 | **Hover** highlights current pixel; **selected** pixels shown in red/blue |
| **放大/缩小**（按钮或滚轮），图片加载后自动居中 | **Zoom** in/out (buttons or wheel); image centered on load |
| 生成 `HAND_POSITIONS` / `FOOT_POSITIONS` 的 .py | Export .py with `HAND_POSITIONS` / `FOOT_POSITIONS` |
| 与 PIXEL_DATA 同坐标系，便于动画、碰撞等逻辑 | Same coordinate system as PIXEL_DATA; useful for animation, collision, etc. |

### 界面通用 / UI (all tools)

| 中文 | English |
|------|--------|
| 各工具窗口内容可**上下、左右滚动**（窗口小于内容时） | All tool windows support **vertical and horizontal** scrolling when content overflows |
| 滚轮上下滑动；**Shift + 滚轮**左右滑动；也可拖滚动条 | Mouse wheel: vertical scroll; **Shift + wheel**: horizontal; or use scrollbars |

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

### 统一入口 (推荐) / Unified launcher (recommended)

在一个界面中选择要用的功能，点击即可打开对应工具窗口。  
One window to choose which tool to open.

```bash
python pixel_launcher.py
```

启动后会看到四个选项：**提取**、**生成**、**合并**、**手/脚标定**，点击「打开」即打开该功能的窗口。统一入口与各工具窗口均支持内容超出时上下、左右滚动。  
You get four options: Extract, Generate, Merge, Limb annotator; click “打开” to open that tool. Launcher and all tool windows support vertical and horizontal scrolling when content doesn’t fit.

### 单独运行各模块 / Run each module separately

无参数运行即可打开对应界面。  
Run with no arguments to open the GUI.

```bash
python pixel_extractor.py      # 提取 / Extract
python pixel_generator.py      # 生成 / Generate
python pixel_merger.py         # 合并 / Merge
python pixel_limb_annotator.py # 手/脚位置标定 / Limb annotator
```

**提取器**：选图 → 设置输出路径、透明处理、坐标倍数、颜色格式 → 「提取并保存」。  
**Extractor**: Choose image → set output path, transparency, multiplier, color format → “Extract and save”.

**生成器**：选数据 .py → 设输出图像与放大倍数 → 「生成图像」。  
**Generator**: Choose data .py → set output image and scale → “Generate image”.

**合并**：选基础 .py、补丁 .py、补丁变量名 → 「合并并保存」。  
**Merger**: Choose base .py, patch .py, patch variable → “Merge and save”.

**手/脚标定**：加载图片（自动居中）→ 可选「放大/缩小」→ 选「手（红）」或「脚（蓝）」→ 悬停看高亮、点击添加标定点 → 「保存为 .py」。  
**Limb annotator**: Load image (auto-centered) → optionally zoom → choose hand/foot → hover to highlight, click to add → “Save as .py”.

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

#### 手/脚标定 (仅 GUI) / Limb annotator (GUI only)

运行 `python pixel_limb_annotator.py`，加载图片后选择「手」或「脚」，在图上点击标定，最后「保存为 .py」。  
Run `python pixel_limb_annotator.py`, load image, choose hand/foot, click to mark, then “Save as .py”.

保存的 .py 示例 / Saved .py example:

```python
# 手部与脚部标定位置（由 pixel_limb_annotator 生成）
HAND_POSITIONS = [(18, 13), (22, 14), ...]  # 图像坐标
FOOT_POSITIONS = [(20, 36), (24, 37), ...]
```

在代码中可与 `PIXEL_DATA` 一起使用（同坐标系）。  
Use in code together with `PIXEL_DATA` (same coordinate system).

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
├── pixel_launcher.py        # 统一入口  /  Unified launcher
├── pixel_gui_util.py        # 可滚动区域等 GUI 公用  /  Scrollable frame, etc.
├── pixel_extractor.py      # 提取：图像 → .py  /  Extract: image → .py
├── pixel_generator.py      # 生成：.py → 图像  /  Generate: .py → image
├── pixel_merger.py         # 合并：基础 + 补丁 → .py  /  Merge: base + patch → .py
├── pixel_limb_annotator.py # 手/脚位置标定  /  Limb annotator
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
| **窗口内容看不全**：用右侧/底部滚动条或滚轮上下、Shift+滚轮左右滑动。 | **Content doesn’t fit**: Use scrollbars or mouse wheel (vertical); Shift + wheel for horizontal. |
| **合并报错「无法执行数据文件」**：补丁文件须含合法 `PIXEL_DATA` 或 `PIXEL_DATA_* = { ... }` 块；若整文件有语法错误，程序会尝试只提取并执行该块。 | **Merge “cannot exec”**: Patch file must contain valid `PIXEL_DATA* = { ... }`; if the whole file has syntax errors, the tool tries to extract and run only that block. |
