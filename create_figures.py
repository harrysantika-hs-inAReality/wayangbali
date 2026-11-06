import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = '/opt/lampp/htdocs/landingpage/wayang/docs_assets'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper font loader
def get_font(size, bold=False, serif=False, mono=False):
    try:
        if mono:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        elif serif:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        else:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

# -------------------------------------------------------------
# FIG 1: Cover Banner
# -------------------------------------------------------------
def create_fig01_cover():
    width, height = 1600, 900
    bg_path = '/opt/lampp/htdocs/landingpage/wayang/assett/BG.jpg'
    if os.path.exists(bg_path):
        bg = Image.open(bg_path).convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
    else:
        bg = Image.new('RGBA', (width, height), (238, 232, 220, 255))
    
    # Apply warm dark vignette / overlay
    overlay = Image.new('RGBA', (width, height), (30, 20, 10, 160))
    bg = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(bg)

    # Load characters and compose
    chars = [
        ('wayang04', 150, 240, 420),
        ('wayang02', 360, 220, 480),
        ('wayang01', 650, 180, 560),
        ('wayang03', 960, 210, 500),
        ('wayang05', 1190, 230, 440),
    ]

    for char_id, x, y, h in chars:
        p1 = f'/opt/lampp/htdocs/landingpage/wayang/assett/{char_id}/reference.png'
        p2 = f'/opt/lampp/htdocs/landingpage/wayang/assett/{char_id}/refrence.png'
        p = p1 if os.path.exists(p1) else p2
        if os.path.exists(p):
            wimg = Image.open(p).convert('RGBA')
            aspect = wimg.width / wimg.height
            w = int(h * aspect)
            wimg = wimg.resize((w, h), Image.Resampling.LANCZOS)
            # Add soft gold glow under puppet
            glow = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow)
            gdraw.ellipse([10, 10, w + 30, h + 30], fill=(212, 174, 97, 40))
            glow = glow.filter(ImageFilter.GaussianBlur(15))
            bg.alpha_composite(glow, (x - 20, y - 20))
            bg.alpha_composite(wimg, (x, y))

    # Top title bar & emblem
    draw.rectangle([0, 0, width, 140], fill=(18, 12, 8, 210))
    draw.line([(0, 140), (width, 140)], fill=(168, 120, 38, 255), width=3)

    # Monogram WB
    draw.ellipse([80, 25, 170, 115], outline=(212, 174, 97, 255), width=3)
    f_wb = get_font(42, bold=True, serif=True)
    draw.text((100, 45), "WB", font=f_wb, fill=(212, 174, 97, 255))

    f_title = get_font(38, bold=True, serif=True)
    draw.text((200, 35), "WAYANG BALI INTERACTIVE", font=f_title, fill=(255, 245, 225, 255))
    f_sub = get_font(20, bold=False, serif=False)
    draw.text((200, 85), "Dokumentasi Modul Sistem Komputer Visi, Kinematika Wayang & Arsitektur WebGL", font=f_sub, fill=(212, 174, 97, 255))

    # Bottom Banner Info
    draw.rectangle([0, height - 120, width, height], fill=(18, 12, 8, 230))
    draw.line([(0, height - 120), (width, height - 120)], fill=(168, 120, 38, 255), width=3)
    f_bot1 = get_font(22, bold=True)
    draw.text((80, height - 95), "MODUL PROFESIONAL & PANDUAN PENGEMBANGAN TEKNIS LENGKAP", font=f_bot1, fill=(245, 235, 215, 255))
    f_bot2 = get_font(18, bold=False)
    draw.text((80, height - 60), "Dilengkapi Penjelasan Kode Teknis, Logika Orang Awam, Diagram Kinematika & Screenshot Antarmuka", font=f_bot2, fill=(180, 165, 145, 255))

    bg.convert('RGB').save(os.path.join(OUTPUT_DIR, 'fig01_cover_banner.png'), quality=95)
    print("Fig 1 created")

# -------------------------------------------------------------
# FIG 2: System Architecture Diagram (Matplotlib)
# -------------------------------------------------------------
def create_fig02_architecture():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor('#F8F5EE')
    ax.set_facecolor('#F8F5EE')

    # Title
    ax.text(0.5, 0.95, "ARSITEKTUR END-TO-END WAYANG BALI INTERACTIVE", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#35291D', fontfamily='sans-serif')
    ax.text(0.5, 0.91, "Aliran Data Real-Time: Dari Sensor Kamera Fisik Hingga Rendering 30 FPS WebGL", 
            ha='center', va='center', fontsize=11, color='#776A5C', fontfamily='sans-serif')

    boxes = [
        # (x, y, w, h, title, subtitle, color, border)
        (0.05, 0.65, 0.25, 0.18, "1. Camera Input", "navigator.mediaDevices.getUserMedia\nResolusi: 640x480 @ 24fps\nDevice fallback: Android/Safari", "#FFFDF8", "#A87826"),
        (0.37, 0.65, 0.26, 0.18, "2. VideoFrameLoop", "requestVideoFrameCallback\nThrottling: 12-20 FPS adaptif\nSync frame tanpa frame-skip", "#FFFDF8", "#A87826"),
        (0.70, 0.65, 0.25, 0.18, "3. MediaPipe Vision", "HandLandmarker (Wasm/SIMD)\n21 Titik Landmark 3D\nRunningMode: VIDEO (2 Tangan)", "#FFFDF8", "#A87826"),

        (0.05, 0.35, 0.25, 0.18, "6. PixiRenderer (WebGL)", "Pixi.js v8 Stage Container\nFraming letterboxing & auto-fit\nHard ceiling: strictly 30 FPS", "#FFFDF8", "#2C5E8A"),
        (0.37, 0.35, 0.26, 0.18, "5. PuppetRig & TwoBoneIK", "Inverse Kinematics 2-Tulang\nHukum Cosinus Sudut Siku\nScenegraph Hierarki Tubuh", "#FFFDF8", "#2C5E8A"),
        (0.70, 0.35, 0.25, 0.18, "4. HandTrackManager", "Bipartite Cost Assignment\nAnti Hand-Swapping Filter\nPalm Center Averaging & Mirror", "#FFFDF8", "#2C5E8A"),

        (0.20, 0.06, 0.60, 0.18, "7. Controller, Session & PWA Runtime", 
         "State Machine (HOME -> SELECTION -> CALIBRATION -> PLAYING -> COMPLETE)\nOffline Caching (Service Worker, Cache API, asset-manifest.json) & Concurrency Queue (queue.php)",
         "#FFFDF8", "#5C4018")
    ]

    for x, y, w, h, title, sub, bg_c, bd_c in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=bg_c, edgecolor=bd_c, linewidth=2, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.04, title, ha='center', va='center', fontsize=11, fontweight='bold', color=bd_c, zorder=3)
        ax.text(x + w/2, y + h/2 - 0.02, sub, ha='center', va='center', fontsize=8.5, color='#45382A', zorder=3)

    # Arrows
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#A87826', lw=2.5)
    ax.annotate("", xy=(0.37, 0.74), xytext=(0.30, 0.74), arrowprops=arrow_props)
    ax.annotate("", xy=(0.70, 0.74), xytext=(0.63, 0.74), arrowprops=arrow_props)
    # Down arrow
    arrow_down = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#2C5E8A', lw=2.5)
    ax.annotate("", xy=(0.825, 0.53), xytext=(0.825, 0.65), arrowprops=arrow_down)
    # Left arrows
    ax.annotate("", xy=(0.63, 0.44), xytext=(0.70, 0.44), arrowprops=arrow_down)
    ax.annotate("", xy=(0.30, 0.44), xytext=(0.37, 0.44), arrowprops=arrow_down)
    # Down to bottom
    arrow_sub = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#5C4018', lw=2, linestyle='--')
    ax.annotate("", xy=(0.50, 0.24), xytext=(0.50, 0.35), arrowprops=arrow_sub)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig02_system_architecture.png'), dpi=180, facecolor=fig.get_facecolor())
    plt.close()
    print("Fig 2 created")

