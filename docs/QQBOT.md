# OneBot v11 QQBot

在 OneBot v11 客户端中设置反向 WebSocket：`ws://127.0.0.1:8765/onebot/v11/ws`。双击项目根目录的 `run.cmd`，选「2. Start QQBot」即可启动；若缺少 `.venv`，启动脚本会先运行环境安装。也可以在命令提示符中启动：

```bat
.\setup.cmd
.\start_qqbot.cmd
```

默认本机监听 8765 端口，不要求令牌。非本机监听必须配置令牌。可用 `start_qqbot.cmd --help` 查看全部参数，常用参数包括 `--host`、`--port`、`--token`、`--groups`、`--users`、`--file-cache`、`--max-mb` 和 `--output`。设置服务后重启程序；Ctrl+C 可停止。

连接 OneBot v11 协议端（NapCat、OpenQQ 等）后，Bot 默认每 5 分钟向群 `2151080494` 发送一条简要报告，包含协议端名称、在线状态、运行状态及 Bot 与协议端的连续连接时间。首次报告在连接 5 分钟后发送。可用 `--heartbeat-group 其他群号` 修改群，`--heartbeat-minutes 10` 修改间隔，或用 `--heartbeat-group 0` 关闭。示例：`.\start_qqbot.cmd --heartbeat-group 2151080494 --heartbeat-minutes 5`。连接断开或报告发送失败会写入本地日志；协议端掉线后无法通过这条 QQ 连接发送掉线通知，群里不再出现定期报告可作为异常提示。

