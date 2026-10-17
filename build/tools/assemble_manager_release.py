"""Keep the download list small; preserve all supporting files in one ZIP."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

PRIMARY = {
    'KH2FM-Arabic-1.0.10-Windows-x64.exe': '01-KH2FM-Arabic-1.0.10-Windows-x64.exe',
    'KH2FM-Arabic-1.0.10-Linux-x86_64.AppImage': '02-KH2FM-Arabic-1.0.10-Linux-x64.AppImage',
}
EXTRAS = '03-KH2FM-Arabic-1.0.10-Extras-and-Reports.zip'


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def archive_path(name):
    if name == 'SHA256SUMS.txt':
        return 'checksums/ORIGINAL-SHA256SUMS.txt'
    if name.endswith('.png'):
        return 'screenshots/' + name
    if name.startswith('KH2FM-Arabic-'):
        return 'alternative-downloads/' + name
    return 'reports/' + name


def package_extras(root, destination, original_hashes):
    supporting = [root / name for name in sorted(original_hashes) if name not in PRIMARY]
    for path in supporting:
        assert path.is_file(), f'Missing supporting file: {path.name}'
        assert sha256(path) == original_hashes[path.name], f'Hash mismatch: {path.name}'
    checksum_lines = [original_hashes[old] + '  ' + new for old, new in PRIMARY.items()]
    checksum_lines += [original_hashes[p.name] + '  ' + archive_path(p.name) for p in supporting]
    readme = '''# ملفات إضافية لتحديث 1.0.10

هذا الملف اختياري. للتثبيت حمّل برنامج نظامك مباشرة من الإصدار.
نسخة ويندوز هي الملف الأول في قائمة التحميل، ويبدأ اسمها بـ01.

- reports: التقارير ونتائج الاختبارات ودليل استخدام البرنامج.
- screenshots: صور البرنامج وقائمة الحذف على الأنظمة المختلفة.
- alternative-downloads: نسخة TAR.GZ للينكس عند الحاجة.
- SHA256SUMS.txt: بصمات البرنامجين بأسمائها الجديدة، ومحتويات هذا الأرشيف.
- checksums/ORIGINAL-SHA256SUMS.txt: قائمة البصمات القديمة بالأسماء الأصلية، محفوظة للرجوع إليها.
- ORIGINAL_ASSET_HASHES.json: بصمات جميع الملفات الأصلية قبل ترتيب قائمة التحميل.

لم تتغير محتويات أي برنامج عند إعادة تسمية الملفات. تنشر النسخة التجريبية بعد نجاح فحوص Windows ولينكس.
'''
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', allowZip64=True) as archive:
        archive.writestr('README_AR.md', readme, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr('SHA256SUMS.txt', '\n'.join(checksum_lines) + '\n', compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr('ORIGINAL_ASSET_HASHES.json', json.dumps(original_hashes, indent=2) + '\n', compress_type=zipfile.ZIP_DEFLATED)
        for path in supporting:
            compression = zipfile.ZIP_STORED if path.name.endswith(('.zip', '.tar.gz')) else zipfile.ZIP_DEFLATED
            archive.write(path, archive_path(path.name), compress_type=compression)
    # Check the bytes users will extract, before upload or removal of any originals.
    with zipfile.ZipFile(destination) as archive:
        assert len(archive.namelist()) == len(supporting) + 3
        for path in supporting:
            with archive.open(archive_path(path.name)) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == original_hashes[path.name]
    return {'original_files_preserved': len(supporting), 'archive': destination.name, 'sha256': sha256(destination)}


def main():
    root = Path(sys.argv[1])
    reports = [json.loads(p.read_text()) for p in root.glob('PACKAGED-*.json')]
    assert len(reports) == 2 and all(r['passed'] for r in reports)
    for name in PRIMARY:
        assert (root / name).is_file(), f'Missing primary program: {name}'
    original_hashes = {p.name: sha256(p) for p in sorted(root.iterdir()) if p.is_file()}
    assert EXTRAS not in original_hashes, 'Use a fresh staging directory'
    result = package_extras(root, root / EXTRAS, original_hashes)
    for old, new in PRIMARY.items():
        (root / old).rename(root / new)
    for name in original_hashes:
        if name not in PRIMARY:
            (root / name).unlink()
    assert sorted(p.name for p in root.iterdir()) == sorted([*PRIMARY.values(), EXTRAS])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
