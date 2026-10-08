"""Download the official OpenKH release named in config/panacea.json, verify SHA256 (zip + 14 files), extract to vendor/.
Usage: python tools/fetch_panacea.py   (stdlib only; Linux or Windows)"""
import hashlib, json, os, sys, urllib.request, zipfile
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(KIT, 'config', 'panacea.json'), encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
dest = os.path.join(KIT, cfg['extract_to'])
zpath = dest + '.zip'
os.makedirs(os.path.dirname(dest), exist_ok=True)
if not (os.path.isfile(zpath) and sha(open(zpath, 'rb').read()) == cfg['zip_sha256']):
    urllib.request.urlretrieve(cfg['url'], zpath)
if sha(open(zpath, 'rb').read()) != cfg['zip_sha256']:
    sys.exit('zip SHA256 mismatch - refusing to use it')
with zipfile.ZipFile(zpath) as z:
    z.extractall(dest)
for name, want in cfg['files'].items():
    p = os.path.join(dest, *cfg['files_under'].split('/'), name)
    if sha(open(p, 'rb').read()) != want:
        sys.exit('SHA256 mismatch: ' + name)
print('panacea OK: %d files verified in %s' % (len(cfg['files']), cfg['extract_to']))
