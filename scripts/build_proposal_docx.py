import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# --- Palette Colors ---
HEX_PRIMARY = "8B1E1E"       # Balinese Crimson Red
HEX_GOLD = "C59B27"          # Warm Gold
HEX_DARK = "1E2229"          # Deep Charcoal
HEX_MUTED = "5A6578"         # Slate Muted
HEX_CARD_BG = "F4ECE7"       # Soft Warm Tint for Headings
HEX_LIGHT_BG = "F8FAFC"      # Soft Gray Table
HEX_BORDER = "CBD5E1"        # Subtle Border
HEX_CREAM = "FDFBF7"         # Cream Callout Bg
HEX_TABLE_HEADER = "8B1E1E"

COLOR_PRIMARY = RGBColor(139, 30, 30)
COLOR_GOLD = RGBColor(197, 155, 39)
COLOR_DARK = RGBColor(30, 34, 41)
COLOR_MUTED = RGBColor(90, 101, 120)
COLOR_WHITE = RGBColor(255, 255, 255)

def set_cell_bg(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=45, bottom=45, left=75, right=75):
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

def add_page_number(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def create_document():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.50)
        section.bottom_margin = Inches(0.50)
        section.left_margin = Inches(0.60)
        section.right_margin = Inches(0.60)
        section.page_width = Inches(8.27)  # A4
        section.page_height = Inches(11.69)
        section.different_first_page_header_footer = True

        # Header for page 2+
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_hdr.paragraph_format.space_after = Pt(2)
        r_hdr = p_hdr.add_run("Bali DigiFest 2026 — AI Web Innovation Challenge | Proposal MVP: Wayang Bali Interactive")
        r_hdr.font.name = "Segoe UI"
        r_hdr.font.size = Pt(7.5)
        r_hdr.font.color.rgb = COLOR_MUTED

        # Footer for page 2+
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_ftr.paragraph_format.space_before = Pt(2)
        r_ftr_l = p_ftr.add_run("Tim Wayang Bali Interactive  •  Halaman ")
        r_ftr_l.font.name = "Segoe UI"
        r_ftr_l.font.size = Pt(7.5)
        r_ftr_l.font.color.rgb = COLOR_MUTED
        add_page_number(p_ftr.add_run())

    return doc

def add_section_header(doc, num_str, title_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(7.07)

    cell = tbl.cell(0, 0)
    set_cell_bg(cell, HEX_CARD_BG)
    set_cell_margins(cell, top=30, bottom=30, left=70, right=70)
    set_cell_borders(cell, left={'val': 'single', 'sz': 18, 'color': HEX_PRIMARY})

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)

    r_num = p.add_run(f"[{num_str}] ")
    r_num.bold = True
    r_num.font.name = "Segoe UI"
    r_num.font.size = Pt(8.5)
    r_num.font.color.rgb = COLOR_PRIMARY

    r_tit = p.add_run(title_str)
    r_tit.bold = True
    r_tit.font.name = "Georgia"
    r_tit.font.size = Pt(9.5)
    r_tit.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(1)
    p_sp.paragraph_format.space_after = Pt(0)

def add_body_p(doc, text, bold_prefix=None, space_after=1.5, font_size=8.0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.08
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.bold = True
        r_b.font.name = "Segoe UI"
        r_b.font.size = Pt(font_size)
        r_b.font.color.rgb = COLOR_PRIMARY
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(font_size)
    r.font.color.rgb = COLOR_DARK
    return p

def add_bullet_point(doc, lead_bold, body_text, space_after=1.0, font_size=7.8):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.06
    p.paragraph_format.left_indent = Inches(0.18)
    r_b = p.add_run(f"{lead_bold}: ")
    r_b.bold = True
    r_b.font.name = "Segoe UI"
    r_b.font.size = Pt(font_size)
    r_b.font.color.rgb = COLOR_DARK

    r_t = p.add_run(body_text)
    r_t.font.name = "Segoe UI"
    r_t.font.size = Pt(font_size)
    r_t.font.color.rgb = COLOR_DARK
    return p

def add_framed_image(doc, img_path, caption_text, width_in=4.4):
    if not os.path.exists(img_path):
        return
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(width_in)

    cell = tbl.cell(0, 0)
    set_cell_bg(cell, "FAF8F5")
    set_cell_margins(cell, top=25, bottom=25, left=25, right=25)
    set_cell_borders(cell, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                           bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                           left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                           right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})

    p_img = cell.paragraphs[0]
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(0)
    p_img.paragraph_format.space_after = Pt(1)
    p_img.add_run().add_picture(img_path, width=Inches(width_in - 0.15))

    p_cap = cell.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(0)
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = "Segoe UI"
    r_cap.font.size = Pt(7.0)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(0)

