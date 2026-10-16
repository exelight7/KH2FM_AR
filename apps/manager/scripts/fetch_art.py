"""Fetch the artwork URL supplied by the project owner (build time only)."""
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE = 'https://pin.it/5idSzomoi'
out = Path(__file__).resolve().parents[1] / 'artwork-download'
out.mkdir(parents=True, exist_ok=True)


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.url, response.read()


page_url, data = fetch(SOURCE)
page = data.decode('utf-8', 'replace')
images = []
for tag in re.findall(r'<meta\b[^>]+>', page):
    attributes = dict(re.findall(r'([\w:-]+)=[\'"]([^\'"]*)[\'"]', tag))
    if attributes.get('property') == 'og:image' and attributes.get('content'):
        images.append(html.unescape(attributes['content']))
if not images:
    images = re.findall(r'https://i\.pinimg\.com/originals/[^"\s<>\\]+', page)
if not images:
    raise SystemExit('The supplied page did not expose its original image.')
url = images[0]
if urllib.parse.urlparse(url).hostname != 'i.pinimg.com':
    raise SystemExit('Artwork image must be hosted on the Pinterest image CDN.')
image_url, image = fetch(url)
if not (image.startswith(b'\xff\xd8\xff') or image.startswith(b'\x89PNG\r\n\x1a\n')):
    raise SystemExit('Downloaded artwork is not a JPEG or PNG image.')
extension = '.jpg' if image.startswith(b'\xff\xd8\xff') else '.png'
(out / ('user-art' + extension)).write_bytes(image)
metadata = {'supplied_url': SOURCE, 'page_url': page_url, 'image_url': image_url,
            'sha256': hashlib.sha256(image).hexdigest(), 'bytes': len(image)}
(out / 'ARTWORK_SOURCE.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(metadata, ensure_ascii=False, indent=2))
