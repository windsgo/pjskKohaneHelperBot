# 工程结构

- `src/sekai_toolkit/decoder`：解密和 MessagePack 解码。
- `src/sekai_toolkit/report`：总览及四张地图绘制。
- `src/sekai_toolkit/assets`：素材同步；正式素材在根目录 `assets/`，主数据在 `masterdata/`。
- `src/sekai_toolkit/bot`：OneBot v11 接入和任务处理。Bot 调用同一报告入口。
- `src/sekai_toolkit/common/paths.py`：以源码位置定位工程根目录，避免依赖启动时的当前目录。
- `scripts/asset_tools`：解码结果提取辅助脚本；`research/`：历史素材探索、旧补丁、外部源码和快照，不参与正式运行。
- `runtime/jobs`：Bot 任务；`runtime/state`：持久化回复设置；`runtime/decoded`：手动解码结果；`runtime/temp`：测试产物。
- `output/`：用户指定或默认生成的正式报告；`logs/`：运行日志预留目录。

根目录保留 `run.cmd` 作为唯一菜单/命令入口，具体实现为 `setup.cmd`、`start_qqbot.cmd`、`run_report.cmd`、`run_decode.cmd` 和 `clean_cache.cmd`。复制项目到新位置后运行 `.\run.cmd setup` 检查或重建 Python 环境。正在运行的 Bot 需要重启，才会加载新路径。

本轮只迁移正式模块，没有把既有绘图和 Bot 的大文件按功能继续拆成多个子模块，以免改变已经验证的行为。历史研究脚本按用途归档，未逐个转换为正式 CLI；需要重新运行时应先核对其中旧路径。

各群的回复与自动撤回设置保存在 `runtime/state/group_settings.sqlite3`。运行参数以命令行参数为准，不再维护单独的 `config/default.toml`。
