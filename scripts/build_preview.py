"""Local review wrapper around HTML rendered by GitHub's Markdown API."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
body = (ROOT / ".work/readme-rendered.html").read_text(encoding="utf-8")
# GitHub's renderer may resolve relative images to repository URLs.
body = re.sub(r'https://(?:raw\.githubusercontent\.com/FireFlamingo/FireFlamingo/(?:main|HEAD)/|github\.com/FireFlamingo/FireFlamingo/(?:raw|blob)/(?:main|HEAD)/)assets/', '/assets/', body)
body = body.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/').replace('srcset="assets/', 'srcset="/assets/')
head = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FireFlamingo · profile preview</title>
<style>
:root{color-scheme:dark;--bg:#111214;--fg:#eeece6;--border:#393a3d;--link:#d3a087;--subtle:#1b1c1f}
html.light{color-scheme:light;--bg:#ffffff;--fg:#1f2328;--border:#d1d9e0;--link:#0969da;--subtle:#f6f8fa}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
nav{max-width:1024px;margin:30px auto 18px;display:flex;align-items:center;justify-content:space-between;padding:0 32px;font:12px 'Courier New',monospace;color:#949b9f;gap:12px}
nav div{display:flex;gap:8px}button{font:inherit;background:var(--subtle);color:var(--fg);border:1px solid var(--border);border-radius:5px;padding:7px 12px;cursor:pointer}button:hover{border-color:#d3a087}
article{max-width:1024px;border:1px solid var(--border);border-radius:6px;margin:0 auto 48px;padding:32px}img{max-width:100%;height:auto}picture{display:block}a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}p{margin:16px 0}h3{font-size:20px;line-height:1.25;margin:30px 0 16px;font-weight:600}table{width:100%;border-collapse:collapse;margin:16px 0;font-size:16px}th,td{padding:6px 13px;border:1px solid var(--border);text-align:left;vertical-align:top}th{font-weight:600}td:first-child{width:35%}tr:nth-child(2n){background:var(--subtle)}sub{font-size:12px;line-height:1.5;bottom:0;color:#959da5}code{background:var(--subtle);padding:2px 5px;border-radius:4px}hr{border:0;border-top:1px solid var(--border);margin:28px 0 18px}.anchor{display:none}.markdown-heading{position:relative}
@media(max-width:650px){nav{padding:0 16px;margin-top:16px}article{border:0;padding:16px;margin-bottom:16px}th,td{padding:10px;font-size:13px}sub{font-size:10px}h3{font-size:18px}}
</style><nav><span>FireFlamingo / README.md · local preview</span><div><button id="theme">Light</button><button id="replay">Replay</button></div></nav><article>'''
tail = '''</article><script>
let light=false;
function refresh(){document.querySelectorAll('article img').forEach(img=>{img.src=img.src.split('?')[0]+'?replay='+Date.now();});}
document.getElementById('theme').onclick=()=>{light=!light;document.documentElement.classList.toggle('light',light);document.getElementById('theme').textContent=light?'Dark':'Light';refresh()};document.getElementById('replay').onclick=refresh;refresh();
</script></html>'''
(ROOT / "preview").mkdir(exist_ok=True)
(ROOT / "preview/index.html").write_text(head + body + tail, encoding="utf-8")
(ROOT / "preview.html").write_text((head + body + tail).replace('="/assets/', '="assets/'), encoding="utf-8")
print("Preview created at /preview/ and preview.html")
