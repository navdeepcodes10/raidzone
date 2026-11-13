#!/usr/bin/env python3
"""Generate all CapCut-ready assets for Raid Zone velocity edit Reel."""
import subprocess, os, shutil

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = "/Users/navdeep/Desktop/RaidZone_CapCut_Assets"
SRC = "/Users/navdeep/raidzone-website/capcut_assets"
os.makedirs(OUT, exist_ok=True)

# ──────────────────────────────────────────
# PART 1: Generate bold kinetic text cards
# ──────────────────────────────────────────
text_cards = [
    # (filename, big_text, sub_text, bg_gradient, text_color)
    ("text_SOIL", "SOIL.", "", "radial-gradient(ellipse at 50% 50%, #1a0800, #000)", "#FFFFFF"),
    ("text_SWEAT", "SWEAT.", "", "radial-gradient(ellipse at 50% 50%, #1a0800, #000)", "#FFFFFF"),
    ("text_THE_RAID", "THE RAID.", "", "radial-gradient(ellipse at 50% 50%, #1a0800, #000)", "#FF4500"),
    ("text_EVERY_TOURNAMENT", "EVERY\nTOURNAMENT.", "", "radial-gradient(ellipse at 50% 50%, #0a0a0a, #000)", "#FFFFFF"),
    ("text_ONE_APP", "ONE APP.", "", "radial-gradient(ellipse at 50% 50%, #1a0800, #000)", "#FF6B00"),
    ("text_NO_FAKE_POSTERS", "NO FAKE\nPOSTERS.", "", "radial-gradient(ellipse at 50% 50%, #0a0a0a, #000)", "#FFFFFF"),
    ("text_REAL_PRIZES", "REAL\nPRIZES.", "₹5,00,000+", "radial-gradient(ellipse at 50% 50%, #0a0800, #000)", "#FFD700"),
    ("text_LIVE_STREAMS", "LIVE\nSTREAMS.", "🔴 YouTube", "radial-gradient(ellipse at 50% 50%, #0a0005, #000)", "#E74C3C"),
    ("text_GPS_GROUNDS", "GPS\nGROUNDS.", "📍 Google Maps", "radial-gradient(ellipse at 50% 50%, #000a05, #000)", "#00B894"),
    ("text_DOWNLOAD_FREE", "DOWNLOAD\nFREE.", "Link in Bio 👇", "radial-gradient(ellipse at 50% 50%, #1a0800, #000)", "#FF4500"),
    ("text_RAID_ZONE", "RAID\nZONE", "India's Kabaddi Discovery Hub", "radial-gradient(ellipse at 50% 50%, #1a0500, #000)", "#FF6B00"),
]

for fname, big, sub, bg, color in text_cards:
    sub_html = f'<div class="sub">{sub}</div>' if sub else ''
    big_display = big.replace('\n', '<br>')
    html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1920px; background:{bg}; overflow:hidden; display:flex; align-items:center; justify-content:center; flex-direction:column; }}
.big {{ color:{color}; font-family:'Helvetica Neue',system-ui,sans-serif; font-weight:900; font-size:140px; line-height:0.95; text-align:center; letter-spacing:-4px; text-shadow: 0 0 80px {color}44, 0 4px 0 rgba(0,0,0,0.5); }}
.sub {{ color:rgba(255,255,255,0.6); font-family:system-ui; font-weight:600; font-size:36px; margin-top:30px; text-align:center; }}
.vignette {{ position:absolute; inset:0; background:radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.6) 100%); pointer-events:none; }}
</style></head><body>
<div class="vignette"></div>
<div class="big">{big_display}</div>
{sub_html}
</body></html>'''
    path = os.path.join(SRC, f"{fname}.html")
    with open(path, 'w') as f:
        f.write(html)

# ──────────────────────────────────────────
# PART 2: Render all HTML files to PNG
# ──────────────────────────────────────────
renders = [
    # (html_file, output_name, width, height)
    ("01_phone_mockup.html", "01_3D_Phone_Mockup", 1080, 1920),
    ("02_glow_logo.html", "02_Glowing_Logo", 1080, 1080),
    ("03_dark_arena_bg.html", "03_Dark_Arena_Background", 1080, 1920),
]

# Add all text cards
for fname, _, _, _, _ in text_cards:
    renders.append((f"{fname}.html", fname, 1080, 1920))

for html_file, out_name, w, h in renders:
    html_path = os.path.join(SRC, html_file)
    png_path = os.path.join(OUT, f"{out_name}.png")
    
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        f"--screenshot={png_path}",
        f"--default-background-color=00000000",  # transparent
        f"file://{html_path}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if os.path.exists(png_path):
        size_kb = os.path.getsize(png_path) // 1024
        print(f"✅ {out_name}.png ({size_kb} KB)")
    else:
        print(f"❌ FAILED: {out_name}")
        if result.stderr:
            print(f"   Error: {result.stderr[:200]}")

# ──────────────────────────────────────────
# PART 3: Copy clean logo (transparent)
# ──────────────────────────────────────────
logo_src = "/Users/navdeep/raidzone-website/assets/logo.png"
logo_dst = os.path.join(OUT, "00_Logo_Transparent.png")
shutil.copy2(logo_src, logo_dst)
print(f"✅ 00_Logo_Transparent.png (copied)")

# ──────────────────────────────────────────
# PART 4: Copy existing kabaddi hero image
# ──────────────────────────────────────────
hero_src = "/Users/navdeep/raidzone-website/assets/kabaddi_hero.jpg"
hero_dst = os.path.join(OUT, "04_Kabaddi_Hero_Action.jpg")
if os.path.exists(hero_src):
    shutil.copy2(hero_src, hero_dst)
    print(f"✅ 04_Kabaddi_Hero_Action.jpg (copied)")

# Summary
print(f"\n{'='*50}")
print(f"📁 All assets saved to: {OUT}")
total = len([f for f in os.listdir(OUT) if f.endswith(('.png','.jpg'))])
print(f"📊 Total assets: {total} files")
print(f"\n🎬 HOW TO USE IN CAPCUT:")
print(f"1. AirDrop this folder to your phone")
print(f"2. Open CapCut → New Project → 9:16")
print(f"3. Use a trending velocity template")
print(f"4. Replace template images with these assets")
print(f"5. The text cards work perfectly with beat-synced cuts")