def build_full_proposal(output_docx):
    doc = create_document()
    base_dir = r"C:\Users\inAReality\Desktop\wayangbali"
    img_home = os.path.join(base_dir, "screenshot_home.png")
    img_select = os.path.join(base_dir, "screenshot_character_selection.png")
    img_tutor = os.path.join(base_dir, "screenshot_tutor.png")

    # =========================================================================
    # HALAMAN 1: COVER
    # =========================================================================
    # Top Crimson Banner
    tbl_cov_bar = doc.add_table(rows=1, cols=1)
    tbl_cov_bar.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cov_bar.autofit = False
    tbl_cov_bar.columns[0].width = Inches(7.07)
    c_bar = tbl_cov_bar.cell(0, 0)
    set_cell_bg(c_bar, HEX_PRIMARY)
    set_cell_margins(c_bar, top=90, bottom=90, left=140, right=140)

    p_ev = c_bar.paragraphs[0]
    p_ev.paragraph_format.space_before = Pt(0)
    p_ev.paragraph_format.space_after = Pt(2)
    r_ev = p_ev.add_run("BALI DIGIFEST 2026  •  AI WEB INNOVATION CHALLENGE")
    r_ev.bold = True
    r_ev.font.name = "Segoe UI"
    r_ev.font.size = Pt(9.5)
    r_ev.font.color.rgb = COLOR_GOLD

    p_ev_sub = c_bar.add_paragraph()
    p_ev_sub.paragraph_format.space_before = Pt(0)
    p_ev_sub.paragraph_format.space_after = Pt(0)
    r_ev_sub = p_ev_sub.add_run("Tema: BUILD WITH AI, SOLVE FOR BALI  •  Tahap Penyisihan (MVP Submission)")
    r_ev_sub.font.name = "Segoe UI"
    r_ev_sub.font.size = Pt(8.5)
    r_ev_sub.font.color.rgb = RGBColor(245, 235, 225)

    # Title Area
    p_t = doc.add_paragraph()
    p_t.paragraph_format.space_before = Pt(12)
    p_t.paragraph_format.space_after = Pt(2)
    r_t = p_t.add_run("WAYANG BALI INTERACTIVE")
    r_t.bold = True
    r_t.font.name = "Georgia"
    r_t.font.size = Pt(22)
    r_t.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(6)
    p_sub.paragraph_format.line_spacing = 1.15
    r_sub = p_sub.add_run("Panggung Wayang Kulit Digital Berbasis Edge AI Computer Vision (WASM), Dynamic Two-Bone Inverse Kinematics, dan Multimodal Cultural AI Tutor")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = COLOR_DARK

    # Category Badges Table
    tbl_badge = doc.add_table(rows=1, cols=2)
    tbl_badge.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_badge.autofit = False
    tbl_badge.columns[0].width = Inches(3.5)
    tbl_badge.columns[1].width = Inches(3.57)

    c_b1, c_b2 = tbl_badge.cell(0, 0), tbl_badge.cell(0, 1)
    set_cell_bg(c_b1, "F2EFE9")
    set_cell_bg(c_b2, "F2EFE9")
    set_cell_margins(c_b1, top=35, bottom=35, left=60, right=60)
    set_cell_margins(c_b2, top=35, bottom=35, left=60, right=60)
    set_cell_borders(c_b1, left={'val': 'single', 'sz': 14, 'color': HEX_PRIMARY})
    set_cell_borders(c_b2, left={'val': 'single', 'sz': 14, 'color': HEX_GOLD})

    p_b1 = c_b1.paragraphs[0]
    p_b1.paragraph_format.space_before = Pt(0)
    p_b1.paragraph_format.space_after = Pt(0)
    r_b1_tag = p_b1.add_run("Kategori Lomba:\n")
    r_b1_tag.font.size = Pt(7.5)
    r_b1_tag.font.color.rgb = COLOR_MUTED
    r_b1_val = p_b1.add_run("Mahasiswa / Umum")
    r_b1_val.bold = True
    r_b1_val.font.size = Pt(9.0)
    r_b1_val.font.color.rgb = COLOR_PRIMARY

    p_b2 = c_b2.paragraphs[0]
    p_b2.paragraph_format.space_before = Pt(0)
    p_b2.paragraph_format.space_after = Pt(0)
    r_b2_tag = p_b2.add_run("Bidang Solusi:\n")
    r_b2_tag.font.size = Pt(7.5)
    r_b2_tag.font.color.rgb = COLOR_MUTED
    r_b2_val = p_b2.add_run("Bali Smart Society & Education")
    r_b2_val.bold = True
    r_b2_val.font.size = Pt(9.0)
    r_b2_val.font.color.rgb = COLOR_DARK

    p_cov_sp = doc.add_paragraph()
    p_cov_sp.paragraph_format.space_before = Pt(4)
    p_cov_sp.paragraph_format.space_after = Pt(0)

    # Hero Mockup Preview
    if os.path.exists(img_home):
        add_framed_image(doc, img_home, "Gambar 1: Antarmuka Panggung Utama Wayang Bali Interactive (Kelir & Blencong Interaktif)", width_in=4.7)

    # Metadata Card Table
    tbl_meta = doc.add_table(rows=2, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    tbl_meta.columns[0].width = Inches(3.5)
    tbl_meta.columns[1].width = Inches(3.57)

    for r_idx in range(2):
        for c_idx in range(2):
            c = tbl_meta.cell(r_idx, c_idx)
            set_cell_bg(c, "FAF8F5")
            set_cell_margins(c, top=35, bottom=35, left=60, right=60)
            set_cell_borders(c, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})

    # Cell 0,0: Tim & Produk
    p_m00 = tbl_meta.cell(0, 0).paragraphs[0]
    p_m00.paragraph_format.space_before = Pt(0)
    p_m00.paragraph_format.space_after = Pt(0)
    p_m00.paragraph_format.line_spacing = 1.15
    p_m00.add_run("IDENTITAS PRODUK & TIM\n").bold = True
    p_m00.runs[0].font.size = Pt(7.5)
    p_m00.runs[0].font.color.rgb = COLOR_PRIMARY
    r_m1 = p_m00.add_run("Produk: Wayang Bali Interactive\nNama Tim: Tim Wayang Bali Interactive\nInstansi: Umum / Komunitas Digital Bali")
    r_m1.font.size = Pt(8.0)
    r_m1.font.color.rgb = COLOR_DARK

    # Cell 0,1: Anggota
    p_m01 = tbl_meta.cell(0, 1).paragraphs[0]
    p_m01.paragraph_format.space_before = Pt(0)
    p_m01.paragraph_format.space_after = Pt(0)
    p_m01.paragraph_format.line_spacing = 1.15
    p_m01.add_run("SUSUNAN ANGGOTA TIM\n").bold = True
    p_m01.runs[0].font.size = Pt(7.5)
    p_m01.runs[0].font.color.rgb = COLOR_PRIMARY
    r_m2 = p_m01.add_run("Ketua: I Putu Ngurah Harry Santika (Developer)\nAnggota: I Putu Adi Surya Arthayasa (Designer)\nFormat: Tim (2 Orang)")
    r_m2.font.size = Pt(8.0)
    r_m2.font.color.rgb = COLOR_DARK

    # Cell 1,0: Kontak
    p_m10 = tbl_meta.cell(1, 0).paragraphs[0]
    p_m10.paragraph_format.space_before = Pt(0)
    p_m10.paragraph_format.space_after = Pt(0)
    p_m10.paragraph_format.line_spacing = 1.15
    p_m10.add_run("KONTAK KETUA TIM\n").bold = True
    p_m10.runs[0].font.size = Pt(7.5)
    p_m10.runs[0].font.color.rgb = COLOR_PRIMARY
    r_m3 = p_m10.add_run("WhatsApp: 081337668803\nEmail: harrysantika@gmail.com\nDomisili: Denpasar, Bali")
    r_m3.font.size = Pt(8.0)
    r_m3.font.color.rgb = COLOR_DARK

    # Cell 1,1: Link Cepat
    p_m11 = tbl_meta.cell(1, 1).paragraphs[0]
    p_m11.paragraph_format.space_before = Pt(0)
    p_m11.paragraph_format.space_after = Pt(0)
    p_m11.paragraph_format.line_spacing = 1.15
    p_m11.add_run("URL PUBLIK & REPOSITORY\n").bold = True
    p_m11.runs[0].font.size = Pt(7.5)
    p_m11.runs[0].font.color.rgb = COLOR_PRIMARY
    r_m4 = p_m11.add_run("Website MVP: https://wayangbali.hikari.my.id\nGitHub: github.com/harrysantika-hs-inAReality/wayangbali\nVersi: v0.2.0 (Commit 7d23d66)")
    r_m4.font.size = Pt(8.0)
    r_m4.font.color.rgb = COLOR_DARK

    # END OF PAGE 1
    doc.add_page_break()

    # =========================================================================
    # HALAMAN 2: PROBLEM, TARGET USER, PROPOSED SOLUTION
    # =========================================================================
    add_section_header(doc, "01", "PROBLEM & BACKGROUND (LATAR BELAKANG MASALAH)")
    add_body_p(doc, "Kesenian Wayang Kulit Bali merupakan warisan budaya adiluhung yang sarat akan nilai filosofis, spiritual, moral, dan estetika kearifan lokal. Namun, pelestarian dan pewarisan tradisi ini di era modern menghadapi tantangan berat:", font_size=8.2)
    add_bullet_point(doc, "1. Kesenjangan Generasi terhadap Seni Tradisi", "Wayang kulit kian terasing dari generasi muda. Media pengenalan budaya yang tersedia saat ini umumnya statis dan satu arah (buku pelajaran teks atau video dokumenter pasif), sehingga minim interaktivitas dan gagal membangkitkan rasa memiliki pada generasi digital.")
    add_bullet_point(doc, "2. Hambatan Aksesibilitas Sensor & Biaya Perangkat Keras", "Pengalaman interaktif berbasis pelacakan gerak (motion tracking) di museum seni atau pameran budaya biasanya mengandalkan sensor fisik khusus yang mahal (seperti Microsoft Kinect atau Leap Motion) serta instalasi software native rumit yang tidak dapat diakses masyarakat umum di rumah.")
    add_bullet_point(doc, "3. Isu Privasi & Efisiensi Komputasi Gawai", "Banyak aplikasi berbasis kamera modern mengunggah rekaman video ke server cloud, menimbulkan kekhawatiran kebocoran data privasi wajah/ruangan pengguna, konsumsi kuota boros, serta menyebabkan panas berlebih (overheating) pada gawai seluler.")

    add_section_header(doc, "02", "TARGET USER & CONTEXT OF USE (PENGGUNA SASARAN)")
    add_body_p(doc, "Solusi Wayang Bali Interactive dirancang inklusif untuk menjangkau empat kelompok persona pengguna utama:", font_size=8.2)

    tbl_user = doc.add_table(rows=2, cols=2)
    tbl_user.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_user.autofit = False
    tbl_user.columns[0].width = Inches(3.5)
    tbl_user.columns[1].width = Inches(3.57)

    users_data = [
        ("Pelajar & Generasi Muda", "Mengeksplorasi karakter dan cerita pewayangan Bali melalui simulasi dalang digital interaktif yang seru, modern, dan langsung dapat dimainkan di smartphone/laptop tanpa aplikasi tambahan."),
        ("Pengunjung Pameran & Kiosk", "Menikmati atraksi instalasi kilat (sesi 3 menit) di festival seni/museum budaya, langsung aktif di depan layar tanpa unduh software, dengan sistem reset otomatis saat pengunjung berganti."),
        ("Pendidik & Penggiat Seni", "Sebagai sarana alat peraga digital interaktif di ruang kelas sekolah atau lokakarya seni yang dilengkapi asisten AI Tutor cerdas untuk menjawab rasa ingin tahu murid seputar budaya Bali."),
        ("Wisatawan Domestik & Asing", "Media edukasi budaya interaktif mandiri yang intuitif untuk mengenal tokoh punokawan, mitologi, dan tata nilai tradisi pewayangan Bali langsung dari genggaman gawai mereka.")
    ]

    for idx, (u_title, u_desc) in enumerate(users_data):
        r, c = divmod(idx, 2)
        cell = tbl_user.cell(r, c)
        set_cell_bg(cell, "FAF8F5")
        set_cell_margins(cell, top=30, bottom=30, left=50, right=50)
        set_cell_borders(cell, left={'val': 'single', 'sz': 12, 'color': HEX_PRIMARY},
                               top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                               bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                               right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.06
        r_ut = p.add_run(f"• {u_title}\n")
        r_ut.bold = True
        r_ut.font.size = Pt(7.8)
        r_ut.font.color.rgb = COLOR_PRIMARY
        r_ud = p.add_run(u_desc)
        r_ud.font.size = Pt(7.5)
        r_ud.font.color.rgb = COLOR_DARK

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(3)
    p_sp2.paragraph_format.space_after = Pt(0)

    add_section_header(doc, "03", "PROPOSED SOLUTION & USER JOURNEY (SOLUSI PRODUK)")
    add_body_p(doc, "Wayang Bali Interactive menghadirkan panggung wayang digital berbasis web murni (zero-install) yang mengubah siapa saja menjadi dalang secara langsung hanya bermodalkan webcam gawai. Solusi memadukan Computer Vision lokal di browser, simulasi artikulasi Inverse Kinematics, serta AI Tutor interaktif.", font_size=8.2)
    add_bullet_point(doc, "Alur Perjalanan Pengguna (User Journey)", "Pengguna membuka URL https://wayangbali.hikari.my.id -> Mengizinkan akses kamera webcam -> Memilih tokoh untuk tangan kiri dan/atau tangan kanan -> Melakukan kalibrasi posisi tangan selama 1,5 detik -> Memainkan wayang di panggung interaktif 2D selama sesi 3 menit (termasuk membalik orientasi tokoh via gestur kepal-lurus) -> Bertanya seputar tokoh/sejarah kepada AI Tutor Wayang Bali via teks atau mikrofon suara.")

    # END OF PAGE 2
    doc.add_page_break()

    # =========================================================================
    # HALAMAN 3: AI IMPLEMENTATION & MVP FEATURES
    # =========================================================================
    add_section_header(doc, "04", "AI IMPLEMENTATION & TECHNICAL DEPTH (IMPLEMENTASI TEKNOLOGI AI)")
    add_body_p(doc, "Kecerdasan Buatan (AI) merupakan fondasi utama yang bekerja simultan pada dua lapisan inti aplikasi:", font_size=8.2)

    add_body_p(doc, "1. Edge Computer Vision on-device (Google MediaPipe Hand Landmarker WASM):", bold_prefix=None, space_after=1, font_size=8.0)
    add_bullet_point(doc, "Pelacakan 21 Sendi 3D", "Model machine learning hand_landmarker.task (v1.0.1) dieksekusi 100% lokal di browser melalui WebAssembly. Model mendeteksi 21 titik koordinat sendi tangan 3D ternormalisasi secara real-time pada 20–30 FPS tanpa mengirim sebutir pun data gambar ke cloud.")
    add_bullet_point(doc, "Algoritma Two-Bone Inverse Kinematics (IK)", "Translasi landmark jari telunjuk dan jari tengah dipetakan menjadi target artikulasi sendi bahu dan siku lengan wayang secara anatomis dan luwes dengan batasan rotasi sendi khusus.")
    add_bullet_point(doc, "Identitas Tangan Persisten & Grace Period 300 ms", "Sistem pelacak menjaga konsistensi identitas tangan kiri dan kanan. Jika tangan saling bersilangan (hand crossing) atau terhalang sesaat, grace period 300 ms menahan pose terakhir sehingga tokoh tidak pernah tertukar.")
    add_bullet_point(doc, "Facing Flip Gesture Recognition", "Finite State Machine (FSM) mendeteksi gestur alami: mengepal ±0,5 detik lalu meluruskan jari untuk membalik arah hadap tokoh wayang di panggung secara mulus dengan cooldown pengaman.")

    add_body_p(doc, "2. Multimodal Cultural Knowledge AI Tutor (Google Gemini + OpenAI Failover):", bold_prefix=None, space_after=1, font_size=8.0)
    add_bullet_point(doc, "Penalaran Bahasa Alami", "Google Gemini 3.5 Flash-Lite bertindak sebagai pemandu budaya yang menjawab pertanyaan seputar sejarah, filosofi, mitologi, lakon, dan tradisi Wayang Bali dalam bahasa Indonesia yang ringkas (maksimal 2 kalimat / ~55 kata).")
    add_bullet_point(doc, "Input Suara Multimodal & Transkripsi", "Pengguna dapat bertanya langsung lewat mikrofon browser. Audio direkam via MediaRecorder (format MP4/WebM/OGG, maks. 15 dtk / 256 KiB) dan ditranskripsikan secara ephemeral ke teks.")
    add_bullet_point(doc, "Automatic Dual-Provider Failover", "Backend proxy PHP menerapkan pembatasan kuota token harian. Jika panggilan Gemini mencapai batas kuota atau rate limit (HTTP 429), sistem otomatis mengalihkan permintaan ke OpenAI GPT-4.1-mini & Whisper secara transparan.")

    # Screenshot 2: Character Selection
    if os.path.exists(img_select):
        add_framed_image(doc, img_select, "Gambar 2: Antarmuka Pemilihan Tokoh & Penugasan Slot Tangan Kiri/Kanan (Twalen, Merdah, Sangut, Delem)", width_in=4.4)

    add_section_header(doc, "05", "MVP & KEY FEATURES (FITUR UTAMA YANG SUDAH BERFUNGSI)")
    add_body_p(doc, "Seluruh fitur inti di bawah ini telah selesai diimplementasikan, lulus pengujian, dan dapat diuji langsung oleh juri saat submission Tahap 1:", font_size=8.0)

    tbl_feat = doc.add_table(rows=8, cols=3)
    tbl_feat.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_feat.autofit = False
    tbl_feat.columns[0].width = Inches(1.8)
    tbl_feat.columns[1].width = Inches(4.37)
    tbl_feat.columns[2].width = Inches(0.9)

    # Header
    for idx, h_text in enumerate(["Fitur Utama", "Mekanisme & Cara Kerja pada MVP", "Status"]):
        cell = tbl_feat.cell(0, idx)
        set_cell_bg(cell, HEX_TABLE_HEADER)
        set_cell_margins(cell, top=30, bottom=30, left=50, right=50)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = COLOR_WHITE

    feat_data = [
        ("Dual-Hand Independent", "Tangan kiri fisik mengendalikan tokoh slot kiri, tangan kanan slot kanan. Bisa dimainkan 1 atau 2 orang.", "✓ Teruji"),
        ("Two-Bone Inverse Kinematics", "Jari telunjuk menggerakkan lengan utama dan jari tengah menggerakkan lengan sekunder secara dinamis.", "✓ Teruji"),
        ("Palm Tracking & Tilt", "Translasi telapak tangan menggerakkan posisi wayang; kemiringan telapak membuat badan condong.", "✓ Teruji"),
        ("Facing Flip Gesture", "Gestur kepal 0,5 dtk lalu luruskan jari membalik arah hadap wayang seketika dengan cooldown pengaman.", "✓ Teruji"),
        ("Hand Persistence", "Wayang tidak tertukar saat tangan bersilangan; grace period 300 ms menahan pose saat tracking hilang.", "✓ Teruji"),
        ("Multimodal AI Tutor", "Tanya jawab sejarah dan filosofi wayang Bali via teks atau rekaman suara mikrofon + Text-to-Speech.", "✓ Teruji"),
        ("PWA Offline Caching", "Service Worker menyimpan aset panggung; antrean unduhan streaming mencegah server overload.", "✓ Teruji")
    ]

    for r_idx, (f_name, f_desc, f_stat) in enumerate(feat_data, start=1):
        bg = HEX_LIGHT_BG if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([f_name, f_desc, f_stat]):
            cell = tbl_feat.cell(r_idx, c_idx)
            set_cell_bg(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=50, right=50)
            set_cell_borders(cell, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                   bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                   left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                   right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(7.2)
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            elif c_idx == 2:
                r.bold = True
                r.font.color.rgb = RGBColor(16, 120, 50)
            else:
                r.font.color.rgb = COLOR_DARK

    # END OF PAGE 3
    doc.add_page_break()

    # =========================================================================
    # HALAMAN 4: ARCHITECTURE, INNOVATION, IMPACT & ROADMAP
    # =========================================================================
    add_section_header(doc, "06", "TECHNICAL ARCHITECTURE & PIPELINE (ARSITEKTUR SISTEM)")
    add_body_p(doc, "Arsitektur dibangun berprinsip edge-first, decoupled modularity, serta batas privasi yang ketat:", font_size=8.2)

    # ASCII Architecture Box
    tbl_arch = doc.add_table(rows=1, cols=1)
    tbl_arch.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_arch.autofit = False
    tbl_arch.columns[0].width = Inches(7.07)
    c_arch = tbl_arch.cell(0, 0)
    set_cell_bg(c_arch, "F2F5F8")
    set_cell_margins(c_arch, top=35, bottom=35, left=60, right=60)
    set_cell_borders(c_arch, left={'val': 'single', 'sz': 16, 'color': HEX_PRIMARY},
                             top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})

    p_arch = c_arch.paragraphs[0]
    p_arch.paragraph_format.space_before = Pt(0)
    p_arch.paragraph_format.space_after = Pt(0)
    p_arch.paragraph_format.line_spacing = 1.05
    arch_code = (
        "[KAMERA WEBCAM LOKAL] ──▶ [requestVideoFrameCallback] ──▶ [MediaPipe WASM (20-30 FPS)]\n"
        "                                                               │ 21 Titik Sendi 3D (Lokal)\n"
        "                                                               ▼\n"
        "[PANGGUNG PIXIJS v8 (30 FPS)] ◀── [Two-Bone IK Rig] ◀── [HandTrackManager (Grace 300ms)]\n"
        "────────────────────────────────────────────────────────────────────────────────────────\n"
        "[AUDIO / TEKS PENGGUNA] ──▶ [PHP Backend Proxy (server/tutor.php)] ──▶ [Cek Kuota/Limit]\n"
        "                                   │                                            │\n"
        "                                   ▼                                            ▼\n"
        "[TTS AUDIO / BUBBLE CHAT] ◀── [Format JSON] ◀── [Fallback OpenAI] ◀── [Gemini Flash-Lite]"
    )
    r_arch = p_arch.add_run(arch_code)
    r_arch.font.name = "Consolas"
    r_arch.font.size = Pt(6.8)
    r_arch.font.color.rgb = COLOR_DARK

    p_sp4 = doc.add_paragraph()
    p_sp4.paragraph_format.space_before = Pt(3)
    p_sp4.paragraph_format.space_after = Pt(0)

    add_section_header(doc, "07", "INNOVATION & DIFFERENTIATION (INOVASI & KOMPARASI)")
    add_body_p(doc, "Tabel perbandingan Wayang Bali Interactive terhadap alternatif solusi eksisting:", font_size=8.0)

    tbl_comp = doc.add_table(rows=6, cols=4)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_comp.autofit = False
    tbl_comp.columns[0].width = Inches(1.5)
    tbl_comp.columns[1].width = Inches(2.1)
    tbl_comp.columns[2].width = Inches(1.8)
    tbl_comp.columns[3].width = Inches(1.67)

    # Header
    for idx, h_text in enumerate(["Parameter", "Wayang Bali Interactive", "Sensor Fisik (Kinect/Leap)", "Media Konvensional"]):
        cell = tbl_comp.cell(0, idx)
        set_cell_bg(cell, HEX_TABLE_HEADER)
        set_cell_margins(cell, top=25, bottom=25, left=40, right=40)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(7.2)
        r.font.color.rgb = COLOR_WHITE

    comp_rows = [
        ("Biaya Perangkat", "Rp 0 (Webcam standar laptop/HP)", "Mahal (Jutaan Rupiah/alat)", "Rp 0 (Buku teks/YouTube)"),
        ("Aksesibilitas", "Instan di browser, zero-install", "Rumit, butuh instalasi driver", "Mudah, namun minim engagement"),
        ("Interaktivitas Gerak", "Simultan 2 tangan + Inverse Kinematics", "Bisa gerak tubuh, tanpa AI tutor", "Pasif total (satu arah)"),
        ("Edukasi Budaya", "AI Tutor Budaya teks & suara aktif", "Tidak ada modul edukasi AI", "Statis, tidak bisa tanya jawab"),
        ("Privasi Data Kamera", "100% On-Device, tidak diunggah", "Bergantung vendor hardware", "Tidak menggunakan kamera")
    ]

    for r_idx, (p_name, p_ours, p_kinect, p_conv) in enumerate(comp_rows, start=1):
        bg = HEX_LIGHT_BG if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([p_name, p_ours, p_kinect, p_conv]):
            cell = tbl_comp.cell(r_idx, c_idx)
            set_cell_bg(cell, bg)
            set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
            set_cell_borders(cell, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                   bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                   left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                                   right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(7.0)
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            elif c_idx == 1:
                r.bold = True
                r.font.color.rgb = COLOR_DARK
            else:
                r.font.color.rgb = COLOR_MUTED

    p_sp5 = doc.add_paragraph()
    p_sp5.paragraph_format.space_before = Pt(3)
    p_sp5.paragraph_format.space_after = Pt(0)

    add_section_header(doc, "08", "IMPACT, LIMITATIONS, & DEVELOPMENT ROADMAP (DAMPAK & PENGEMBANGAN)")
    add_body_p(doc, "Dampak Nyata: Menjembatani kesenjangan generasi muda terhadap budaya adiluhung Bali secara inklusif, menghidupkan kembali minat anak muda pada seni pedalangan, dan membuka pintu edukasi pariwisata cerdas (Bali Smart Society).", font_size=8.0)
    add_bullet_point(doc, "Keterbatasan MVP Saat Ini", "Katalog tokoh saat ini memuat 4 punokawan (Twalen, Merdah, Sangut, Delem); durasi panggung dibatasi 3 menit untuk efisiensi termal gawai; AI Tutor memerlukan koneksi internet.")
    add_bullet_point(doc, "Roadmap Pengembangan Lanjutan", "Tahap berikutnya: (1) Penambahan katalog tokoh epos Mahabharata & Ramayana; (2) Mode Lakon Cerita Terpandu (Interactive Storytelling Mode); (3) Fitur Multi-Device Dalang Duet melalui WebRTC.")

    # Screenshot 3: AI Tutor
    if os.path.exists(img_tutor):
        add_framed_image(doc, img_tutor, "Gambar 3: Antarmuka AI Tutor Wayang Bali Multimodal (Tanya Dalang via Suara Mikrofon & Teks)", width_in=4.4)

    # END OF PAGE 4
    doc.add_page_break()

    # =========================================================================
    # HALAMAN 5: TECHNOLOGY DISCLOSURE, SUBMISSION LINKS, DECLARATION
    # =========================================================================
    add_section_header(doc, "09", "TECHNOLOGY & THIRD-PARTY DISCLOSURE (PENGUNGKAPAN TEKNOLOGI)")
    add_body_p(doc, "Matriks pengungkapan penuh komponen teknologi, pustaka, model AI, dan aset pihak ketiga sesuai Panduan Lampiran C:", font_size=8.0)

    tbl_disc = doc.add_table(rows=8, cols=2)
    tbl_disc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_disc.autofit = False
    tbl_disc.columns[0].width = Inches(2.2)
    tbl_disc.columns[1].width = Inches(4.87)

    disc_data = [
        ("Framework & Frontend", "TypeScript 7 (Strict Mode), PixiJS v8 (WebGL Renderer), Semantic HTML5 & Modern Vanilla CSS3, Vite 8 (Bundler)."),
        ("Computer Vision (On-Device)", "Google MediaPipe Tasks Vision (@mediapipe/tasks-vision v1.0.1 WASM), hand_landmarker.task."),
        ("AI Models & Cloud APIs", "Google Gemini API (gemini-3.5-flash-lite) sebagai AI Tutor utama; OpenAI API (gpt-4.1-mini, Whisper, TTS) sebagai failover otomatis."),
        ("Backend & Runtime", "PHP 8.1+ dengan ekstensi ext-curl dan ext-mbstring, dijalankan di atas Apache Web Server (mod_rewrite, .htaccess)."),
        ("Database & Storage", "Stateless (No Database), local atomic file budget lock (wayangbali-tutor-budget.json via PHP flock), PWA Service Worker Cache."),
        ("Hosting & Domain", "Apache HTTPS Server, Domain: https://wayangbali.hikari.my.id."),
        ("AI Coding Assistants", "Claude Code, Google Antigravity / Gemini CLI, GitHub Copilot (digunakan untuk refactoring TypeScript, Two-Bone IK, unit test gestur, dan PRD)."),
        ("Aset Seni, Font, & Audio", "Ilustrasi potongan tubuh 4 tokoh punokawan Wayang Bali; Self-hosted fonts Cormorant Garamond & Plus Jakarta Sans; Musik latar Gending Gender Wayang 'Pengrumrum' karya Astadi Jaya.")
    ]

    for r_idx, (d_comp, d_detail) in enumerate(disc_data):
        bg = HEX_LIGHT_BG if r_idx % 2 == 1 else "FFFFFF"
        c0, c1 = tbl_disc.cell(r_idx, 0), tbl_disc.cell(r_idx, 1)
        set_cell_bg(c0, bg)
        set_cell_bg(c1, bg)
        set_cell_margins(c0, top=20, bottom=20, left=45, right=45)
        set_cell_margins(c1, top=20, bottom=20, left=45, right=45)
        set_cell_borders(c0, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})
        set_cell_borders(c1, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.05
        r0 = p0.add_run(d_comp)
        r0.bold = True
        r0.font.size = Pt(7.2)
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.05
        r1 = p1.add_run(d_detail)
        r1.font.size = Pt(7.2)
        r1.font.color.rgb = COLOR_DARK

    p_sp6 = doc.add_paragraph()
    p_sp6.paragraph_format.space_before = Pt(3)
    p_sp6.paragraph_format.space_after = Pt(0)

    add_section_header(doc, "10", "SUBMISSION LINKS & TECHNICAL VERIFICATION (TAUTAN SUBMISSION)")
    add_body_p(doc, "Informasi verifikasi teknis dan aksesibilitas juri Tahap 1:", font_size=8.0)

    tbl_links = doc.add_table(rows=4, cols=2)
    tbl_links.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_links.autofit = False
    tbl_links.columns[0].width = Inches(2.2)
    tbl_links.columns[1].width = Inches(4.87)

    links_data = [
        ("URL Website MVP Aktif", "https://wayangbali.hikari.my.id (Dapat diakses publik langsung, HTTPS)"),
        ("URL Repository GitHub", "https://github.com/harrysantika-hs-inAReality/wayangbali (Status: Public)"),
        ("Git Release Tag / Hash", "Tag: v0.2.0  •  Commit Hash: 7d23d666329aca4f7e1f164ee34ff76c8c67bf13"),
        ("Instruksi Akses / Akun Demo", "Tidak memerlukan login/akun khusus. Buka URL pada browser, izinkan webcam, dan mainkan.")
    ]

    for r_idx, (l_title, l_val) in enumerate(links_data):
        bg = HEX_LIGHT_BG if r_idx % 2 == 1 else "FFFFFF"
        c0, c1 = tbl_links.cell(r_idx, 0), tbl_links.cell(r_idx, 1)
        set_cell_bg(c0, bg)
        set_cell_bg(c1, bg)
        set_cell_margins(c0, top=20, bottom=20, left=45, right=45)
        set_cell_margins(c1, top=20, bottom=20, left=45, right=45)
        set_cell_borders(c0, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})
        set_cell_borders(c1, top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             left={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                             right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.05
        r0 = p0.add_run(l_title)
        r0.bold = True
        r0.font.size = Pt(7.2)
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.05
        r1 = p1.add_run(l_val)
        r1.font.size = Pt(7.2)
        r1.font.color.rgb = COLOR_DARK

    p_sp7 = doc.add_paragraph()
    p_sp7.paragraph_format.space_before = Pt(4)
    p_sp7.paragraph_format.space_after = Pt(0)

    # Formal Declaration & Sign-off Box
    tbl_dec = doc.add_table(rows=1, cols=1)
    tbl_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_dec.autofit = False
    tbl_dec.columns[0].width = Inches(7.07)
    c_dec = tbl_dec.cell(0, 0)
    set_cell_bg(c_dec, HEX_CREAM)
    set_cell_margins(c_dec, top=45, bottom=45, left=70, right=70)
    set_cell_borders(c_dec, left={'val': 'single', 'sz': 16, 'color': HEX_GOLD},
                           top={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                           bottom={'val': 'single', 'sz': 4, 'color': HEX_BORDER},
                           right={'val': 'single', 'sz': 4, 'color': HEX_BORDER})

    p_dec = c_dec.paragraphs[0]
    p_dec.paragraph_format.space_before = Pt(0)
    p_dec.paragraph_format.space_after = Pt(2)
    p_dec.paragraph_format.line_spacing = 1.08
    r_dec_h = p_dec.add_run("PERNYATAAN ORISINALITAS & KESIAPAN VERIFIKASI TEKNIS\n")
    r_dec_h.bold = True
    r_dec_h.font.size = Pt(7.8)
    r_dec_h.font.color.rgb = COLOR_PRIMARY

    dec_text = (
        "Kami menyatakan bahwa seluruh informasi teknis, source code, arsitektur, dan tautan submission dalam proposal ini "
        "adalah benar, sah, orisinal dikembangkan oleh tim kami, dan siap dipertanggungjawabkan pada sesi Technical Verification. "
        "Tidak ada credential/API key sensitif yang terekspos di repository publik. Kami bersedia mematuhi seluruh ketentuan lomba Bali DigiFest 2026.\n\n"
        "Denpasar, Bali — 6 November 2026\n"
        "Ketua Tim: I Putu Ngurah Harry Santika  •  Anggota: I Putu Adi Surya Arthayasa"
    )
    r_dec_b = p_dec.add_run(dec_text)
    r_dec_b.font.size = Pt(7.2)
    r_dec_b.font.color.rgb = COLOR_DARK

    doc.save(output_docx)
    print(f"Proposal berhasil dibuat di: {output_docx}")

if __name__ == "__main__":
    out_file = r"C:\Users\inAReality\Desktop\wayangbali\Proposal_AIWIC2026_WayangBaliInteractive.docx"
    build_full_proposal(out_file)
