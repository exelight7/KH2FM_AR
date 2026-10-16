import platform
import shutil
from pathlib import Path

app = Path(__file__).resolve().parents[2] / 'apps/manager'
out = app / 'release-output'
out.mkdir(exist_ok=True)
extensions = ('.exe', '.dmg', '.zip', '.AppImage', '.tar.gz', '.deb')
for p in (app / 'dist').iterdir():
    if p.is_file() and p.name.startswith('KH2FM-Arabic-1.0.6-') and p.name.endswith(extensions):
        shutil.copy2(p, out / p.name)
for p in (app / 'test-results').iterdir():
    if p.is_file() and p.suffix in ('.png', '.json', '.txt'):
        shutil.copy2(p, out / p.name)
print('Release files:', ', '.join(p.name for p in out.iterdir()))
