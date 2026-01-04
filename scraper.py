import requests
import re
from datetime import datetime
import html

def clean_text(text):
    return html.unescape(re.sub(r'<[^>]+>', '', text)).strip()

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Live Football Streams • {today}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  <style>
    :root {{ --bg:#0f0f1a; --card:#161b2e; --accent:#00d4ff; --text:#e0e0ff; --border:#2a3566; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:system-ui,sans-serif; background:var(--bg); color:var(--text); padding:1.2rem; }}
    header {{ text-align:center; padding:2rem 0; }}
    h1 {{ font-size:clamp(2.2rem,5vw,3.4rem); background:linear-gradient(90deg,#00d4ff,#7c3aed); -webkit-background-clip:text; color:transparent; }}
    .subtitle {{ color:#aaa; font-size:1.1rem; margin-top:0.5rem; }}
    .container {{ max-width:1280px; margin:0 auto; }}
    .date-group {{ margin:2.5rem 0; }}
    .date-header {{ font-size:1.9rem; color:var(--accent); margin-bottom:1rem; padding-left:1rem; border-left:5px solid var(--accent); }}
    .matches-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(380px,1fr)); gap:1.4rem; }}
    .match-card {{ background:var(--card); border-radius:12px; border:1px solid var(--border); overflow:hidden; transition:all .25s; }}
    .match-card:hover {{ transform:translateY(-6px); box-shadow:0 12px 30px rgba(0,212,255,.18); }}
    .match-title {{ padding:1.2rem 1.4rem; font-size:1.3rem; font-weight:600; background:rgba(0,212,255,.08); border-bottom:1px solid var(--border); }}
    .streams {{ padding:1.2rem 1.4rem; display:flex; flex-direction:column; gap:0.9rem; }}
    .stream-btn {{ padding:1rem; background:#1e2550; color:white; text-align:center; border-radius:10px; text-decoration:none; font-weight:500; transition:all .2s; border:1px solid #3a437a; cursor:pointer; }}
    .stream-btn:hover {{ background:var(--accent); color:#000; transform:translateY(-2px); }}
    footer {{ text-align:center; margin-top:4rem; padding:2rem 0; color:#666; font-size:.95rem; border-top:1px solid var(--border); }}
  </style>
</head>
<body>
  <header>
    <h1>Live Football Streams</h1>
    <div class="subtitle">Today's & Upcoming Matches • {today}</div>
  </header>
  <div class="container">
{content}
  </div>
  <footer>
    <p>Unofficial streams • Use responsibly • Updated {now}</p>
  </footer>

  <script>
    function openStream(url){{
      const w=Math.min(1920,screen.availWidth*0.94);
      const h=Math.min(1080,screen.availHeight*0.9);
      const l=(screen.availWidth-w)/2;
      const t=(screen.availHeight-h)/2-30;
      window.open(url,'stream','width='+w+',height='+h+',left='+l+',top='+t+',menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=yes');
    }}
  </script>
</body>
</html>"""

def make_card(title, links):
    btns = '\n'.join(
        f'    <button class="stream-btn" onclick="openStream(\'{link}\')"><i class="fas fa-play-circle"></i> Stream {i}</button>'
        for i, link in enumerate(links, 1)
    )
    return f'''<div class="match-card">
  <div class="match-title">{title}</div>
  <div class="streams">
{btns}
  </div>
</div>'''

def main():
    url = "https://elixx.link/"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        html = r.text
    except Exception as e:
        print(f"Error: {e}")
        return

    # Very simple pattern - works with current text-like format (Jan 2026)
    date_matches = re.findall(r'(\d{2}\.\d{2})\s+((?:Match:.*?(?=Match:|$)[\s\S]*?))', html, re.MULTILINE)

    content = ""
    for date, block in date_matches:
        date_clean = date.replace('.', ' ')
        cards = []
        matches = re.findall(r'Match: (.*?)\s+Links: (https?://elixx\.link/aw/[\w-]+\.php(?:\s+https?://elixx\.link/aw/[\w-]+\.php)*)', block)
        
        for title, links_str in matches:
            links = re.findall(r'https?://elixx\.link/aw/[\w-]+\.php', links_str)
            links = list(set(links))  # remove duplicates if any
            if links:
                cards.append(make_card(title.strip(), links))
        
        if cards:
            content += f'<div class="date-group"><h2 class="date-header">{date_clean}</h2><div class="matches-grid">{"".join(cards)}</div></div>'

    today = datetime.utcnow().strftime("%d %b %Y")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    final = TEMPLATE.format(today=today, content=content, now=now)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final)
    
    print("Generated index.html")

if __name__ == "__main__":
    main()
