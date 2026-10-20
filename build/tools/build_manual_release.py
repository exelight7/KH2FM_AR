"""Build a Windows manual edition from owned originals and the verified 2.0.1 payload."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NODE_VERSION = '24.19.0'
NODE_ZIP_SHA = '57f71ab3652e797d84acddc79c81cc9ff1c6ddb2a1974cdb83f00fee9bff4c73'
OPENKH_SHA = '6e88976744a0fba13f605357238e88285e86ce8c092d2434b935d3feb4ac6eb2'
EXE_SHA = '9002b2de6a1f91a790bd0673de125d1cf833f7942bfec827cdcf6ba64d5849ed'
HEDS = ['kh2_' + name + '.hed' for name in ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(url, destination, expected):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with urllib.request.urlopen(url, timeout=120) as source, destination.open('wb') as out:
            shutil.copyfileobj(source, out)
    if file_sha(destination) != expected:
        raise ValueError('Dependency hash mismatch: ' + destination.name)
    return destination


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def build(args):
    original = Path(args.original).resolve()
    archives = Path(args.archives).resolve()
    cache = Path(args.cache).resolve()
    output = Path(args.output).resolve()
    # Never recursively delete or overwrite a previous release workspace.
    output.mkdir(parents=True, exist_ok=False)
    stage = output / 'KH2FM_AR_Manual'
    stage.mkdir()
    source_manifest = json.loads((ROOT / 'apps/manager/data/manifest.json').read_text())
    assert source_manifest['version'] == '2.0.1'
    catalog = json.loads((ROOT / 'apps/manager/catalog/legacy.json').read_text())
    approved = {f['path']: f['sha256'] for v in catalog['versions'] if v['version'] == '2.0.1' for f in v['files']}
    assert len(approved) == 831
    blob_path = ROOT / 'apps/manager/data/payload.bin'
    assert file_sha(blob_path) == source_manifest['blobHash']
    openkh_config = json.loads((ROOT / 'build/config/panacea.json').read_text())
    openkh_zip = Path(args.openkh_zip) if args.openkh_zip else download(openkh_config['url'], cache / 'openkh-release2-1691.zip', OPENKH_SHA)
    assert file_sha(openkh_zip) == OPENKH_SHA
    deps = ROOT / 'build/vendor/manual-openkh'
    deps.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(openkh_zip) as archive:
        for name in ['OpenKh.Egs.dll', 'OpenKh.Common.dll', 'Xe.BinaryMapper.dll']:
            (deps / name).write_bytes(archive.read('openkh/Apps/' + name))
        for name in ['ddd', 'mare', 'settingmenu', 'theater', 'recom', 'bbs', 'kh1pc', 'launcher28']:
            target = stage / 'tools/resources' / (name + '.txt')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read('openkh/Apps/resources/' + name + '.txt'))
    node_zip = download(f'https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-win-x64.zip', cache / f'node-v{NODE_VERSION}-win-x64.zip', NODE_ZIP_SHA)
    with zipfile.ZipFile(node_zip) as archive:
        for source, target in [('node.exe', 'tools/node.exe'), ('LICENSE', 'licenses/Node-LICENSE.txt')]:
            dest = stage / target
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(archive.read(f'node-v{NODE_VERSION}-win-x64/' + source))
    project = ROOT / 'manual/tools/ManualAssets/ManualAssets.csproj'
    publish = output / 'helper-build'
    subprocess.run(['dotnet', 'publish', str(project), '-c', 'Release', '-r', 'win-x64', '--self-contained', 'true', '-o', str(publish), '-p:PathMap=' + str(ROOT) + '=/_/project'], cwd=project.parent, check=True)
    copy(publish / 'ManualAssets.exe', stage / 'tools/ManualAssets.exe')
    subprocess.run([str(stage / 'tools/ManualAssets.exe'), '--self-test'], check=True)
    runtime = Path(os.environ['USERPROFILE']) / '.nuget/packages/microsoft.netcore.app.runtime.win-x64/8.0.31'
    for name in ['LICENSE.TXT', 'THIRD-PARTY-NOTICES.TXT']:
        choices = [p for p in runtime.rglob('*') if p.is_file() and p.name.lower() == name.lower()]
        assert len(choices) == 1, 'Missing .NET notices: ' + name
        copy(choices[0], stage / 'licenses' / ('DotNET-' + name))
    # Xe.BinaryMapper's MIT notice is obtained from the exact upstream NuGet package.
    mapper = cache / 'xe.binarymapper.1.5.2.nupkg'
    if not mapper.exists():
        with urllib.request.urlopen('https://api.nuget.org/v3-flatcontainer/xe.binarymapper/1.5.2/xe.binarymapper.1.5.2.nupkg', timeout=60) as response:
            mapper.write_bytes(response.read())
    with zipfile.ZipFile(mapper) as archive:
        notices = [n for n in archive.namelist() if 'license' in n.lower() and not n.endswith('/')]
        assert sha(archive.read('lib/netstandard2.0/Xe.BinaryMapper.dll')) == file_sha(deps / 'Xe.BinaryMapper.dll')
        if notices:
            (stage / 'licenses/Xe.BinaryMapper-LICENSE.txt').write_bytes(archive.read(notices[0]))
        else:
            import xml.etree.ElementTree as ET
            nuspec = archive.read('Xe.BinaryMapper.nuspec')
            license_tag = ET.fromstring(nuspec).find('.//{*}license')
            assert license_tag is not None and license_tag.attrib.get('type') == 'expression' and license_tag.text == 'MIT'
            text = (ROOT / 'manual/LICENSE.txt').read_text().split('This license applies')[0]
            text = text.replace('Copyright (c) 2026 KH2FM Arabic contributors', 'Copyright 2019 Luciano Ciccariello')
            (stage / 'licenses/Xe.BinaryMapper-LICENSE.txt').write_text(text)
            (stage / 'licenses/Xe.BinaryMapper.nuspec').write_bytes(nuspec)
    for name in ['engine.cjs', 'paths.cjs', 'transaction.cjs', 'compatibility.cjs', 'font-runtime.cjs']:
        copy(ROOT / 'apps/manager/src' / name, stage / 'engine' / name)
    copy(ROOT / 'apps/manager/catalog/legacy.json', stage / 'engine/legacy.json')
    copy(ROOT / 'apps/manager/data/manifest.json', stage / 'files/manifest.json')
    for name in ['Install_Arabic.bat', 'Uninstall_Arabic.bat', 'Verify_Arabic.bat', 'Undo_Arabic.bat', 'README_AR.md', 'README_EN.md', 'INSTALL_AR.md', 'UNINSTALL_AR.md', 'LICENSE.txt', 'CHANGELOG.md']:
        copy(ROOT / 'manual' / name, stage / name)
    copy(ROOT / 'manual/scripts/manual.cjs', stage / 'scripts/manual.cjs')
    for notice in (ROOT / 'build/docs/licenses').iterdir():
        if notice.is_file() and not notice.name.startswith('InnoSetup'):
            copy(notice, stage / 'licenses' / notice.name)
    for name in ['THIRD_PARTY_LICENSES.md', 'CREDITS.md', 'DISCLAIMER.txt']:
        copy(ROOT / 'build/docs' / name, stage / 'licenses' / name)
    files = []
    original_hashes = set()
    changed = unchanged = 0
    with blob_path.open('rb') as blob:
        for index, entry in enumerate(source_manifest['files']):
            assert entry['size'] <= 128 * 1024 * 1024
            blob.seek(entry['offset'])
            data = gzip.decompress(blob.read(entry['compressedSize']))
            assert len(data) == entry['size'] and sha(data) == entry['sha256']
            record = {k: entry[k] for k in ['path', 'group', 'size', 'sha256']}
            if entry['group'] == 'payload':
                assert approved[entry['path']] == entry['sha256']
            if entry['group'] == 'loader' or entry['path'].startswith('kh2/dll/'):
                name = f'owned/{index:04d}.dll'
                result = data
            else:
                rel = entry['path'][4:]
                source = original / rel if rel.startswith('remastered/') else original / 'original' / rel
                before = source.read_bytes()
                assert len(before) > 0
                container = str(Path(rel[11:]).parent).replace('\\', '/') if rel.startswith('remastered/') else rel
                asset = Path(rel).name if rel.startswith('remastered/') else None
                assert (original / 'original' / container).is_file()
                record.update(container=container, asset=asset, sourceSize=len(before), sourceHash=sha(before))
                original_hashes.add(sha(before))
                changed += data != before
                unchanged += data == before
                delta = np.bitwise_xor(np.frombuffer(data, dtype=np.uint8), np.resize(np.frombuffer(before, dtype=np.uint8), len(data))).tobytes()
                assert np.bitwise_xor(np.frombuffer(delta, dtype=np.uint8), np.resize(np.frombuffer(before, dtype=np.uint8), len(data))).tobytes() == data
                result = gzip.compress(delta, compresslevel=9, mtime=0)
                name = f'patches/{index:04d}.xgz'
            destination = stage / 'files' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(result)
            record.update(file=name, fileHash=sha(result))
            files.append(record)
    assert sum('container' in f for f in files) == 829
    manual = {'schema': 1, 'version': '2.0.1', 'edition': 'Manual Edition', 'exeHash': EXE_SHA,
              'heds': {name: file_sha(archives / name) for name in HEDS}, 'patchFormat': 'gzip-xor-cyclic-source-v1', 'files': files}
    (stage / 'files/manual-manifest.json').write_text(json.dumps(manual, indent=2) + '\n')
    forbidden = {'.pkg', '.hed', '.bar', '.png', '.dds', '.2dd', '.bin', '.pdb', '.pyc'}
    for file in stage.rglob('*'):
        if file.is_file():
            assert file.suffix.lower() not in forbidden, file
            assert file_sha(file) not in original_hashes, 'Complete original asset accidentally included'
            content = file.read_bytes()
            assert b'npxf1' not in content.lower() and b'c:\\filessss' not in content.lower(), file
    checksums = [file_sha(p) + '  ' + p.relative_to(stage).as_posix() for p in sorted(stage.rglob('*')) if p.is_file()]
    (stage / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n')
    package = output / 'KH2FM_AR_Manual_v2.0.1.zip'
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(stage.rglob('*')):
            if file.is_file():
                info = zipfile.ZipInfo('KH2FM_AR_Manual/' + file.relative_to(stage).as_posix(), date_time=(2026, 10, 20, 0, 0, 0))
                archive.writestr(info, file.read_bytes(), compress_type=zipfile.ZIP_STORED if file.suffix == '.xgz' else zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
    report = {'version': '2.0.1', 'edition': 'Manual Edition', 'archive': package.name, 'size': package.stat().st_size,
              'sha256': file_sha(package), 'payloadFiles': 831, 'originalDependentPatches': 829, 'changedFiles': changed,
              'unchangedFilesGeneratedFromUserCopy': unchanged, 'projectPlugins': 2, 'completeOriginalAssetsIncluded': False,
              'gameArchivesIncluded': False, 'gameArchivesModified': False, 'node': NODE_VERSION, 'dotnetRuntime': '8.0.31',
              'openkh': 'release2-1691', 'packageStaticValidation': 'PASS'}
    (output / 'MANUAL_BUILD.json').write_text(json.dumps(report, indent=2) + '\n')
    (output / 'SHA256SUMS.txt').write_text(report['sha256'] + '  ' + package.name + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', required=True, help='Owned extracted data containing original/ and remastered/')
    parser.add_argument('--archives', required=True, help='Owned Image/dt folder, read-only input')
    parser.add_argument('--openkh-zip')
    parser.add_argument('--cache', default='build/vendor/manual-cache')
    parser.add_argument('--output', required=True, help='New release workspace, must not already exist')
    build(parser.parse_args())