群成员上传名称以 `[数字] response_mkcn` 开头的 MySekai 文件后，Bot 会先回复“已收到烤森抓包文件，正在解析，请稍候。”，然后再开始下载和绘图。默认在群里用一条消息发送总览和四张地图。各群可分别设置回复方式：`烤森解析回复模式 私聊` 为私聊上传者并逐张发送五张图，`烤森解析回复模式 群组` 为群发；`烤森解析回复模式 查询` 查看本群设置。群内任何成员均可修改。发送 `help` 查看总帮助和[抓包教程](https://upload.sakura-bot.cn/about)。

私聊上传的抓包解析完成后，除了私聊发送五张图，还会默认在上报群（`--heartbeat-group`，默认 `2151080494`）提醒一次。可用 `--notify-group <群号>` 指定其他提醒群，或用 `--notify-group 0` 关闭提醒。

全局群聊烤森解码默认开启。只有 QQ `1245784195` 可发送 `烤森群抓包解析 关闭` 或 `烤森群抓包解析 开启` 修改；任何人可用 `烤森群抓包解析 查询` 查看。关闭后不再接收群聊烤森文件任务，已排队但尚未开始的任务也会跳过；私聊文件和其他命令不受影响。设置保存在 `runtime/state/group_settings.sqlite3`，重启后仍生效。

Bot 统一使用 OneBot v11 通用接口，无需选择适配器，也没有 `--adapter` 参数。私聊文件统一调用标准的 `get_file`：NapCat 与 OpenQQ 都支持；`get_private_file_url` 只是部分实现的扩展，仅作最后兜底。`get_file` 会优先使用协议端事件里给出的 `file` 标识（OpenQQ 是文件名，NapCat 是编码 ID），再退回 `file_id`；群聊的 `get_file` 兜底会携带 `group_id`。如果事件自带本地路径则直接读取。

群聊文件先通过 `get_group_file_url` 获取地址：先发 `group_id + file_id + busid`，失败时补上事件里的 `file`/文件名再试，最后才用 `get_file`。OpenQQ 新版本已修复群文件下载接口；如果仍拿不到地址，先确认 OpenQQ 已更新，并查看 Bot 日志里每个 API 的 retcode。调用失败时 Bot 会直接告知用户解析未开始，不影响其他功能。

命令可以带 `/`、`\` 或不带前缀；群聊中 `@机器人` 也可以触发。发送 `help` 或 `/help` 查看总帮助；每个指令后加 `help` 或 `-help` 查看单独帮助，例如 `火 help`、`转换器 -help`。参数错误时 Bot 会回复对应指令的帮助。

发送 `状态` 会调用通用 OneBot `get_status` 与 `get_version_info`，并自动区分协议端：NapCat 显示「NapCat 信息」，OpenQQ 显示「OpenQQ 信息」，其他实现显示其自报名称，无法识别时显示「OneBot v11」。信息含版本、协议版本、平台、运行时间、在线和正常状态；群聊 @机器人后可直接发送 `状态`。若接口不提供平台或运行时长，则分别标明 Bot 所在平台、Bot 与该协议端的连续连接时长，避免误称为协议端进程运行时间；`get_version_info` 不可用时状态查询仍可用。若 QQ 出现“假在线”或消息发送异常，还应查看对应协议端的日志。

本群自动撤回默认开启。成功发送五张图后，Bot 查询自己的群角色；有管理员或群主权限且取得文件消息 ID 时，调用 `delete_msg` 撤回原文件消息，并在群里说明已收到、已解析及撤回原因。没有管理权限时提醒上传者自行撤回。用 `自动撤回用户烤森抓包消息 开启/关闭` 单独设置本群；用 `自动撤回用户烤森抓包消息 查询` 查看设置。私聊不能修改群设置。

任务目录：`runtime/jobs/<任务 ID>/`，内有原始文件、`result/` 五张图、`render.log` 和任务来源。各群设置保存在 `runtime/state/group_settings.sqlite3`；历史任务保留供排错。协议端与 Bot 在同一台电脑时，图片通过本地文件路径发送，需让协议端有权限读取新项目目录。

本地验证：

## 体力提醒

每个 QQ 号独立保存数据。先发送 `火 最大值 50`（也可以写 `火 最大值 -v 50`），再发送 `火 记录 -cur 23 -min 12`（也可简写 `火 记录 23 12`）。`cur` 是当前体力，`min` 是距离下一点体力恢复的分钟数，范围 1–30；每 30 分钟恢复一点。

发送 `火 help`、`火 -help` 或 `火 帮助` 查看体力提醒的完整帮助和示例。
发送 `火 查询` 查看自己的上限、估算当前体力和预计回满时间。

Bot 按真实时间计算满体力时间，提前半小时和满体力时各私聊提醒一次。群聊设置的记录若私聊失败，会在原群提醒并 @ 用户；私聊设置的记录只尝试私聊。Bot 关闭期间时间继续流逝；重启后只发送仍有意义的提醒。满体力时间过去超过 6 小时后，自动清除本次体力记录与提醒状态，保留最大值。数据保存在 `runtime/state/stamina.sqlite3`。

## 转换器计时

发送 `转换器 -time 22` 表示从现在起 22 小时后完成。也支持 `转换器 -计时 22`、`转换器 22`；发送 `转换器 help`、`转换器 -help` 或 `转换器 帮助` 查看完整示例。同一 QQ 号再次记录会覆盖之前的转换器时间。
发送 `转换器 查询` 查看自己的预计完成时间和剩余时间。

完成前半小时及完成时各提醒一次。群聊记录优先私聊，失败时在原群 @；私聊记录只私聊。真实时间在 Bot 关闭时照常流逝；完成超过 6 小时的记录自动清理。每个 QQ 独立保存，数据与体力提醒同在 `runtime/state/stamina.sqlite3`。

```bat
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
.\.venv\Scripts\python.exe tests\test_reply_mode.py
.\.venv\Scripts\python.exe tests\test_private_flow.py
.\.venv\Scripts\python.exe tests\test_status_protocol.py
```

端到端绘图测试需要一份真实抓包；默认读取项目根目录或原 `D:\self\测试烤森逆向\` 下的 `[428] response_mkcn-...` 文件，也可用环境变量 `SEKAI_TEST_CAPTURE` 指定，缺少时会提示 SKIP。