# -------------------------------------------------------------
# FIG 3: UI Home Screen Mockup
# -------------------------------------------------------------
def create_fig03_ui_home():
    width, height = 1280, 720
    im = Image.new('RGBA', (width, height), (238, 232, 220, 255))
    draw = ImageDraw.Draw(im)

    # Decorative Balinese side borders
    for x_edge in [0, width - 45]:
        draw.rectangle([x_edge, 0, x_edge + 45, height], fill=(219, 187, 122, 60))
        for y in range(20, height, 40):
            draw.ellipse([x_edge + 15, y, x_edge + 30, y + 15], outline=(168, 120, 38, 180), width=2)

    # Header
    draw.ellipse([60, 25, 110, 75], outline=(168, 120, 38, 255), width=2)
    draw.text((73, 40), "WB", font=get_font(22, bold=True, serif=True), fill=(168, 120, 38, 255))
    draw.text((125, 42), "WAYANG BALI", font=get_font(20, bold=True), fill=(53, 41, 29, 255))

    # Hero Glass Panel (Left)
    card_x, card_y, card_w, card_h = 70, 120, 520, 480
    card = Image.new('RGBA', (card_w, card_h), (255, 252, 246, 215))
    cdraw = ImageDraw.Draw(card)
    cdraw.rounded_rectangle([0, 0, card_w, card_h], radius=24, outline=(255, 255, 255, 240), width=2)
    im.alpha_composite(card, (card_x, card_y))

    draw.text((card_x + 40, card_y + 40), "PANGGUNG WAYANG INTERAKTIF", font=get_font(13, bold=True), fill=(168, 120, 38, 255))
    draw.text((card_x + 40, card_y + 75), "Hidupkan cerita\nlewat gerakmu.", font=get_font(34, bold=True, serif=True), fill=(53, 41, 29, 255))
    
    lead_text = "Pilih tokoh, gerakkan tangan, dan mainkan\nWayang Bali langsung dari kamera perangkatmu\ntanpa alat sensor tambahan."
    draw.text((card_x + 40, card_y + 190), lead_text, font=get_font(15), fill=(119, 106, 92, 255))

    # Primary Button "PILIH WAYANG ->"
    btn_x, btn_y, btn_w, btn_h = card_x + 40, card_y + 290, 230, 52
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=26, fill=(183, 138, 53, 255), outline=(132, 96, 28, 255), width=2)
    draw.text((btn_x + 35, btn_y + 16), "PILIH WAYANG  →", font=get_font(16, bold=True), fill=(255, 250, 241, 255))

    # Privacy Note
    draw.ellipse([card_x + 40, card_y + 380, card_x + 48, card_y + 388], fill=(168, 120, 38, 255))
    draw.text((card_x + 56, card_y + 375), "Kamera diproses langsung di perangkat dan tidak disimpan.", font=get_font(12), fill=(119, 106, 92, 255))

    # Hero Cast (Right)
    cast_x = 620
    for idx, char_id in enumerate(['wayang01', 'wayang02', 'wayang03', 'wayang04', 'wayang05']):
        p = f'/opt/lampp/htdocs/landingpage/wayang/assett/{char_id}/reference.png'
        if not os.path.exists(p):
            p = f'/opt/lampp/htdocs/landingpage/wayang/assett/{char_id}/refrence.png'
        if os.path.exists(p):
            wimg = Image.open(p).convert('RGBA')
            aspect = wimg.width / wimg.height
            h = 360 if idx == 0 else 310
            w = int(h * aspect)
            wimg = wimg.resize((w, h), Image.Resampling.LANCZOS)
            cx = cast_x + idx * 115
            cy = 200 + (0 if idx == 0 else 30)
            im.alpha_composite(wimg, (cx, cy))
            draw.text((cx + 15, cy + h + 10), f"Wayang 0{idx+1}", font=get_font(12, bold=True), fill=(80, 65, 50, 255))

    # Bottom feature strip
    strip_w, strip_h = 1000, 50
    strip_x, strip_y = 140, height - 70
    draw.rounded_rectangle([strip_x, strip_y, strip_x + strip_w, strip_y + strip_h], radius=25, fill=(255, 252, 246, 210), outline=(212, 174, 97, 180), width=1)
    draw.text((strip_x + 60, strip_y + 16), "01 · Pilih 1–2 wayang       |       02 · Kendalikan dengan tangan       |       03 · Main selama 3 menit", font=get_font(14, bold=True), fill=(83, 65, 45, 255))

    im.convert('RGB').save(os.path.join(OUTPUT_DIR, 'fig03_ui_home.png'), quality=95)
    print("Fig 3 created")

