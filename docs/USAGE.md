# 报告与解码用法

从项目根目录运行，或使用脚本的完整路径从其他目录运行：

```bat
.\setup.cmd
.\run_report.cmd 'D:\captures\mysekai.bin'
.\run_report.cmd 'D:\captures\mysekai.bin' --output '.\output\today' --mode '1+4' --format png --dpi 144
.\run_report.cmd 'D:\captures\mysekai.bin' --output '.\output\full' --mode stitched --format jpg --quality 95 --dpi 300
.\run_decode.cmd 'D:\captures\mysekai.bin'
```

| 参数 | 默认 | 说明 |
|---|---|---|
| `input` | 必填 | 加密响应文件 |
| `--output` | `output/` | 报告输出目录；从批处理入口运行时，相对路径基于项目根目录 |
| `--mode` | `1+1` | `1+1` 总览+四图合览；`1+4` 总览+四张独立地图；`stitched` 单张竖排大图 |
| `--format` | `png` | `png`、`jpg`、`webp` |
| `--dpi` | `144` | 输出图的 DPI 元数据 |
| `--quality` | `95` | JPG/WebP 质量 |
| `--keyset` | `auto` | `auto`、`cn`、`legacy` |

解码中间结果保存在报告目录的 `data/`，原始渲染及报告数据在 `rendered/`。单独运行 `run_decode.cmd` 的结果在 `runtime/decoded/`。

四张站地图固定按 **32:27** 裁剪：从 1920×1080 源图去掉左右各 320 px，输出 **1280×1080**，不再保留标题栏和底部图例。边缘过近的掉落点会跳过，避免图标被裁断。

正式绘图程序在 `src/sekai_toolkit/`；地图背景在 `assets/maps/`，其余图标在 `assets/catalog/`、`assets/library/` 等。素材同步入口是 `sekai_toolkit.assets.sync`；旧版素材探查脚本在 `research/experiments/legacy_asset_tools/`，不参与正式绘图。
