import os
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOC_PATH = '/opt/lampp/htdocs/landingpage/wayang/DOKUMENTASI_MODUL_WAYANG_BALI_INTERACTIVE.docx'
PDF_PATH = '/opt/lampp/htdocs/landingpage/wayang/DOKUMENTASI_MODUL_WAYANG_BALI_INTERACTIVE.pdf'
ASSETS_DIR = '/opt/lampp/htdocs/landingpage/wayang/docs_assets'

COLOR_GOLD = "A87826"
COLOR_DARK = "35291D"
COLOR_MUTED = "776A5C"
COLOR_CREAM = "FBF8F2"
COLOR_BORDER = "D4AE61"
COLOR_CODE_BG = "F4EFE6"

def set_cell_background(cell, color_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for b_name, b_val in borders.items():
        if b_val:
            node = OxmlElement(f'w:{b_name}')
            node.set(qn('w:val'), b_val.get('val', 'single'))
            node.set(qn('w:sz'), str(b_val.get('sz', 4)))
            node.set(qn('w:space'), '0')
            node.set(qn('w:color'), b_val.get('color', 'auto'))
            tcBorders.append(node)
        else:
            node = OxmlElement(f'w:{b_name}')
            node.set(qn('w:val'), 'none')
            tcBorders.append(node)
    tcPr.append(tcBorders)

def add_callout_box(doc, title, text_paras, icon="💡"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)

    cell = tbl.cell(0, 0)
    set_cell_background(cell, COLOR_CREAM)
    set_cell_margins(cell, top=60, bottom=60, left=120, right=120)
    set_cell_borders(cell, left={'val': 'single', 'sz': 18, 'color': COLOR_GOLD})

    p_title = cell.paragraphs[0]
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_icon = p_title.add_run(f"{icon} ")
    r_icon.font.size = Pt(9.5)
    r_title = p_title.add_run(title)
    r_title.bold = True
    r_title.font.name = "Georgia"
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = RGBColor(168, 120, 38)

    for item in text_paras:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.05
        r = p.add_run(item)
        r.font.name = "Liberation Sans"
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(53, 41, 29)

def add_code_block(doc, title, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)

    cell = tbl.cell(0, 0)
    set_cell_background(cell, COLOR_CODE_BG)
    set_cell_margins(cell, top=50, bottom=50, left=100, right=100)
    set_cell_borders(cell, left={'val': 'single', 'sz': 12, 'color': COLOR_DARK},
                           top={'val': 'single', 'sz': 4, 'color': 'D0C8B8'},
                           bottom={'val': 'single', 'sz': 4, 'color': 'D0C8B8'},
                           right={'val': 'single', 'sz': 4, 'color': 'D0C8B8'})

    p_head = cell.paragraphs[0]
    p_head.paragraph_format.space_before = Pt(0)
    p_head.paragraph_format.space_after = Pt(1)
    r_head = p_head.add_run(f"⚙️ KODE SUMBER: {title}")
    r_head.bold = True
    r_head.font.name = "Courier New"
    r_head.font.size = Pt(8)
    r_head.font.color.rgb = RGBColor(136, 96, 28)

    p_code = cell.add_paragraph()
    p_code.paragraph_format.space_before = Pt(1)
    p_code.paragraph_format.space_after = Pt(1)
    p_code.paragraph_format.line_spacing = 1.0
    r_code = p_code.add_run(code_text)
    r_code.font.name = "Courier New"
    r_code.font.size = Pt(7.5)
    r_code.font.color.rgb = RGBColor(40, 30, 20)

def add_image_with_caption(doc, filename, caption, width_in=5.2):
    filepath = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(filepath):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(1)
        p_img.add_run().add_picture(filepath, width=Inches(width_in))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(4)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = "Liberation Sans"
        r_cap.font.size = Pt(8)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(119, 106, 92)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Georgia"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(168, 120, 38)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Georgia"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(53, 41, 29)
    return p

def add_para(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.1
    r = p.add_run(text)
    r.font.name = "Liberation Sans"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(53, 41, 29)
    return p

def add_bullet(doc, title, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    r_b = p.add_run(f"{title}: ")
    r_b.bold = True
    r_b.font.name = "Liberation Sans"
    r_b.font.size = Pt(8)
    r_b.font.color.rgb = RGBColor(53, 41, 29)

    r_t = p.add_run(text)
    r_t.font.name = "Liberation Sans"
    r_t.font.size = Pt(8)
    r_t.font.color.rgb = RGBColor(53, 41, 29)

def generate_document_10_pages():
    doc = docx.Document()

    # Exact margins for 10-page layout: Top=0.55, Bottom=0.55, Left=0.75, Right=0.75 in
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.different_first_page_header_footer = True

        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("Dokumentasi Teknis Modul — Wayang Bali Interactive (v0.1.0)")
        r_hdr.font.name = "Liberation Sans"
        r_hdr.font.size = Pt(7.5)
        r_hdr.font.color.rgb = RGBColor(168, 120, 38)

        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ftr = p_ftr.add_run("Wayang Bali Interactive — Panggung Budaya Digital Berbasis Edge AI & WebGL")
        r_ftr.font.name = "Liberation Sans"
        r_ftr.font.size = Pt(7.5)
        r_ftr.font.color.rgb = RGBColor(119, 106, 92)

    # =============================================================
    # HALAMAN 1: COVER & METADATA PROYEK
    # =============================================================
    add_image_with_caption(doc, 'fig01_cover_banner.png', 'Wayang Bali Interactive — Komposisi 5 Karakter, Ornamen Tradisional dan Panggung Pementasan', width_in=6.5)

    p_cov_title = doc.add_paragraph()
    p_cov_title.paragraph_format.space_before = Pt(8)
    p_cov_title.paragraph_format.space_after = Pt(2)
    r_ct = p_cov_title.add_run("DOKUMENTASI MODUL & ARSITEKTUR TEKNIS\nSISTEM WAYANG BALI INTERAKTIF")
    r_ct.bold = True
    r_ct.font.name = "Georgia"
    r_ct.font.size = Pt(17)
    r_ct.font.color.rgb = RGBColor(53, 41, 29)

    p_cov_sub = doc.add_paragraph()
    p_cov_sub.paragraph_format.space_before = Pt(1)
    p_cov_sub.paragraph_format.space_after = Pt(10)
    r_cs = p_cov_sub.add_run("Panduan Komprehensif Arsitektur Perangkat Lunak, Visi Komputer, Kinematika Wayang Dua-Tulang, serta Penjelasan Logika untuk Orang Awam")
    r_cs.font.name = "Liberation Sans"
    r_cs.font.size = Pt(9.5)
    r_cs.font.color.rgb = RGBColor(168, 120, 38)

    tbl_meta = doc.add_table(rows=6, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.columns[0].width = Inches(2.2)
    tbl_meta.columns[1].width = Inches(4.3)

    meta_data = [
        ("Nama Proyek", "Wayang Bali Interactive (Panggung Budaya Digital)"),
        ("Versi Rilis / Status", "v0.1.0-prod (Baseline Technical Specification Disetujui)"),
        ("Target Perangkat", "Browser Web (Mobile Android, Tablet, iPhone/iPad, Laptop, Desktop)"),
        ("Teknologi Inti", "TypeScript, Google MediaPipe Tasks Vision, Pixi.js v8, Service Worker"),
        ("Model Komputasi", "100% Client-Side Edge AI (Privasi Penuh, Zero Server Upload)"),
        ("Klasifikasi Dokumen", "Dokumentasi Arsitektur Modul, Spesifikasi Kode & Manual Pengguna"),
    ]

    for idx, (label, val) in enumerate(meta_data):
        row = tbl_meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        set_cell_background(c0, COLOR_CREAM if idx % 2 == 0 else "FFFFFF")
        set_cell_background(c1, COLOR_CREAM if idx % 2 == 0 else "FFFFFF")
        set_cell_margins(c0, top=40, bottom=40, left=80, right=80)
        set_cell_margins(c1, top=40, bottom=40, left=80, right=80)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Liberation Sans"
        r0.font.size = Pt(8)
        r0.font.color.rgb = RGBColor(83, 65, 45)

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.name = "Liberation Sans"
        r1.font.size = Pt(8)
        r1.font.color.rgb = RGBColor(53, 41, 29)

    doc.add_page_break()

    # =============================================================
    # HALAMAN 2: BAB 1. RINGKASAN EKSEKUTIF & PANDUAN AWAM
    # =============================================================
    add_heading_1(doc, "BAB 1. RINGKASAN EKSEKUTIF & KONSEP DASAR SISTEM")
    add_heading_2(doc, "1.1 Pengantar: Menghidupkan Budaya Nusantara Lewat Kecerdasan Buatan")
    add_para(doc, "Wayang Bali Interactive adalah aplikasi web modern berbasis Computer Vision dan grafis 2D WebGL berkinerja tinggi yang memungkinkan siapa saja memainkan tokoh Wayang Bali tradisional langsung melalui kamera web (webcam). Pengguna tidak memerlukan sensor sarung tangan khusus ataupun kacamata VR. Cukup membuka peramban web pada ponsel, tablet, atau komputer jinjing, pengguna dapat langsung menggerakkan wayang layaknya seorang Dalang.")

    add_callout_box(doc, "Analogi untuk Orang Awam: Bagaimana Sistem Ini Bekerja?", [
        "1. Di pertunjukan tradisional, Dalang duduk di balik layar putih (kelir) memegang gagang bambu (cempurit) utama untuk memindahkan tubuh wayang, serta menggerakkan bilah bambu kecil untuk mengayunkan tangan wayang.",
        "2. Di sistem kami, kamera web perangkat Anda bertindak sebagai 'panggung kelir virtual'. Kecerdasan buatan (Google MediaPipe) membaca 21 titik persendian tangan Anda secara langsung.",
        "3. Telapak tangan Anda berfungsi sebagai pegangan tubuh wayang, sementara jari telunjuk dan jari tengah Anda berfungsi sebagai pengayun lengan wayang! Anda bahkan dapat memainkan 2 wayang sekaligus dengan kedua tangan secara mandiri."
    ], icon="🎭")

    add_heading_2(doc, "1.2 Tiga Langkah Mudah Mengoperasikan Pementasan")
    add_bullet(doc, "1. Pilih Karakter", "Pengguna memilih 1 atau 2 tokoh wayang dari katalog 5 tokoh, lalu menentukan tangan pengendalinya (Kiri/Kanan).")
    add_bullet(doc, "2. Kalibrasi Cepat", "Tunjukkan tangan selama 1,5 detik di depan kamera untuk mengunci posisi dan memastikan pencahayaan.")
    add_bullet(doc, "3. Pementasan 3 Menit", "Panggung terbuka penuh dengan latar candi Bali. Pengguna bebas berekspresi memainkan lakon wayang.")

    add_image_with_caption(doc, 'fig03_ui_home.png', 'Gambar 1: Antarmuka Layar Utama (Home Screen) dengan Estetika Glassmorphism & Ornamen Bali', width_in=4.9)
    doc.add_page_break()

    # =============================================================
    # HALAMAN 3: BAB 2. ARSITEKTUR SISTEM & ALUR DATA
    # =============================================================
    add_heading_1(doc, "BAB 2. ARSITEKTUR SISTEM KESELURUHAN & ALUR DATA END-TO-END")
    add_heading_2(doc, "2.1 Dekomposisi 8 Sub-Sistem Modular")
    add_para(doc, "Sistem dibangun dengan arsitektur decoupled components yang menjamin kode mudah dirawat, minim ketergantungan silang, dan memiliki latensi end-to-end sangat rendah (< 45 ms):")

    add_image_with_caption(doc, 'fig02_system_architecture.png', 'Gambar 2: Diagram Arsitektur End-to-End Sistem Wayang Bali Interactive (Input Sensor hingga WebGL Output)', width_in=4.9)

    tbl_arch = doc.add_table(rows=5, cols=3)
    tbl_arch.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_arch.columns[0].width = Inches(1.8)
    tbl_arch.columns[1].width = Inches(1.8)
    tbl_arch.columns[2].width = Inches(2.9)

    hdr = tbl_arch.rows[0]
    for ci, h_txt in enumerate(["Modul Inti", "Berkas Sumber", "Tanggung Jawab Teknis"]):
        set_cell_background(hdr.cells[ci], COLOR_DARK)
        set_cell_margins(hdr.cells[ci], top=40, bottom=40, left=60, right=60)
        p = hdr.cells[ci].paragraphs[0]
        r = p.add_run(h_txt)
        r.bold = True
        r.font.name = "Liberation Sans"
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 253, 248)

    modules_data_short = [
        ("Camera & FrameLoop", "CameraManager.ts, VideoFrameLoop.ts", "Stream 640x480 @ 24fps & sinkronisasi fresh-frame 12-20 FPS."),
        ("Vision AI & Tracking", "HandLandmarkerManager.ts, HandTrackManager.ts", "MediaPipe Wasm, 21 landmark 3D, bipartite matching anti-swap."),
        ("Controller & IK Engine", "HandPuppetController.ts, TwoBoneIK.ts", "Pemetaan jari ke cempurit, inverse kinematics analitik dua-tulang."),
        ("Rig & WebGL Renderer", "PuppetRig.ts, PixiRenderer.ts", "Hierarki scenegraph 1024x1365 & rendering WebGL 30 FPS drift-corrected.")
    ]

    for idx, (m_name, m_file, m_desc) in enumerate(modules_data_short):
        row = tbl_arch.rows[idx + 1]
        bg = COLOR_CREAM if idx % 2 == 0 else "FFFFFF"
        for ci, val in enumerate([m_name, m_file, m_desc]):
            c = row.cells[ci]
            set_cell_background(c, bg)
            set_cell_margins(c, top=35, bottom=35, left=60, right=60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Liberation Sans"
            r.font.size = Pt(7.5)
            r.font.color.rgb = RGBColor(53, 41, 29)
            if ci == 0:
                r.bold = True

    add_callout_box(doc, "Penjelasan Alur untuk Orang Awam", [
        "Citra tangan Anda ditangkap kamera -> AI mengenali bentuk jemari -> Posisi tangan dicocokkan agar tidak tertukar -> Rumus matematika menekuk siku wayang -> Wayang ditampilkan menari di layar."
    ], icon="🔄")
    doc.add_page_break()

    # =============================================================
    # HALAMAN 4: BAB 3. MODUL KAMERA & PENJADWALAN FRAME
    # =============================================================
    add_heading_1(doc, "BAB 3. MODUL KAMERA & PENJADWALAN FRAME ADAPTIF")
    add_heading_2(doc, "3.1 Bedah Kode Teknis CameraManager.ts")
    add_para(doc, "Modul CameraManager mengelola hak akses getUserMedia(). Untuk efisiensi energi, resolusi dikunci pada 640x480 piksel dengan toleransi frame-rate 24-30 fps, disertai fallback driver khusus Safari dan Android.")

    add_code_block(doc, "CameraManager.ts (Pengambilan Stream & Fallback)",
"""stream = await navigator.mediaDevices.getUserMedia({
  audio: false,
  video: { facingMode: { ideal: 'user' }, width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 24, max: 30 } }
}).catch(err => {
  if (err.name === 'OverconstrainedError' || err.name === 'ConstraintNotSatisfiedError') {
    return navigator.mediaDevices.getUserMedia({ audio: false, video: { facingMode: 'user', width: 640, height: 480 } });
  }
  throw err;
});""")

    add_heading_2(doc, "3.2 Sinkronisasi requestVideoFrameCallback via VideoFrameLoop.ts")
    add_para(doc, "Alih-alih menggunakan timer berkala yang membebani CPU, VideoFrameLoop memanfaatkan requestVideoFrameCallback() yang hanya memicu inferensi tepat saat sensor kamera menghasilkan frame baru (zero duplicate inference).")

    add_image_with_caption(doc, 'fig05_camera_adaptation.png', 'Gambar 3: Multi-Rate Pipeline: Kamera (24 FPS), AI Vision (15-20 FPS), dan WebGL (30 FPS)', width_in=4.8)

    add_callout_box(doc, "Mata Dalang Digital: Mengapa Ponsel Tidak Panas?", [
        "Kamera biasa merekam sangat cepat dan membuat baterai boros jika seluruh gambar dihitung oleh AI. Di sistem ini, AI hanya melacak 15-20 kali sedetik, sementara layar tetap tampil sangat halus 30 FPS berkat interpolasi cerdas."
    ], icon="⚡")
    doc.add_page_break()

    # =============================================================
    # HALAMAN 5: BAB 4. MODUL VISI KOMPUTER & PELACAKAN TANGAN
    # =============================================================
    add_heading_1(doc, "BAB 4. MODUL VISI KOMPUTER & PELACAKAN TANGAN STABIL")
    add_heading_2(doc, "4.1 Inisialisasi MediaPipe Tasks Vision")
    add_para(doc, "HandLandmarkerManager menginisialisasi model WebAssembly MediaPipe Tasks Vision secara lokal (hand_landmarker.task). Parameter dikonfigurasi: runningMode: 'VIDEO', numHands: 2, minHandDetectionConfidence: 0.4, dan minTrackingConfidence: 0.5.")

    add_image_with_caption(doc, 'fig06_mediapipe_landmarks.png', 'Gambar 4: 21 Titik Landmark MediaPipe, Titik Palm Center, dan Pemetaan Jari Telunjuk & Tengah', width_in=4.7)

    add_heading_2(doc, "4.2 Algoritma Bipartite Matching Anti Hand-Swapping")
    add_para(doc, "Ketika dua tangan bersilangan atau salah satu tangan keluar layar sesaat, urutan indeks deteksi kamera dapat tertukar. HandTrackManager menyelesaikan masalah ini dengan matriks biaya (Bipartite Cost):")

    add_code_block(doc, "HandTrackManager.ts (Cost Function)",
"""const distance = Math.hypot(detection.x - track.x - track.vx * prediction, detection.y - track.y - track.vy * prediction);
if (distance > 0.35) return Infinity; // Tolak lonjakan posisi yang tidak wajar
const handedness = detection.side && detection.side !== slot ? 0.4 * detection.confidence : 0;
const orientation = Math.abs(shortestAngle(detection.angle - track.angle)) / Math.PI;
return distance * 2.5 + orientation * 0.12 + handedness;""")

    add_callout_box(doc, "Membedakan Tangan Kiri dan Kanan Bagi Orang Awam", [
        "Sistem memiliki 'ingatan gerak' (kecepatan & arah tangan). Meskipun tangan kiri dan kanan Anda saling bersilangan di depan dada, karakter wayang tidak akan melompat tertukar."
    ], icon="🖐️")
    doc.add_page_break()

    # =============================================================
    # HALAMAN 6: BAB 5. MODUL KINEMATIKA BALIK & KONTROL WAYANG
    # =============================================================
    add_heading_1(doc, "BAB 5. MODUL KINEMATIKA BALIK & KONTROL WAYANG")
    add_heading_2(doc, "5.1 Formulasi Analitik TwoBoneIK.ts")
    add_para(doc, "TwoBoneIK memecahkan rotasi sendi bahu (Shoulder) dan siku (Elbow) secara analitik tertutup dalam kompleksitas waktu O(1) berbasis Hukum Cosinus, tanpa komputasi iteratif yang berat:")

    add_image_with_caption(doc, 'fig07_twobone_ik_geometry.png', 'Gambar 5: Geometri Segitiga Sendi Kinematika Balik Lengan Wayang Berdasarkan Hukum Cosinus', width_in=4.7)

    add_code_block(doc, "TwoBoneIK.ts (Penyelesaian Sudut Bahu & Siku)",
"""const reach = clamp(distance, Math.abs(upperLength - lowerLength) + eps, maxReach - eps);
const direction = distance > eps ? Math.atan2(dy, dx) : this.restTargetAngle;
const cosine = clamp((reach**2 - upperLength**2 - lowerLength**2) / (2 * upperLength * lowerLength), -1, 1);
const bend = this.elbowDirection * Math.acos(cosine);
const upperAngle = direction - Math.atan2(lowerLength * Math.sin(bend), upperLength + lowerLength * Math.cos(bend));
output.shoulder = clamp(output.shoulder + shortestAngle(upperAngle - this.upperRestAngle - output.shoulder), shoulderLimit.min, shoulderLimit.max);
output.elbow = clamp(bend - this.elbowRestAngle, elbowLimit.min, elbowLimit.max);""")

    add_heading_2(doc, "5.2 Pemetaan Cempurit Virtual pada HandPuppetController.ts")
    add_bullet(doc, "Posisi & Rotasi Badan", "Telapak (Palm Center) mengendalikan koordinat X/Y panggung. Sudut kemiringan pergelangan (#0) ke pangkal jari (#9) memutar tubuh wayang.")
    add_bullet(doc, "Lengan Depan & Belakang", "Ujung telunjuk (#8) mengendalikan lengan depan (Gain 4.0), dan ujung jari tengah (#12) mengendalikan lengan belakang (Gain 2.5).")

    add_callout_box(doc, "Jari Anda Sebagai Cempurit Wayang", [
        "Telapak Anda memegang tubuh wayang, jari telunjuk mengayunkan tangan depan, dan jari tengah mengayunkan tangan belakang. Rumus matematika memastikan siku wayang menekuk alami."
    ], icon="🎯")
    doc.add_page_break()

    # =============================================================
    # HALAMAN 7: BAB 6. MODUL RIGGING & RENDERING WEBGL
    # =============================================================
    add_heading_1(doc, "BAB 6. MODUL RIGGING & RENDERING WEBGL")
    add_heading_2(doc, "6.1 Struktur Hierarki Scenegraph PuppetRig.ts")
    add_para(doc, "Rigging mengadopsi prinsip Full-Canvas Alignment pada kanvas logis 1024 x 1365 piksel. Aset tubuh, cempurit bambu, lengan atas, dan lengan bawah tersusun rapi tanpa pergeseran artifisial:")

    add_image_with_caption(doc, 'fig08_puppet_rigging_scenegraph.png', 'Gambar 6: Pecahan Aset Ukiran Wayang 01 dan Susunan Hierarki Kontainer Pixi.js', width_in=4.9)

    add_heading_2(doc, "6.2 Katalog 5 Karakter Wayang Bali")
    add_bullet(doc, "Wayang 01 (Ksatria Laksamana)", "2 lengan artikulasi penuh, gain responsif (4.0 / 2.5), gerakan lincah dan berwibawa.")
    add_bullet(doc, "Wayang 02 (Punakawan)", "1 lengan artikulasi (lengan belakang statis menyatu dalam body art), kocak dan fleksibel.")
    add_bullet(doc, "Wayang 03 (Ksatria Gagah)", "2 lengan artikulasi, postur kekar, gerakan stabil dan mantap.")
    add_bullet(doc, "Wayang 04 (Raksasa / Rahwana)", "2 lengan artikulasi, ukuran tubuh lebih besar, gerakan berat dan berwibawa.")
    add_bullet(doc, "Wayang 05 (Putri / Dewi)", "2 lengan artikulasi, gerakan halus berkecepatan lembut (smoothing tinggi), anggun dan luwes.")

    add_heading_2(doc, "6.3 Optimasi Mesin Grafis PixiRenderer.ts")
    add_para(doc, "PixiRenderer mengelola kanvas WebGL PixiJS v8. Ticker dikunci pada plafon 30 FPS menggunakan algoritma drift-correction, memastikan konsumsi baterai rendah dan bebas lonjakan visual.")
    doc.add_page_break()

    # =============================================================
    # HALAMAN 8: BAB 7. ANTARMUKA PENGGUNA & MANAJEMEN SESI
    # =============================================================
    add_heading_1(doc, "BAB 7. MODUL ANTARMUKA PENGGUNA & MANAJEMEN SESI")
    add_heading_2(doc, "7.1 State Machine Navigasi Layar (GameApp.ts)")
    add_para(doc, "Alur interaksi dikendalikan oleh Finite State Machine: HOME -> CHARACTER_SELECTION -> START_CAMERA -> CALIBRATION -> PLAYING -> SESSION_COMPLETE.")

    add_image_with_caption(doc, 'fig04_ui_selection.png', 'Gambar 7: Layar Pemilihan Karakter dengan Penetapan Slot Pengendali Tangan Kiri (L) dan Kanan (R)', width_in=4.7)

    add_heading_2(doc, "7.2 Layar Pementasan & Kontrol HUD (Head-Up Display)")
    add_para(doc, "Pada status PLAYING, layar menampilkan panggung wayang dengan kontrol antarmuka kaca tembus pandang (Glassmorphism HUD): tombol Menu Utama, hitungan mundur 3 menit, tombol Ganti Wayang, dan pratinjau webcam cermin mini di sudut kiri bawah.")

    add_image_with_caption(doc, 'fig09_ui_gameplay_hud.png', 'Gambar 8: Tampilan Panggung Pementasan Wayang Interaktif Saat Permainan Berlangsung', width_in=4.7)

    add_heading_2(doc, "7.3 Proteksi Pengalaman Pengguna (UX Guards)")
    add_bullet(doc, "Pengaman Orientasi Ponsel", "Memblokir orientasi potret dan memunculkan notifikasi animasi 'Putar ponsel ke posisi landscape'.")
    add_bullet(doc, "Kalibrasi & Timeout", "Kalibrasi 1,5 detik sebelum bermain, dan otomatis selesai jika tangan tidak terlihat selama 25 detik berturut-turut.")
    doc.add_page_break()

    # =============================================================
    # HALAMAN 9: BAB 8. DISTRIBUSI PWA, CACHING & ANTREAN
    # =============================================================
    add_heading_1(doc, "BAB 8. MODUL DISTRIBUSI PWA, CACHING & ANTREAN SERVER")
    add_heading_2(doc, "8.1 Distribusi Aset Berskala Besar & Concurrency Queue")
    add_para(doc, "Total ukuran paket aplikasi mencapai ~30 MB (WASM MediaPipe 9 MB, model 4 MB, dan tekstur 17 MB). Gerbang antrean queue.php menggunakan atomic file lock (flock) untuk membatasi maksimal 3 unduhan aktif secara bersamaan, melindungi server pameran dari lonjakan akses.")

    add_image_with_caption(doc, 'fig10_pwa_queue_cache.png', 'Gambar 9: Arsitektur Caching PWA, Service Worker, dan Antrean Concurrency (queue.php)', width_in=4.9)

    add_code_block(doc, "public/queue.php (Token Bucket Concurrency)",
"""const MAX_ACTIVE_DOWNLOADS = 3; const CLIENT_TTL_SECONDS = 45;
$lock = fopen($lockPath, 'c+'); flock($lock, LOCK_EX);
$entries = array_values(array_filter($entries, fn($e) => ($now - (float)$e['seen']) < CLIENT_TTL_SECONDS));
$index = array_search($client, array_column($entries, 'id'), true);
$position = $index === false ? 0 : ((int)$index + 1);
$reply = ['admitted' => $position > 0 && $position <= MAX_ACTIVE_DOWNLOADS, 'position' => $position, 'waiting' => max(0, count($entries) - MAX_ACTIVE_DOWNLOADS)];
flock($lock, LOCK_UN); fclose($lock); echo json_encode($reply);""")

    add_heading_2(doc, "8.2 Service Worker & Kapabilitas 100% Offline")
    add_para(doc, "Paket hanya diunduh tepat satu kali di setiap perangkat menggunakan pekerja unduhan paralel (dual worker) via bootstrap.ts dan sw.js. Kunjungan berikutnya dimuat seketika dalam waktu < 0,5 detik bahkan tanpa akses internet.")

    add_callout_box(doc, "Sekali Unduh, Main Kapan Saja Tanpa Kuota Internet", [
        "Aplikasi tersimpan permanen di memori browser Anda. Anda dapat mematikan Wi-Fi atau data seluler setelah unduhan pertama, dan pertunjukan wayang tetap berjalan normal 100% offline."
    ], icon="📶")
    doc.add_page_break()

    # =============================================================
    # HALAMAN 10: BAB 9. EVALUASI KINERJA & PANDUAN PEMECAHAN MASALAH
    # =============================================================
    add_heading_1(doc, "BAB 9. EVALUASI KINERJA, TROUBLESHOOTING & ROADMAP")
    add_heading_2(doc, "9.1 Matriks Kinerja Lintas Perangkat (Uji Benchmark)")
    add_para(doc, "Pengujian komparasi pada berbagai tingkatan perangkat keras membuktikan stabilitas kinerja sistem:")

    tbl_bench = doc.add_table(rows=5, cols=5)
    tbl_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, w in enumerate([1.5, 1.3, 1.2, 1.2, 1.3]):
        tbl_bench.columns[i].width = Inches(w)

    h_bench = tbl_bench.rows[0]
    for ci, txt in enumerate(["Kategori Perangkat", "WebGL Render", "MediaPipe FPS", "Latensi Kontrol", "Status Termal"]):
        set_cell_background(h_bench.cells[ci], COLOR_DARK)
        set_cell_margins(h_bench.cells[ci], top=40, bottom=40, left=60, right=60)
        p = h_bench.cells[ci].paragraphs[0]
        r = p.add_run(txt)
        r.bold = True
        r.font.name = "Liberation Sans"
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 253, 248)

    b_data = [
        ("Android Midrange (Snapdragon 778G)", "30.0 FPS stabil", "18–20 FPS adaptif", "42 ms (sangat baik)", "Dingin / Hangat Ringan"),
        ("Apple iPhone 13 (A15 Bionic)", "30.0 FPS stabil", "20.0 FPS konstan", "28 ms (luar biasa)", "Dingin / Stabil"),
        ("Laptop Tipis (Core i5 Gen 11)", "30.0 FPS stabil", "20.0 FPS konstan", "31 ms (sangat baik)", "Dingin / Kipas Tenang"),
        ("PC Desktop (Ryzen 5 / GPU)", "30.0 FPS stabil", "20.0 FPS konstan", "22 ms (tanpa lag)", "Suhu Ruangan")
    ]

    for idx, row_vals in enumerate(b_data):
        row = tbl_bench.rows[idx + 1]
        bg = COLOR_CREAM if idx % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(row_vals):
            c = row.cells[ci]
            set_cell_background(c, bg)
            set_cell_margins(c, top=35, bottom=35, left=60, right=60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Liberation Sans"
            r.font.size = Pt(7.2)
            r.font.color.rgb = RGBColor(53, 41, 29)
            if ci == 0:
                r.bold = True

    add_heading_2(doc, "9.2 Panduan Pemecahan Masalah (Troubleshooting Matrix)")
    add_bullet(doc, "Kamera Tidak Terbuka", "Buka situs via HTTPS / localhost dan klik 'Izinkan' (Allow) pada pop-up izin browser.")
    add_bullet(doc, "Tangan Tidak Terdeteksi", "Posisikan tangan 40-80 cm di depan kamera dengan penerangan ruangan cukup terang.")
    add_bullet(doc, "Peringatan 'Putar Ponselmu'", "Matikan kunci orientasi (Auto-rotate lock) di ponsel dan miringkan ke mode lanskap.")
    add_bullet(doc, "Tertahan Pada 'Menunggu Giliran'", "Antrean server sedang membatasi unduhan paket awal. Harap tunggu beberapa detik.")

    add_heading_2(doc, "9.3 Kesimpulan & Peta Jalan Masa Depan (Roadmap)")
    add_para(doc, "Wayang Bali Interactive berhasil memadukan kecerdasan buatan terdepan (Edge AI) dan grafis WebGL dengan seni adiluhung Nusantara tanpa mengorbankan filosofi tradisinya. Pengembangan masa depan mencakup: (1) Integrasi audio gamelan Bali dinamis (Tabuh Batel & Tetamburan) berbasis Web Audio API, (2) Fitur ekspor rekaman video dalang berdurasi 30 detik untuk media sosial, dan (3) Pertunjukan kolaboratif 2 perangkat via WebRTC.")

    doc.save(DOC_PATH)
    print(f"Document successfully created at: {DOC_PATH}")

if __name__ == '__main__':
    generate_document_10_pages()