# -------------------------------------------------------------
# FIG 4: UI Character Selection Mockup
# -------------------------------------------------------------
def create_fig04_ui_selection():
    width, height = 1280, 720
    im = Image.new('RGBA', (width, height), (238, 232, 220, 255))
    draw = ImageDraw.Draw(im)

    # Header
    draw.rounded_rectangle([60, 30, 200, 65], radius=18, fill=(255, 252, 246, 220), outline=(168, 120, 38, 180), width=1)
    draw.text((80, 40), "← MENU UTAMA", font=get_font(12, bold=True), fill=(83, 65, 45, 255))

    draw.text((240, 25), "PILIH LAKONMU", font=get_font(12, bold=True), fill=(168, 120, 38, 255))
    draw.text((240, 45), "Pilih Wayang", font=get_font(26, bold=True, serif=True), fill=(53, 41, 29, 255))
    draw.text((430, 52), "— Tentukan 1 atau 2 tokoh, lalu pilih tangan pengendali (Kiri / Kanan).", font=get_font(13), fill=(119, 106, 92, 255))

    # Grid of 5 characters
    card_w, card_h = 220, 370
    start_x, start_y = 60, 110
    selections = {0: 'left', 2: 'right'} # Wayang 01 = left, Wayang 03 = right

    for i in range(5):
        char_id = f'wayang0{i+1}'
        cx = start_x + i * 235
        cy = start_y

        is_sel = i in selections
        slot = selections.get(i)

        # Card container
        bg_col = (255, 250, 240, 245) if is_sel else (255, 252, 246, 190)
        bd_col = (168, 120, 38, 255) if is_sel else (220, 205, 185, 255)
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=18, fill=bg_col, outline=bd_col, width=2 if is_sel else 1)

        # Selected badge
        if is_sel:
            draw.rounded_rectangle([cx + 20, cy + 12, cx + card_w - 20, cy + 36], radius=12, fill=(168, 120, 38, 255))
            txt = "TANGAN KIRI (L)" if slot == 'left' else "TANGAN KANAN (R)"
            draw.text((cx + 42, cy + 16), txt, font=get_font(11, bold=True), fill=(255, 255, 255, 255))

        # Thumbnail
        p = f'/opt/lampp/htdocs/landingpage/wayang/assett/{char_id}/reference.png'
        if not os.path.exists(p):
            p = f'/opt/lampp/htdocs/landingpage/wayang/assett/{char_id}/refrence.png'
        if os.path.exists(p):
            wimg = Image.open(p).convert('RGBA')
            aspect = wimg.width / wimg.height
            th_h = 210
            th_w = int(th_h * aspect)
            wimg = wimg.resize((th_w, th_h), Image.Resampling.LANCZOS)
            im.alpha_composite(wimg, (cx + (card_w - th_w)//2, cy + 45))

        # Name
        draw.text((cx + 65, cy + 270), f"Wayang 0{i+1}", font=get_font(16, bold=True, serif=True), fill=(53, 41, 29, 255))

        # Hand assignment buttons L and R
        btn_w_half = 90
        btn_y = cy + 310
        # Left button
        l_fill = (168, 120, 38, 255) if slot == 'left' else (245, 240, 230, 255)
        l_text = (255, 255, 255, 255) if slot == 'left' else (53, 41, 29, 255)
        draw.rounded_rectangle([cx + 15, btn_y, cx + 15 + btn_w_half, btn_y + 36], radius=18, fill=l_fill, outline=(168, 120, 38, 200), width=1)
        draw.text((cx + 32, btn_y + 10), "L · KIRI", font=get_font(11, bold=True), fill=l_text)

        # Right button
        r_fill = (168, 120, 38, 255) if slot == 'right' else (245, 240, 230, 255)
        r_text = (255, 255, 255, 255) if slot == 'right' else (53, 41, 29, 255)
        draw.rounded_rectangle([cx + 115, btn_y, cx + 115 + btn_w_half, btn_y + 36], radius=18, fill=r_fill, outline=(168, 120, 38, 200), width=1)
        draw.text((cx + 128, btn_y + 10), "R · KANAN", font=get_font(11, bold=True), fill=r_text)

    # Bottom Dock
    dock_x, dock_y, dock_w, dock_h = 60, height - 190, width - 120, 160
    draw.rounded_rectangle([dock_x, dock_y, dock_x + dock_w, dock_y + dock_h], radius=24, fill=(255, 252, 246, 235), outline=(212, 174, 97, 220), width=2)

    # Slot 1 Box
    draw.rounded_rectangle([dock_x + 40, dock_y + 35, dock_x + 360, dock_y + 125], radius=16, fill=(245, 238, 225, 255), outline=(168, 120, 38, 255), width=2)
    draw.ellipse([dock_x + 60, dock_y + 55, dock_x + 110, dock_y + 105], fill=(168, 120, 38, 255))
    draw.text((dock_x + 77, dock_y + 68), "L", font=get_font(20, bold=True), fill=(255, 255, 255, 255))
    draw.text((dock_x + 130, dock_y + 52), "TANGAN KIRI", font=get_font(12, bold=True), fill=(168, 120, 38, 255))
    draw.text((dock_x + 130, dock_y + 75), "Wayang 01", font=get_font(18, bold=True, serif=True), fill=(53, 41, 29, 255))

    # Slot 2 Box
    draw.rounded_rectangle([dock_x + 390, dock_y + 35, dock_x + 710, dock_y + 125], radius=16, fill=(245, 238, 225, 255), outline=(168, 120, 38, 255), width=2)
    draw.ellipse([dock_x + 410, dock_y + 55, dock_x + 460, dock_y + 105], fill=(168, 120, 38, 255))
    draw.text((dock_x + 427, dock_y + 68), "R", font=get_font(20, bold=True), fill=(255, 255, 255, 255))
    draw.text((dock_x + 480, dock_y + 52), "TANGAN KANAN", font=get_font(12, bold=True), fill=(168, 120, 38, 255))
    draw.text((dock_x + 480, dock_y + 75), "Wayang 03", font=get_font(18, bold=True, serif=True), fill=(53, 41, 29, 255))

    # Start button
    sbtn_x, sbtn_y, sbtn_w, sbtn_h = dock_x + dock_w - 280, dock_y + 50, 240, 60
    draw.rounded_rectangle([sbtn_x, sbtn_y, sbtn_x + sbtn_w, sbtn_y + sbtn_h], radius=30, fill=(183, 138, 53, 255), outline=(132, 96, 28, 255), width=2)
    draw.text((sbtn_x + 32, sbtn_y + 18), "MULAI BERMAIN  →", font=get_font(16, bold=True), fill=(255, 250, 241, 255))

    im.convert('RGB').save(os.path.join(OUTPUT_DIR, 'fig04_ui_selection.png'), quality=95)
    print("Fig 4 created")

# -------------------------------------------------------------
# FIG 5: Multi-Rate Pipeline & Camera Adaptation (Matplotlib)
# -------------------------------------------------------------
def create_fig05_camera_adaptation():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=150)
    fig.patch.set_facecolor('#F8F5EE')
    ax.set_facecolor('#F8F5EE')

    ax.text(0.5, 0.94, "PIPELINE ADAPTIF & PENJADWALAN FRAME MULTI-RATE", 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#35291D')
    ax.text(0.5, 0.88, "Sinkronisasi Kamera 24 FPS, Inferensi MediaPipe 12-20 FPS, dan WebGL Visual 30 FPS", 
            ha='center', va='center', fontsize=10, color='#776A5C')

    # Draw 3 parallel timeline lanes
    lanes = [
        ("1. Input Kamera Fisik (24 FPS)", 0.65, "#E28743", 24),
        ("2. MediaPipe Task Vision (15-20 FPS Adaptif)", 0.42, "#2C5E8A", 18),
        ("3. PixiJS WebGL Render (Capped 30 FPS)", 0.18, "#2E7D32", 30)
    ]

    for title, y, col, rate in lanes:
        ax.plot([0.15, 0.92], [y, y], color='#D0C8B8', lw=3, zorder=1)
        ax.text(0.13, y, title, ha='right', va='center', fontsize=10, fontweight='bold', color='#35291D')
        
        # pulses along the line
        num_ticks = int(rate * 0.7)
        xs = np.linspace(0.18, 0.90, num_ticks)
        for x in xs:
            ax.scatter(x, y, s=90, color=col, zorder=3, edgecolors='#FFFFFF', linewidths=1.5)
            # small tick
            ax.plot([x, x], [y - 0.03, y + 0.03], color=col, lw=2, zorder=2)

    # Interpolation connector arrows from MediaPipe to PixiJS
    mp_xs = np.linspace(0.18, 0.90, int(18 * 0.7))
    for mx in mp_xs[::2]:
        ax.annotate("", xy=(mx + 0.02, 0.22), xytext=(mx, 0.38),
                    arrowprops=dict(arrowstyle="->", color='#8C621D', lw=1.2, linestyle=':'))

    # Annotation box for explanation
    rect = patches.FancyBboxPatch((0.15, 0.02), 0.75, 0.09, boxstyle="round,pad=0.01",
                                  facecolor='#FFFDF8', edgecolor='#A87826', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.525, 0.065, "Keuntungan Multi-Rate: Beban komputasi AI turun 40-50%, panas perangkat terjaga stabil,\nsedangkan gerakan wayang di layar tetap halus 30 FPS berkat interpolasi alpha eksponensial.",
            ha='center', va='center', fontsize=9, color='#35291D')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig05_camera_adaptation.png'), dpi=180, facecolor=fig.get_facecolor())
    plt.close()
    print("Fig 5 created")

# -------------------------------------------------------------
# FIG 6: MediaPipe 21 Hand Landmarks Diagram (Matplotlib)
# -------------------------------------------------------------
def create_fig06_landmarks():
    fig, ax = plt.subplots(figsize=(10, 8), dpi=160)
    fig.patch.set_facecolor('#F8F5EE')
    ax.set_facecolor('#F8F5EE')

    ax.text(0.5, 0.96, "21 TITIK LANDMARK MEDIAPIPE & PEMETAAN KONTROL", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#35291D')
    ax.text(0.5, 0.92, "Struktur Kerangka Tangan, Palm Center Averaging, dan Kontrol Lengan Wayang", 
            ha='center', va='center', fontsize=9.5, color='#776A5C')

    # Coordinates roughly matching a front open hand
    # 0: Wrist
    pts = {
        0: (0.45, 0.15),
        # Thumb
        1: (0.35, 0.25), 2: (0.28, 0.35), 3: (0.24, 0.44), 4: (0.20, 0.52),
        # Index
        5: (0.36, 0.48), 6: (0.33, 0.60), 7: (0.31, 0.70), 8: (0.29, 0.78),
        # Middle
        9: (0.45, 0.50), 10: (0.45, 0.65), 11: (0.45, 0.76), 12: (0.45, 0.85),
        # Ring
        13: (0.54, 0.47), 14: (0.56, 0.59), 15: (0.57, 0.68), 16: (0.58, 0.76),
        # Pinky
        17: (0.63, 0.42), 18: (0.67, 0.52), 19: (0.70, 0.60), 20: (0.72, 0.68),
    }

    bones = [
        (0,1), (1,2), (2,3), (3,4),
        (0,5), (5,6), (6,7), (7,8),
        (0,9), (9,10), (10,11), (11,12),
        (0,13), (13,14), (14,15), (15,16),
        (0,17), (17,18), (18,19), (19,20),
        (5,9), (9,13), (13,17)
    ]

    for p1, p2 in bones:
        x1, y1 = pts[p1]
        x2, y2 = pts[p2]
        ax.plot([x1, x2], [y1, y2], color='#BDB09E', lw=2.5, zorder=1)

    # Highlight Palm Center points [0, 5, 9, 13, 17]
    palm_pts = [0, 5, 9, 13, 17]
    px = sum(pts[i][0] for i in palm_pts) / 5
    py = sum(pts[i][1] for i in palm_pts) / 5

    # Connect palm polygon
    poly = patches.Polygon([pts[i] for i in [0, 5, 9, 13, 17]], closed=True,
                           facecolor='#D4AE61', alpha=0.25, edgecolor='#A87826', lw=1.5, zorder=2)
    ax.add_patch(poly)

    # Draw nodes
    for i, (x, y) in pts.items():
        if i == 8: # Index tip
            col = '#D32F2F'
            sz = 140
        elif i == 12: # Middle tip
            col = '#1976D2'
            sz = 140
        elif i in palm_pts:
            col = '#A87826'
            sz = 100
        else:
            col = '#554433'
            sz = 70
        ax.scatter(x, y, s=sz, color=col, zorder=4, edgecolors='#FFFFFF', linewidths=1.5)
        ax.text(x + 0.018, y, str(i), fontsize=8, fontweight='bold', color='#221100', zorder=5)

    # Mark Palm Center
    ax.scatter(px, py, s=180, color='#FF9800', marker='*', zorder=6, edgecolors='#332211', linewidths=1.5)
    ax.text(px + 0.02, py - 0.03, "Palm Center\n(Average 0,5,9,13,17)", fontsize=8, fontweight='bold', color='#A87826')

    # Annotations for finger controllers
    ax.annotate("JARI TELUNJUK (#8)\nPengendali Lengan Utama / Kiri\nGainX: 4.0, GainY: 4.0",
                xy=pts[8], xytext=(0.08, 0.82),
                arrowprops=dict(arrowstyle="->", color='#D32F2F', lw=2),
                fontsize=8.5, fontweight='bold', color='#D32F2F',
                bbox=dict(boxstyle="round,pad=0.4", fc="#FFF0F0", ec="#D32F2F", lw=1.2))

    ax.annotate("JARI TENGAH (#12)\nPengendali Lengan Kedua / Kanan\nGainX: 2.5, GainY: 2.5",
                xy=pts[12], xytext=(0.60, 0.85),
                arrowprops=dict(arrowstyle="->", color='#1976D2', lw=2),
                fontsize=8.5, fontweight='bold', color='#1976D2',
                bbox=dict(boxstyle="round,pad=0.4", fc="#F0F6FF", ec="#1976D2", lw=1.2))

    ax.annotate("KEMIRINGAN TELAPAK (ROTASI TUBUH)\nSudut Vektor Pergelangan (0) ke Pangkal Jari Tengah (9)\natan2(-(x9 - x0), y0 - y9)",
                xy=((pts[0][0]+pts[9][0])/2, (pts[0][1]+pts[9][1])/2), xytext=(0.48, 0.28),
                arrowprops=dict(arrowstyle="->", color='#35291D', lw=1.5),
                fontsize=8, fontweight='bold', color='#35291D',
                bbox=dict(boxstyle="round,pad=0.4", fc="#FFFDF8", ec="#A87826", lw=1))

    ax.set_xlim(0.02, 0.98)
    ax.set_ylim(0.08, 0.98)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig06_mediapipe_landmarks.png'), dpi=180, facecolor=fig.get_facecolor())
    plt.close()
    print("Fig 6 created")

# -------------------------------------------------------------
# FIG 7: Two-Bone IK Geometry (Matplotlib)
# -------------------------------------------------------------
def create_fig07_twobone_ik():
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=160)
    fig.patch.set_facecolor('#F8F5EE')
    ax.set_facecolor('#F8F5EE')

    ax.text(0.5, 0.96, "GEOMETRI DUA-TULANG INVERSE KINEMATICS (TwoBoneIK)", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#35291D')
    ax.text(0.5, 0.92, "Formulasi Hukum Cosinus, Arah Tekukan Siku, dan Batasan Ruang Jangkauan", 
            ha='center', va='center', fontsize=9.5, color='#776A5C')

    # Points
    S = (0.25, 0.65)   # Shoulder
    E = (0.50, 0.78)   # Elbow
    T = (0.75, 0.42)   # Target Hand

    # Draw bones
    ax.plot([S[0], E[0]], [S[1], E[1]], color='#2C5E8A', lw=4, label='Upper Arm (L1)', zorder=2)
    ax.plot([E[0], T[0]], [E[1], T[1]], color='#D32F2F', lw=4, label='Forearm/Hand (L2)', zorder=2)
    # Direct reach line
    ax.plot([S[0], T[0]], [S[1], T[1]], color='#8C621D', lw=2, linestyle='--', label='Distance (D)', zorder=1)

    # Nodes
    ax.scatter(*S, s=150, color='#2C5E8A', zorder=4, edgecolors='#FFF', lw=2)
    ax.scatter(*E, s=150, color='#E28743', zorder=4, edgecolors='#FFF', lw=2)
    ax.scatter(*T, s=180, color='#D32F2F', marker='X', zorder=4, edgecolors='#FFF', lw=2)

    ax.text(S[0] - 0.03, S[1] - 0.05, "Bahu (Shoulder Ps)\n(xs, ys)", fontsize=9, fontweight='bold', color='#2C5E8A')
    ax.text(E[0], E[1] + 0.04, "Siku (Elbow Pe)\nSudut β", fontsize=9, fontweight='bold', color='#E28743', ha='center')
    ax.text(T[0] + 0.02, T[1], "Target Tangan Pt\n(xt, yt)", fontsize=9, fontweight='bold', color='#D32F2F')

    # Formulas in a nice box
    formula_text = (
        r"$\mathbf{Hukum\ Cosinus\ Sudut\ Siku:}$" + "\n"
        r"$\cos(\beta) = \mathrm{clamp}\left(\frac{D^2 - L_1^2 - L_2^2}{2 \cdot L_1 \cdot L_2}, -1, 1\right)$" + "\n\n"
        r"$\mathbf{Tekukan\ Siku\ (Elbow\ Bend):}$" + "\n"
        r"$\beta = \mathrm{elbowDirection} \cdot \arccos(\cos\beta), \quad (\mathrm{elbowDirection} \in \{+1, -1\})$" + "\n\n"
        r"$\mathbf{Rotasi\ Lengan\ Atas\ (Shoulder):}$" + "\n"
        r"$\theta_1 = \mathrm{atan2}(\Delta y, \Delta x) - \mathrm{atan2}(L_2 \sin\beta, L_1 + L_2 \cos\beta)$" + "\n\n"
        r"$\mathbf{Batas\ Annulus\ Jangkauan:}$" + "\n"
        r"$|L_1 - L_2| \leq D \leq (L_1 + L_2)$"
    )
    rect = patches.FancyBboxPatch((0.10, 0.04), 0.80, 0.32, boxstyle="round,pad=0.015",
                                  facecolor='#FFFDF8', edgecolor='#A87826', linewidth=1.5, zorder=2)
    ax.add_patch(rect)
    ax.text(0.50, 0.20, formula_text, ha='center', va='center', fontsize=9.5, color='#35291D')

    ax.set_xlim(0.05, 0.95)
    ax.set_ylim(0.02, 0.98)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig07_twobone_ik_geometry.png'), dpi=180, facecolor=fig.get_facecolor())
    plt.close()
    print("Fig 7 created")

# -------------------------------------------------------------
# FIG 8: Wayang Rigging & Scenegraph Breakdown (PIL)
# -------------------------------------------------------------
def create_fig08_rigging_breakdown():
    width, height = 1200, 750
    im = Image.new('RGBA', (width, height), (248, 245, 238, 255))
    draw = ImageDraw.Draw(im)

    # Title
    draw.text((width//2, 35), "ANATOMI RIGGING & PECAHAN ASET WAYANG 01", font=get_font(22, bold=True), fill=(53, 41, 29, 255), anchor="mm")
    draw.text((width//2, 65), "Struktur Lapisan (Layers): Main Rod, Body, Upper Arm, Forearm & Pivot Points", font=get_font(13), fill=(119, 106, 92, 255), anchor="mm")

    # Left: Isolated Part Cards
    parts = [
        ("main_rod.png", "Gagang Cempurit\n(Main Rod)", 60, 110, 120, 360),
        ("body.png", "Badan & Mahkota\n(Body)", 200, 110, 240, 360),
        ("left_upper_arm.png", "Lengan Atas Kiri\n(Upper Arm)", 460, 110, 150, 170),
        ("left_forearm_hand.png", "Lengan Bawah & Jari\n(Forearm Hand)", 460, 300, 150, 170),
        ("right_upper_arm.png", "Lengan Atas Kanan\n(Upper Arm)", 630, 110, 150, 170),
        ("right_forearm_hand.png", "Lengan Bawah Kanan\n(Forearm Hand)", 630, 300, 150, 170),
    ]

    for fname, label, px, py, pw, ph in parts:
        draw.rounded_rectangle([px, py, px + pw, py + ph], radius=14, fill=(255, 252, 246, 220), outline=(212, 174, 97, 180), width=1)
        fpath = f'/opt/lampp/htdocs/landingpage/wayang/assett/wayang01/{fname}'
        if os.path.exists(fpath):
            pimg = Image.open(fpath).convert('RGBA')
            aspect = pimg.width / pimg.height
            h = ph - 55
            w = int(h * aspect)
            if w > pw - 20:
                w = pw - 20
                h = int(w / aspect)
            pimg = pimg.resize((w, h), Image.Resampling.LANCZOS)
            im.alpha_composite(pimg, (px + (pw - w)//2, py + 10))
        draw.text((px + pw//2, py + ph - 25), label, font=get_font(10, bold=True), fill=(83, 65, 45, 255), anchor="mm")

    # Right: Scenegraph Hierarchy Box
    hx, hy, hw, hh = 800, 110, 350, 360
    draw.rounded_rectangle([hx, hy, hx + hw, hy + hh], radius=18, fill=(255, 250, 240, 240), outline=(168, 120, 38, 255), width=2)
    draw.text((hx + hw//2, hy + 28), "HIERARKI CONTAINER PIXI.JS", font=get_font(13, bold=True), fill=(168, 120, 38, 255), anchor="mm")

    tree = [
        "Stage (Pixi Application)",
        " └── ViewportFraming (Scale & Letterbox)",
        "      └── WayangRoot (Pivot: 512, 1000)",
        "           ├── MainRod Sprite (Layer 0)",
        "           ├── Shoulder Container (Kiri)",
        "           │    ├── UpperArm Sprite",
        "           │    └── Elbow Container",
        "           │         └── ForearmHand Sprite",
        "           ├── Body Sprite (Layer 2)",
        "           └── Shoulder Container (Kanan)",
        "                ├── UpperArm Sprite",
        "                └── Elbow Container",
        "                     └── ForearmHand Sprite"
    ]
    ty = hy + 60
    for line in tree:
        draw.text((hx + 20, ty), line, font=get_font(11, mono=True), fill=(53, 41, 29, 255))
        ty += 22

    # Bottom Pivot Table Summary
    bx, by, bw, bh = 60, 500, width - 120, 210
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(255, 252, 246, 240), outline=(212, 174, 97, 200), width=1)
    draw.text((bx + 30, by + 25), "KOORDINAT PIVOT LOGIS (Canvas 1024 × 1365):", font=get_font(12, bold=True), fill=(168, 120, 38, 255))

    pivots = [
        "• Root Pivot: (512, 1000) — Titik tumpu pegangan dalang pada cempurit bambu.",
        "• Lengan Kiri (Left Arm): Shoulder (600, 627) | Elbow (412, 697) | Hand Anchor (219, 684) | Index Finger Gain: 4.0",
        "• Lengan Kanan (Right Arm): Shoulder (600, 627) | Elbow (793, 650) | Hand Anchor (798, 824) | Middle Finger Gain: 2.5",
        "• Batas Perputaran Sendi: Bahu (-0.8 s/d +0.8 rad) | Siku (-1.2 s/d +1.2 rad) | Body Tilt: gain 0.2, max ±π/12 rad.",
        "• Prinsip Tanpa Distorsi: Seluruh tekstur dipetakan penuh (full-canvas alignment) tanpa cropping atau skewing independen."
    ]
    pty = by + 55
    for p in pivots:
        draw.text((bx + 30, pty), p, font=get_font(12), fill=(65, 52, 38, 255))
        pty += 28

    im.convert('RGB').save(os.path.join(OUTPUT_DIR, 'fig08_puppet_rigging_scenegraph.png'), quality=95)
    print("Fig 8 created")

# -------------------------------------------------------------
# FIG 9: UI Gameplay & Stage HUD Mockup
# -------------------------------------------------------------
def create_fig09_ui_gameplay():
    width, height = 1280, 720
    bg_path = '/opt/lampp/htdocs/landingpage/wayang/assett/BG.jpg'
    if os.path.exists(bg_path):
        im = Image.open(bg_path).convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
    else:
        im = Image.new('RGBA', (width, height), (238, 232, 220, 255))
    draw = ImageDraw.Draw(im)

    # Place two wayang puppets on stage
    # Left Puppet: Wayang 01
    p1 = '/opt/lampp/htdocs/landingpage/wayang/assett/wayang01/reference.png'
    if os.path.exists(p1):
        w1 = Image.open(p1).convert('RGBA')
        aspect1 = w1.width / w1.height
        h1 = 580
        w1 = w1.resize((int(h1 * aspect1), h1), Image.Resampling.LANCZOS)
        im.alpha_composite(w1, (240, 110))

    # Right Puppet: Wayang 03
    p3 = '/opt/lampp/htdocs/landingpage/wayang/assett/wayang03/refrence.png'
    if not os.path.exists(p3):
        p3 = '/opt/lampp/htdocs/landingpage/wayang/assett/wayang03/reference.png'
    if os.path.exists(p3):
        w3 = Image.open(p3).convert('RGBA')
        # Mirror slightly for face-off stance
        w3 = w3.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        aspect3 = w3.width / w3.height
        h3 = 580
        w3 = w3.resize((int(h3 * aspect3), h3), Image.Resampling.LANCZOS)
        im.alpha_composite(w3, (640, 110))

    # Top HUD Bar (Glass Panel)
    hud_w, hud_h = 1160, 68
    hud_x, hud_y = 60, 20
    hud = Image.new('RGBA', (hud_w, hud_h), (255, 252, 246, 215))
    hdraw = ImageDraw.Draw(hud)
    hdraw.rounded_rectangle([0, 0, hud_w, hud_h], radius=34, outline=(255, 255, 255, 230), width=2)
    im.alpha_composite(hud, (hud_x, hud_y))

    # Back button
    draw.rounded_rectangle([hud_x + 15, hud_y + 12, hud_x + 160, hud_y + 56], radius=22, fill=(245, 240, 230, 255), outline=(168, 120, 38, 180), width=1)
    draw.text((hud_x + 35, hud_y + 26), "← MENU UTAMA", font=get_font(11, bold=True), fill=(53, 41, 29, 255))

    # Center phase indicator & green live dot
    draw.ellipse([hud_x + 220, hud_y + 28, hud_x + 232, hud_y + 40], fill=(46, 125, 50, 255))
    draw.text((hud_x + 242, hud_y + 24), "Sedang bermain", font=get_font(14, bold=True), fill=(53, 41, 29, 255))
    draw.text((hud_x + 380, hud_y + 26), "• Tangan kiri: Wayang 01   • Tangan kanan: Wayang 03", font=get_font(12), fill=(119, 106, 92, 255))

    # Timer in center right
    draw.rounded_rectangle([hud_x + 820, hud_y + 14, hud_x + 920, hud_y + 54], radius=20, fill=(168, 120, 38, 240))
    draw.text((hud_x + 845, hud_y + 24), "2:45", font=get_font(18, bold=True, mono=True), fill=(255, 255, 255, 255))

    # Change Wayang button
    draw.rounded_rectangle([hud_x + 940, hud_y + 12, hud_x + 1140, hud_y + 56], radius=22, fill=(245, 240, 230, 255), outline=(168, 120, 38, 180), width=1)
    draw.text((hud_x + 975, hud_y + 26), "GANTI WAYANG", font=get_font(11, bold=True), fill=(53, 41, 29, 255))

    # Bottom-left camera preview box (mirrored video style)
    cam_w, cam_h = 180, 135
    cam_x, cam_y = 30, height - 165
    draw.rounded_rectangle([cam_x, cam_y, cam_x + cam_w, cam_y + cam_h], radius=14, fill=(20, 18, 16, 230), outline=(212, 174, 97, 240), width=2)
    # Simulated skeletal overlay inside camera box
    draw.text((cam_x + 15, cam_y + 12), "LIVE CAMERA (MIRRORED)", font=get_font(8, bold=True), fill=(212, 174, 97, 255))
    # Two hand skeleton representations
    for hx_off in [40, 120]:
        draw.ellipse([cam_x + hx_off, cam_y + 95, cam_x + hx_off + 8, cam_y + 103], fill=(0, 255, 128, 255))
        draw.line([(cam_x + hx_off + 4, cam_y + 95), (cam_x + hx_off + 4, cam_y + 60)], fill=(0, 255, 128, 200), width=2)
        draw.line([(cam_x + hx_off + 4, cam_y + 60), (cam_x + hx_off - 12, cam_y + 40)], fill=(0, 255, 128, 200), width=2)
        draw.line([(cam_x + hx_off + 4, cam_y + 60), (cam_x + hx_off + 12, cam_y + 38)], fill=(0, 255, 128, 200), width=2)
        draw.ellipse([cam_x + hx_off - 14, cam_y + 36, cam_x + hx_off - 8, cam_y + 42], fill=(255, 80, 80, 255)) # Index tip
        draw.ellipse([cam_x + hx_off + 10, cam_y + 34, cam_x + hx_off + 16, cam_y + 40], fill=(80, 150, 255, 255)) # Middle tip

    # Status toast notification at bottom center
    toast_w, toast_h = 560, 42
    toast_x, toast_y = (width - toast_w)//2, height - 60
    draw.rounded_rectangle([toast_x, toast_y, toast_x + toast_w, toast_y + toast_h], radius=21, fill=(255, 252, 246, 230), outline=(168, 120, 38, 200), width=1)
    draw.ellipse([toast_x + 20, toast_y + 16, toast_x + 30, toast_y + 26], fill=(46, 125, 50, 255))
    draw.text((toast_x + 40, toast_y + 13), "Pelacakan aktif: Tangan kiri mengontrol Wayang 01, Tangan kanan Wayang 03", font=get_font(11, bold=True), fill=(53, 41, 29, 255))

    im.convert('RGB').save(os.path.join(OUTPUT_DIR, 'fig09_ui_gameplay_hud.png'), quality=95)
    print("Fig 9 created")

# -------------------------------------------------------------
# FIG 10: PWA Offline Caching & Concurrency Queue (Matplotlib)
# -------------------------------------------------------------
def create_fig10_pwa_queue():
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=150)
    fig.patch.set_facecolor('#F8F5EE')
    ax.set_facecolor('#F8F5EE')

    ax.text(0.5, 0.95, "ARSITEKTUR OFFLINE PWA, SERVICE WORKER & ANTREAN SERVER (queue.php)", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#35291D')
    ax.text(0.5, 0.90, "Proteksi Bandwidth Server Pameran dan Pemuatan Seketika (Instant Load) Tanpa Koneksi Internet", 
            ha='center', va='center', fontsize=9.5, color='#776A5C')

    # Boxes:
    # 1. User Browser / PWA Client
    # 2. Service Worker (sw.js)
    # 3. Cache Storage (wayang-app-vX)
    # 4. Concurrency Queue (queue.php)
    # 5. Apache / Static Asset Server
    b_client = (0.05, 0.50, 0.22, 0.30)
    b_sw = (0.37, 0.50, 0.25, 0.30)
    b_cache = (0.72, 0.50, 0.23, 0.30)
    b_queue = (0.20, 0.10, 0.28, 0.26)
    b_srv = (0.58, 0.10, 0.30, 0.26)

    def draw_box(b, title, lines, col):
        x, y, w, h = b
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                      facecolor='#FFFDF8', edgecolor=col, linewidth=2, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.04, title, ha='center', va='center', fontsize=10.5, fontweight='bold', color=col, zorder=3)
        ax.text(x + w/2, y + h/2 - 0.02, "\n".join(lines), ha='center', va='center', fontsize=8.5, color='#35291D', zorder=3)

    draw_box(b_client, "1. Browser Client (bootstrap.ts)", 
             ["Cek localStorage versionKey", "Progress bar unduhan 0-100%", "Worker ganda paralel fetch", "Session Heartbeat 15s"], "#A87826")
    
    draw_box(b_sw, "2. Service Worker (sw.js)", 
             ["Scope: '/' (PWA registered)", "Cache-First Routing", "USE_CACHE message handler", "Bypass server saat offline"], "#2C5E8A")

    draw_box(b_cache, "3. Cache Storage (Browser)", 
             ["wayang-app-{version}", "Model Wasm & Task (~13 MB)", "Sprite Tekstur 5 Wayang", "Zero Latency Loading"], "#2E7D32")

    draw_box(b_queue, "4. Antrean Server (queue.php)", 
             ["Token Bucket Concurrency", "Max 3 unduhan aktif serentak", "File Lock atomic (flock)", "TTL 45 detik auto-cleanup"], "#B71C1C")

    draw_box(b_srv, "5. Web Server (Apache/Static)", 
             ["asset-manifest.json", "models/hand_landmarker.task", "mediapipe/wasm binaries", "HTTP range & keepalive"], "#5D4037")

    # Arrows
    # Client -> SW
    ax.annotate("", xy=(0.37, 0.65), xytext=(0.27, 0.65), arrowprops=dict(arrowstyle="->", color='#2C5E8A', lw=2))
    ax.text(0.32, 0.68, "Intercept", fontsize=8, color='#2C5E8A', ha='center')

    # SW -> Cache
    ax.annotate("", xy=(0.72, 0.65), xytext=(0.62, 0.65), arrowprops=dict(arrowstyle="<->", color='#2E7D32', lw=2))
    ax.text(0.67, 0.68, "Match / Put", fontsize=8, color='#2E7D32', ha='center')

    # Client -> Queue (If cache miss)
    ax.annotate("", xy=(0.30, 0.36), xytext=(0.18, 0.50), arrowprops=dict(arrowstyle="->", color='#B71C1C', lw=2, linestyle='--'))
    ax.text(0.18, 0.41, "Cache Miss:\nJoin Queue", fontsize=8, color='#B71C1C', ha='center')

    # Queue -> Srv (Admitted)
    ax.annotate("", xy=(0.58, 0.23), xytext=(0.48, 0.23), arrowprops=dict(arrowstyle="->", color='#A87826', lw=2))
    ax.text(0.53, 0.26, "Admitted\nPosition <= 3", fontsize=8, color='#A87826', ha='center')

    # Srv -> Cache (Download & Store)
    ax.annotate("", xy=(0.80, 0.50), xytext=(0.75, 0.36), arrowprops=dict(arrowstyle="->", color='#2E7D32', lw=2))
    ax.text(0.83, 0.42, "Stream Assets\nto Cache", fontsize=8, color='#2E7D32', ha='center')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig10_pwa_queue_cache.png'), dpi=180, facecolor=fig.get_facecolor())
    plt.close()
    print("Fig 10 created")

if __name__ == '__main__':
    create_fig01_cover()
    create_fig02_architecture()
    create_fig03_ui_home()
    create_fig04_ui_selection()
    create_fig05_camera_adaptation()
    create_fig06_landmarks()
    create_fig07_twobone_ik()
    create_fig08_rigging_breakdown()
    create_fig09_ui_gameplay()
    create_fig10_pwa_queue()
    print("All 10 figures created successfully!")
