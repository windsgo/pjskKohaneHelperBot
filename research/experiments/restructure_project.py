from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
pkg = root / 'src' / 'sekai_toolkit'
for part in ('', 'cli', 'decoder', 'report', 'assets', 'bot', 'common'):
    folder = pkg / part
    folder.mkdir(parents=True, exist_ok=True)
    (folder / '__init__.py').touch()

def move(name, dest):
    source = root / name
    target = root / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.exists() and not target.exists():
        shutil.move(str(source), str(target))

for old, new in {
    'sekai_report.py': 'src/sekai_toolkit/cli/report.py',
    'decode_sekai.py': 'src/sekai_toolkit/decoder/decode_sekai.py',
    'msgpack_reader.py': 'src/sekai_toolkit/decoder/msgpack_reader.py',
    'render_compact_report.py': 'src/sekai_toolkit/report/renderer.py',
    'qqbot_server.py': 'src/sekai_toolkit/bot/server.py',
    'sync_report_assets.py': 'src/sekai_toolkit/assets/sync.py',
    'USAGE.md': 'docs/USAGE.md',
    'QQBOT.md': 'docs/QQBOT.md',
    'reference': 'research/reference',
    'bot_jobs': 'runtime/jobs',
    'decoded': 'runtime/decoded',
    'decrypted.msgpack': 'research/snapshots/decrypted.msgpack',
    'materials_cn.json': 'masterdata/materials_cn.json',
    'materials_jp.json': 'masterdata/materials_jp.json',
    'lunabot_tree.json': 'research/reference/lunabot/tree.json',
    'mapper_tree.json': 'research/reference/mapper/tree.json',
    'openqq_tree.json': 'research/reference/openqq/tree.json',
    'ursekai_tree.json': 'research/reference/ursekai/tree.json',
    'project_tree.txt': 'research/snapshots/project_tree.txt',
}.items():
    move(old, new)

for f in root.glob('test_*.py'):
    move(f.name, 'tests/' + f.name)

patches = ('add_', 'allow_', 'adapt_', 'compact_bg_', 'finish_', 'fix_', 'improve_', 'lazy_', 'polish_', 'refactor_', 'refine_', 'split_', 'unify_python_', 'update_vertical')
assets = ('audit_', 'cache_csv_', 'download_', 'fetch_', 'retry_', 'sync_', 'unify_chibi', 'update_visitor_', 'extract_resources')
for f in root.glob('*.py'):
    n = f.name
    if n == 'restructure_project.py':
        continue
    if n.startswith(patches):
        move(n, 'research/experiments/legacy_patches/' + n)
    elif n.startswith(assets):
        move(n, 'scripts/asset_tools/' + n)
    elif n.startswith(('inspect_', 'probe_', 'find_', 'check_', 'verify_')):
        move(n, 'research/probes/' + n)
    elif n.startswith(('plot_', 'build_', 'finalize_', 'summarize_')):
        move(n, 'research/experiments/' + n)
    elif n.startswith(('install_', 'document_')):
        move(n, 'scripts/environment/' + n)

for name, folder in [('lunabot_', 'research/reference/lunabot'), ('mapper_', 'research/reference/mapper')]:
    for f in root.glob(name + '*'):
        if f.is_file():
            move(f.name, folder + '/' + f.name)

for folder in ('runtime/state', 'runtime/cache', 'runtime/temp', 'logs/bot', 'logs/report', 'config'):
    (root / folder).mkdir(parents=True, exist_ok=True)
move('runtime/jobs/reply_settings.json', 'runtime/state/reply_settings.json')
