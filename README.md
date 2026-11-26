# MySekai 地图报告与 QQBot

解码国服 MySekai 响应文件，生成掉落总览与四张带背景的地图；也可以通过 OneBot v11 反向 WebSocket 让 QQ 群文件触发绘图。四张站地图固定按 32:27 裁剪为 1280×1080，去掉外围无关区域和标题/图例。

## 快速开始

首次从 Git 拉下来后：

```bat
git lfs install
git lfs pull
```

然后双击 `run.cmd`，选择「1. Setup environment」；或运行：

```bat
.\setup.cmd
```

它会自动找到 Python 3.10+、创建 `.venv`、安装 `requirements.lock.txt` 里的依赖，并验证导入。

之后常用命令：

```bat
.\run.cmd report 'D:\captures\response.com_mysekai'
.\run.cmd decode 'D:\captures\response.com_mysekai'
.\run.cmd start
```

要传完整报告参数时，直接调用实现脚本：

```bat
.\run_report.cmd 'D:\captures\response.com_mysekai' --mode '1+4' --output '.\output\today'
```

`run.cmd` 是统一的菜单/命令行入口，其余实现也都是 `.cmd`。

OneBot v11 反向 WebSocket 地址：`ws://127.0.0.1:8765/onebot/v11/ws`，NapCat、OpenQQ 等客户端通用，无需选择适配器。默认仅监听本机，默认不要求令牌。各群用 `烤森解析回复模式 群组/私聊` 设置回复方式、用 `自动撤回用户烤森抓包消息 开启/关闭` 设置文件消息撤回；`help` 查看帮助；`状态` 会区分并显示当前协议端（如 NapCat、OpenQQ）。指令支持 `/`、`\` 或无前缀，也支持 `@机器人` 触发。

## 根目录入口

| 文件 | 用途 |
|---|---|
| `run.cmd` | 唯一菜单入口：`setup` / `start` / `report` / `decode` / `clean` |
| `setup.cmd` | 创建 `.venv`、安装锁定依赖、验证环境 |
| `start_qqbot.cmd` | 启动 OneBot v11 QQBot（缺少 `.venv` 时会先安装） |
| `run_report.cmd` | 解码抓包并生成报告，支持完整参数 |
| `run_decode.cmd` | 只解码，不绘图 |
| `clean_cache.cmd` | 清理临时缓存；默认也清 `runtime/jobs` 和 `output` |
| `requirements.lock.txt` | 锁定版本，`setup.cmd` 按它安装 |
| `pyproject.toml` | Python 包元数据与依赖范围，供 `pip install -e .` 使用 |
| `.gitattributes` | Git LFS 图片规则 |
| `.gitignore` | 运行数据、缓存、私有配置的忽略规则 |

`run.cmd` 用法：

```text
run.cmd             打开菜单
run.cmd setup       创建 .venv
run.cmd start       启动 QQBot
run.cmd report FILE 生成报告
run.cmd decode FILE 只解码
run.cmd clean       清理缓存
```

默认报告输出在 `output/`，Bot 任务在 `runtime/jobs/`，各群设置在 `runtime/state/group_settings.sqlite3`。项目搬到别的目录后，重新执行 `setup.cmd`，再重启 Bot；如果协议端依赖本地图片文件读取，也要确保它能访问搬迁后的项目目录。

详细用法：[报告参数](docs/USAGE.md)、[QQBot 接入](docs/QQBOT.md)、[工程结构](docs/ARCHITECTURE.md)、[迁移记录](docs/REFACTOR_PLAN.md)。

> 微信小程序已拆分为独立项目，不在本仓库中维护。

## 清理缓存

双击 `run.cmd` 选「5. Clean cache」，或命令行运行：

```bat
.\clean_cache.cmd -DryRun          # 只查看会删除什么
.\clean_cache.cmd                  # 清理临时缓存（默认）
.\clean_cache.cmd -Yes             # 不询问，直接清理
```

默认清理 `runtime/temp`、`runtime/cache`、`runtime/decoded`、`runtime/jobs`、`output`、`runtime/mp-debug*`、`__pycache__` 和 `.pytest_cache`，不会动 `runtime/state`、`assets`、`masterdata`、`samples` 或小程序目录。

`runtime/jobs` 里是 Bot 上传的抓包和历史结果，`output` 里是已生成的报告图片；两者默认都会清空。需要保留时加 `-KeepJobs` / `-KeepOutput`。建议清理前先停 Bot。

可选：

```bat
.\clean_cache.cmd -KeepJobs        # 保留 runtime/jobs 上传文件和历史任务
.\clean_cache.cmd -KeepOutput      # 保留 output 里已生成的报告
.\clean_cache.cmd -IncludeLogs     # 清空 logs
.\clean_cache.cmd -IncludeResearch # 删除 runtime 下的 OpenQQ/LLOneBot/milky/NapCatQQ 研究克隆
```

`output` 和 `runtime/jobs` 都可以重新生成；脚本会先列出清理目标并确认。

## Git 与素材

`output/`、`runtime/`、`logs/`、`.venv/` 和生成缓存已经在 `.gitignore` 中，不会进入版本库。

`assets/` 下的图片由 **Git LFS** 管理：

- `.gitattributes` 里的 `filter=lfs` 规则告诉 Git：这些图片不要直接存进普通 Git 对象，而是存 LFS 指针，实际内容进 `.git/lfs/`
- 克隆仓库时必须安装 Git LFS 并执行 `git lfs pull`，否则拿到的只是指针文件
- 推送远程前要确认远程支持 LFS 且有配额；GitHub 的 LFS 免费额度有限
- 如果只想把项目拷到另一台电脑，直接复制包含 `.git/lfs` 的整个目录即可；如果重新 clone，记得 `git lfs pull`

`runtime/`、`output/`、`logs/`、`.venv/` 和解密样本不进入版本库。首次提交只在本地创建，不设置远程地址。

