"""Arrange an existing draft without rebuilding or changing any program bytes."""
import json
import subprocess
from pathlib import Path

from assemble_manager_release import EXTRAS, PRIMARY, package_extras

REPOSITORY = 'exelight7/KH2FM_AR'


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True)


def api(path, *args):
    return json.loads(gh('api', f'repos/{REPOSITORY}/{path}', *args))


def main():
    release = next(r for r in api('releases') if r['tag_name'] == 'v1.0.3')
    release_id = release['id']
    assert release['draft'], 'The owner already published this release'
    expected = set(PRIMARY.values()) | {EXTRAS}
    if {a['name'] for a in release['assets']} == expected:
        print('Already arranged:', release['html_url'])
        return
    assets = {a['name']: a for a in release['assets']}
    assert set(PRIMARY).issubset(assets), 'Unexpected draft layout; refusing changes'
    assert EXTRAS not in assets, 'An archive is already present; inspect before retrying'
    hashes = {name: a['digest'].removeprefix('sha256:') for name, a in assets.items()}
    supporting = sorted(set(assets) - set(PRIMARY))
    root = Path('original-downloads')
    root.mkdir()
    download_args = ['release', 'download', 'v1.0.3', '-R', REPOSITORY, '-D', str(root)]
    for name in supporting:
        download_args.extend(['--pattern', name])
    gh(*download_args)
    archive = Path('compact-release') / EXTRAS
    result = package_extras(root, archive, hashes)
    assert api(f'releases/{release_id}')['draft']
    gh('release', 'upload', 'v1.0.3', str(archive), '-R', REPOSITORY)
    uploaded = api(f'releases/{release_id}')
    assert uploaded['draft']
    remote_archive = next(a for a in uploaded['assets'] if a['name'] == EXTRAS)
    assert remote_archive['state'] == 'uploaded'
    assert remote_archive['size'] == archive.stat().st_size
    assert remote_archive['digest'] == 'sha256:' + result['sha256']
    # Supporting originals are removed only after all bytes are verified locally
    # and GitHub confirms the replacement archive's full size and SHA256.
    for old, new in PRIMARY.items():
        renamed = api(f"releases/assets/{assets[old]['id']}", '--method', 'PATCH', '-f', 'name=' + new)
        assert renamed['digest'] == assets[old]['digest']
    for name in supporting:
        subprocess.run(['gh', 'api', f"repos/{REPOSITORY}/releases/assets/{assets[name]['id']}", '--method', 'DELETE'], check=True)
    body = {
        'tag_name': 'v1.0.3',
        'name': 'v1.0.3',
        'body': Path('docs/releases/1.0.3.md').read_text(),
        'target_commitish': gh('api', f'repos/{REPOSITORY}/git/ref/heads/installer/1.0.3', '--jq', '.object.sha').strip(),
        'draft': True,
        'prerelease': False,
    }
    Path('release-update.json').write_text(json.dumps(body))
    final = api(f'releases/{release_id}', '--method', 'PATCH', '--input', 'release-update.json')
    assert final['tag_name'] == 'v1.0.3' and final['draft'] and not final['prerelease']
    assert {a['name'] for a in final['assets']} == expected
    for old, new in PRIMARY.items():
        current = next(a for a in final['assets'] if a['name'] == new)
        assert current['id'] == assets[old]['id'] and current['digest'] == assets[old]['digest']
    Path('ASSETS_CLEANUP_FINAL.json').write_text(json.dumps(final, indent=2))
    print(json.dumps(result, indent=2))
    print('Six verified assets; Windows first:', final['html_url'])


if __name__ == '__main__':
    main()
