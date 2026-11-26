from pathlib import Path
note='> 当前环境已统一：优先使用项目 `.venv`。启动QQBot：`./start_qqbot.ps1`；手动绘图：`./run_report.ps1 "D:\\captures\\mysekai.bin" --mode "1+4"`。无需激活环境，也无需使用系统 `py`。下文旧的 `py ...` 示例可改用 `.\\.venv\\Scripts\\python.exe ...`。\n\n'
for name in ['README.md','QQBOT.md','USAGE.md']:
 p=Path(name);s=p.read_text(encoding='utf-8-sig');p.write_text(note+s,encoding='utf-8')
p=Path('QQBOT.md');p.write_text(p.read_text(encoding='utf-8')+'\n项目环境由本机Python 3.12创建，所有直接和间接依赖版本固定在 requirements.lock.txt。重装命令：`.\\.venv\\Scripts\\python.exe -m pip install -r requirements.lock.txt`。当前依赖完整性检查和OpenQQ五图模拟测试均通过。已有vendor保留供旧方式备用；运行在.venv时不再优先使用vendor，避免混装。停止旧服务后使用start_qqbot.ps1启动才能切换到新环境。\n',encoding='utf-8')
