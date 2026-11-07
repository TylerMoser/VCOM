from pathlib import Path
import html
import json
import hashlib
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
files = sorted(root.glob('*.png'))
records = []
for file in files:
    with Image.open(file) as im:
        im.verify()
    with Image.open(file) as im:
        records.append(dict(file=file.name, width=im.width, height=im.height,
                            bytes=file.stat().st_size, sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
(root / 'capture' / 'manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
for start in range(0, len(files), 24):
    batch = files[start:start+24]
    sheet = Image.new('RGB', (1280, ((len(batch)+3)//4)*205), '#181c24')
    draw = ImageDraw.Draw(sheet)
    for i, file in enumerate(batch):
        x, y = (i % 4)*320, (i//4)*205
        with Image.open(file) as im:
            im.thumbnail((320,180))
            sheet.paste(im, (x+(320-im.width)//2,y))
        label = file.stem
        draw.text((x+4,y+181), label[:44], fill='white')
    sheet.save(root / 'capture' / f'contact-sheet-{start//24+1:02}.jpg', quality=92)
cards = ''.join(f'<a href="{html.escape(f.name)}"><img loading="lazy" src="{html.escape(f.name)}"><span>{html.escape(f.stem)}</span></a>' for f in files)
(root / 'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VCOM — End of First Month</title><style>body{background:#151922;color:#eee;font:16px system-ui;margin:32px}h1{font-size:28px}input{padding:12px;width:min(500px,90%);margin:15px 0 25px;background:#252d39;color:white;border:1px solid #59657a;border-radius:6px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:20px}a{color:#dce8ff;text-decoration:none;background:#252d39;border-radius:6px;overflow:hidden}img{width:100%;aspect-ratio:16/9;object-fit:contain}span{display:block;padding:12px;font-size:13px}a:hover{outline:2px solid #e1bd62}</style><h1>VCOM — End of First Month</h1><p>November 5, 2026 · '''+str(len(files))+''' new screenshots · Click an image for its full-resolution PNG.</p><input id="filter" placeholder="Filter: combat, lighting, menu, worldmap, editor…" aria-label="Filter screenshots"><div class="grid">'''+cards+'''</div><script>document.querySelector('#filter').addEventListener('input',e=>{for(const a of document.querySelectorAll('.grid a'))a.style.display=a.textContent.toLowerCase().includes(e.target.value.toLowerCase())?'':'none'})</script></html>''', encoding='utf-8')
print(f'Validated {len(files)} screenshots; gallery, contact sheets and SHA-256 manifest written.')
