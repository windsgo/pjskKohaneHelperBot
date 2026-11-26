# 本轮迁移记录

- 将解码、报告、素材同步和 Bot 主程序移至 `src/sekai_toolkit/`。
- 将测试移至 `tests/`，文档移至 `docs/`，历史脚本和外部参考移至 `research/`。
- 将四张运行时地图背景放入 `assets/maps/`，原有素材目录其余层级不变。
- 将 `bot_jobs/` 归入 `runtime/jobs/`，把回复设置独立放到 `runtime/state/`；旧任务与输出原样保留。
- 去除对 `vendor/` 与本机固定 Python 路径的运行依赖。
- 将不能直接按新目录运行的旧素材探查脚本归档到 `research/experiments/legacy_asset_tools/`；正式素材同步入口保留在 `src/sekai_toolkit/assets/sync.py`。

验证：原始示例通过 `run_report.cmd --mode 1+4` 生成五张 PNG；`tests/test_reply_mode.py` 通过。
