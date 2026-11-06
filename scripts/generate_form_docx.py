import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# --- Color Constants ---
COLOR_PRIMARY_HEX = "8B1E1E"       # Crimson Balinese Red
COLOR_GOLD_HEX = "C59B27"          # Warm Gold
COLOR_DARK_HEX = "23272E"          # Slate Dark / Charcoal
COLOR_MUTED_HEX = "5A6275"         # Muted Slate
COLOR_CREAM_HEX = "FBF9F5"         # Cream Callout Background
COLOR_BOX_BG_HEX = "F8FAFC"        # Soft Gray for Input Boxes
COLOR_BORDER_HEX = "D1D5DB"        # Subtle Border Gray
COLOR_ANSWER_TEXT_HEX = "1A365D"   # Deep Navy for filled answers
COLOR_REQUIRED_HEX = "DC2626"      # Required red star

COLOR_PRIMARY = RGBColor(139, 30, 30)
COLOR_GOLD = RGBColor(197, 155, 39)
COLOR_DARK = RGBColor(35, 39, 46)
COLOR_MUTED = RGBColor(90, 98, 117)
COLOR_ANSWER_TEXT = RGBColor(26, 54, 93)
COLOR_REQUIRED = RGBColor(220, 38, 38)

def set_cell_bg(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_box_border(cell, color=COLOR_BORDER_HEX, sz=4):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ['top', 'bottom', 'left', 'right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), str(sz))
        b.set(qn('w:color'), color)
        tcBorders.append(b)
    tcPr.append(tcBorders)

def set_cell_left_border(cell, color=COLOR_GOLD_HEX, sz=24):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), str(sz))
    left.set(qn('w:color'), color)
    tcBorders.append(left)
    for side in ['top', 'bottom', 'right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tcBorders.append(b)
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

def create_base_document(title_prefix=""):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.page_width = Inches(8.27)  # A4
        section.page_height = Inches(11.69)
        section.different_first_page_header_footer = True

        # Header for page 2+
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run(f"Bali DigiFest 2026 — AI Web Innovation Challenge | {title_prefix}")
        r_hdr.font.name = "Segoe UI"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = COLOR_MUTED

        # Footer for page 2+
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ftr_l = p_ftr.add_run("Wayang Bali Interactive  •  Halaman ")
        r_ftr_l.font.name = "Segoe UI"
        r_ftr_l.font.size = Pt(8.5)
        r_ftr_l.font.color.rgb = COLOR_MUTED
        add_page_number(p_ftr.add_run())

    return doc

def add_header_banner(doc, title, subtitle, badge="BALI DIGIFEST 2026  •  TAHAP PENYISIHAN"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.77)

    cell = tbl.cell(0, 0)
    set_cell_bg(cell, COLOR_PRIMARY_HEX)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    p_tag = cell.paragraphs[0]
    p_tag.paragraph_format.space_before = Pt(0)
    p_tag.paragraph_format.space_after = Pt(3)
    r_tag = p_tag.add_run(badge)
    r_tag.bold = True
    r_tag.font.name = "Segoe UI"
    r_tag.font.size = Pt(8.5)
    r_tag.font.color.rgb = COLOR_GOLD

    p_title = cell.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(3)
    r_title = p_title.add_run(title)
    r_title.bold = True
    r_title.font.name = "Georgia"
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(255, 255, 255)

    p_sub = cell.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(0)
    r_sub = p_sub.add_run(subtitle)
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(9)
    r_sub.font.color.rgb = RGBColor(245, 240, 235)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(6)
    p_space.paragraph_format.space_after = Pt(0)

def add_callout(doc, text_list, title="PANDUAN & KETENTUAN PENTING", icon="📌"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.77)

    cell = tbl.cell(0, 0)
    set_cell_bg(cell, COLOR_CREAM_HEX)
    set_cell_margins(cell, top=90, bottom=90, left=140, right=140)
    set_cell_left_border(cell, color=COLOR_GOLD_HEX, sz=20)

    p_title = cell.paragraphs[0]
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(3)
    r_icon = p_title.add_run(f"{icon} ")
    r_icon.font.size = Pt(9.5)
    r_t = p_title.add_run(title)
    r_t.bold = True
    r_t.font.name = "Georgia"
    r_t.font.size = Pt(9.5)
    r_t.font.color.rgb = COLOR_PRIMARY

    for t in text_list:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(t)
        r.font.name = "Segoe UI"
        r.font.size = Pt(8.5)
        r.font.color.rgb = COLOR_DARK

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(4)
    p_space.paragraph_format.space_after = Pt(0)

def add_step_heading(doc, step_label, step_title, instruction_note=None):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.77)

    cell = tbl.cell(0, 0)
    set_cell_bg(cell, "F3ECE7")
    set_cell_margins(cell, top=70, bottom=70, left=130, right=130)
    set_cell_left_border(cell, color=COLOR_PRIMARY_HEX, sz=20)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1)
    
    r_lbl = p.add_run(step_label.upper())
    r_lbl.bold = True
    r_lbl.font.name = "Segoe UI"
    r_lbl.font.size = Pt(8.5)
    r_lbl.font.color.rgb = COLOR_PRIMARY

    r_sep = p.add_run("  —  ")
    r_sep.bold = True
    r_sep.font.color.rgb = COLOR_MUTED

    r_tit = p.add_run(step_title)
    r_tit.bold = True
    r_tit.font.name = "Georgia"
    r_tit.font.size = Pt(10.5)
    r_tit.font.color.rgb = COLOR_DARK

    if instruction_note:
        p_note = cell.add_paragraph()
        p_note.paragraph_format.space_before = Pt(2)
        p_note.paragraph_format.space_after = Pt(0)
        r_n = p_note.add_run(instruction_note)
        r_n.italic = True
        r_n.font.name = "Segoe UI"
        r_n.font.size = Pt(8)
        r_n.font.color.rgb = COLOR_MUTED

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(3)
    p_space.paragraph_format.space_after = Pt(0)

def add_question_item(doc, q_num, title, q_type=None, help_text=None, options=None, filled_answer=None, answer_box_lines=2):
    p_q = doc.add_paragraph()
    p_q.paragraph_format.space_before = Pt(5)
    p_q.paragraph_format.space_after = Pt(2)
    p_q.paragraph_format.keep_with_next = True

    clean_title = title.replace("*", "").strip()
    is_req = "*" in title

    r_num = p_q.add_run(f"{q_num}. ")
    r_num.bold = True
    r_num.font.name = "Georgia"
    r_num.font.size = Pt(9.5)
    r_num.font.color.rgb = COLOR_PRIMARY

    r_title = p_q.add_run(clean_title)
    r_title.bold = True
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = COLOR_DARK

    if is_req:
        r_star = p_q.add_run(" *")
        r_star.bold = True
        r_star.font.size = Pt(9.5)
        r_star.font.color.rgb = COLOR_REQUIRED

    if q_type:
        r_type = p_q.add_run(f"  ({q_type})")
        r_type.font.name = "Segoe UI"
        r_type.font.size = Pt(8)
        r_type.font.italic = True
        r_type.font.color.rgb = COLOR_MUTED

    if help_text:
        p_help = doc.add_paragraph()
        p_help.paragraph_format.left_indent = Inches(0.2)
        p_help.paragraph_format.space_before = Pt(0)
        p_help.paragraph_format.space_after = Pt(2)
        p_help.paragraph_format.keep_with_next = True
        r_help = p_help.add_run(f"ℹ️ {help_text}")
        r_help.font.name = "Segoe UI"
        r_help.font.size = Pt(8)
        r_help.font.italic = True
        r_help.font.color.rgb = COLOR_MUTED

    # Options (checkbox / radio list)
    if options:
        is_checkbox_type = "checkbox" in (q_type or "").lower()
        for opt in options:
            p_opt = doc.add_paragraph()
            p_opt.paragraph_format.left_indent = Inches(0.3)
            p_opt.paragraph_format.space_before = Pt(1)
            p_opt.paragraph_format.space_after = Pt(1)
            
            is_selected = False
            if filled_answer is not None:
                if isinstance(filled_answer, list) and opt in filled_answer:
                    is_selected = True
                elif isinstance(filled_answer, str) and (opt == filled_answer or opt.startswith(filled_answer)):
                    is_selected = True

            if is_selected:
                symbol = "[X] " if is_checkbox_type else "(X) "
            else:
                symbol = "[  ] " if is_checkbox_type else "(  ) "

            r_mark = p_opt.add_run(symbol)
            r_mark.bold = is_selected
            r_mark.font.name = "Consolas"
            r_mark.font.size = Pt(9)
            r_mark.font.color.rgb = COLOR_PRIMARY if is_selected else COLOR_MUTED

            r_opt = p_opt.add_run(opt)
            r_opt.font.name = "Segoe UI"
            r_opt.font.size = Pt(8.5)
            if is_selected:
                r_opt.bold = True
                r_opt.font.color.rgb = COLOR_ANSWER_TEXT
            else:
                r_opt.font.color.rgb = COLOR_DARK

    # Answer box (either empty placeholder or filled answer)
    if filled_answer is not None and not options:
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.5)

        cell = tbl.cell(0, 0)
        set_cell_bg(cell, "F0F4F9")
        set_cell_box_border(cell, color="A5B4FC", sz=6)
        set_cell_margins(cell, top=60, bottom=60, left=100, right=100)

        p_ans = cell.paragraphs[0]
        p_ans.paragraph_format.space_before = Pt(0)
        p_ans.paragraph_format.space_after = Pt(0)
        p_ans.paragraph_format.line_spacing = 1.15
        
        lines = str(filled_answer).split('\n')
        for idx, line in enumerate(lines):
            if idx > 0:
                p_ans = cell.add_paragraph()
                p_ans.paragraph_format.space_before = Pt(2)
                p_ans.paragraph_format.space_after = Pt(0)
                p_ans.paragraph_format.line_spacing = 1.15
            r_ans = p_ans.add_run(line)
            r_ans.font.name = "Segoe UI"
            r_ans.font.size = Pt(8.5)
            r_ans.font.color.rgb = COLOR_ANSWER_TEXT

    elif not options and filled_answer is None:
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.5)

        cell = tbl.cell(0, 0)
        set_cell_bg(cell, COLOR_BOX_BG_HEX)
        set_cell_box_border(cell, color=COLOR_BORDER_HEX, sz=4)
        set_cell_margins(cell, top=50, bottom=50, left=100, right=100)

        p_box = cell.paragraphs[0]
        p_box.paragraph_format.space_before = Pt(0)
        p_box.paragraph_format.space_after = Pt(0)
        if answer_box_lines <= 2:
            placeholder_text = "[ Tulis isian jawaban di sini... ]"
        else:
            placeholder_text = "[ Tulis deskripsi lengkap di sini... ]" + ("\n" * (answer_box_lines - 1))
        r_box = p_box.add_run(placeholder_text)
        r_box.italic = True
        r_box.font.name = "Segoe UI"
        r_box.font.size = Pt(8)
        r_box.font.color.rgb = RGBColor(165, 175, 185)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(1)
    p_spacer.paragraph_format.space_after = Pt(0)

def generate_form_docx(output_path, filled=False):
    title_suffix = "Draf Isian Submission" if filled else "Formulir Registrasi & Submission"
    doc = create_base_document(title_prefix=title_suffix)

    # 1. Header Banner
    add_header_banner(
        doc,
        title="Formulir Registrasi & Submission — AI Web Innovation Challenge",
        subtitle="Bali DigiFest 2026  •  Build with AI, Solve for Bali" + (" (Draf Isian Lengkap)" if filled else ""),
        badge="BALI DIGIFEST 2026  •  TAHAP PENYISIHAN"
    )

    # 2. Callout Info
    info_points = [
        "Form ini digunakan untuk REGISTRASI sekaligus SUBMISSION Tahap Penyisihan AI Web Innovation Challenge — Bali DigiFest 2026.",
        "Kategori Lomba: SMA/SMK/Sederajat dan Mahasiswa/Umum. Penilaian dan penetapan juara terpisah.",
        "Bidang Solusi: Pendidikan, UMKM & Bisnis, atau Bali Smart Society.",
        "Sebelum mulai, pastikan telah menyiapkan: Identitas Peserta/Tim, Proposal PDF (maks. 100 MB), Repository GitHub, URL Website MVP aktif yang dapat diakses juri, serta Pengungkapan Teknologi AI.",
        "Periode Registrasi & Submission Tahap Penyisihan: 12 Oktober – 6 November 2026. Pendaftaran GRATIS.",
        "Link Panduan Peserta Resmi: https://drive.google.com/uc?export=download&id=1LNiRhP4tB5UCQsb3g9yojVaOsUjbw4Ys"
    ]
    add_callout(doc, info_points, title="INFORMASI UMUM & PETUNJUK PENDAFTARAN", icon="📢")

    # Page 1: Pertanyaan Pembuka
    add_step_heading(doc, "Halaman 1", "Informasi Akun & Konfirmasi Awal", "Persyaratan awal sebelum mengisi formulir registrasi")
    add_question_item(
        doc,
        q_num=1,
        title="Email *",
        q_type="isian email",
        help_text="Gunakan email aktif ketua tim untuk korespondensi resmi panitia.",
        filled_answer="harrysantika@gmail.com" if filled else None
    )
    add_question_item(
        doc,
        q_num=2,
        title="Konfirmasi sebelum mengisi *",
        q_type="checkbox, wajib dicentang",
        help_text="Pastikan sudah membaca panduan teknis lomba.",
        options=["Saya telah membaca panduan lomba dan siap mengisi data registrasi serta submission dengan benar."],
        filled_answer=["Saya telah membaca panduan lomba dan siap mengisi data registrasi serta submission dengan benar."] if filled else None
    )

    # Page 2: Identitas Peserta / Tim
    add_step_heading(doc, "Step 1", "Identitas Peserta / Tim (Halaman 2)", "Isi data sesuai kategori peserta dan kondisi tim Anda.")
    add_question_item(
        doc,
        q_num=1,
        title="Kategori Lomba *",
        q_type="pilih satu",
        help_text="Penilaian dan penetapan juara dilakukan terpisah per kategori.",
        options=["SMA/SMK/Sederajat", "Mahasiswa/Umum"],
        filled_answer="Mahasiswa/Umum" if filled else None
    )
    add_question_item(
        doc,
        q_num=2,
        title="Bentuk Keikutsertaan *",
        q_type="pilih satu",
        options=["Individu", "Tim (2 orang)", "Tim (3 orang)"],
        filled_answer="Tim (2 orang)" if filled else None
    )
    add_question_item(
        doc,
        q_num=3,
        title="Nama Tim *",
        q_type="isian singkat",
        help_text="Untuk peserta individu, isi dengan nama peserta atau nama project.",
        filled_answer="Wayang Bali Interactive" if filled else None
    )
    add_question_item(
        doc,
        q_num=4,
        title="Nama Lengkap Ketua / Peserta Individu *",
        q_type="isian singkat",
        help_text="Gunakan nama lengkap untuk administrasi lomba dan sertifikat.",
        filled_answer="I Putu Ngurah Harry Santika" if filled else None
    )
    add_question_item(
        doc,
        q_num=5,
        title="Nomor WhatsApp Ketua / Peserta Individu *",
        q_type="isian singkat",
        help_text="Contoh: 081337668803. Pastikan nomor aktif untuk koordinasi grup panitia.",
        filled_answer="081337668803" if filled else None
    )
    add_question_item(
        doc,
        q_num=6,
        title="Asal Sekolah / Kampus / Instansi *",
        q_type="isian singkat",
        help_text='Peserta umum/independen dapat menulis "Umum/Independen".',
        filled_answer="Umum / Independen" if filled else None
    )
    add_question_item(
        doc,
        q_num=7,
        title="Kabupaten/Kota Domisili *",
        q_type="isian singkat",
        help_text="Contoh: Denpasar, Badung, Gianyar.",
        filled_answer="Denpasar, Bali" if filled else None
    )
    add_question_item(
        doc,
        q_num=8,
        title="Nama Anggota 2",
        q_type="isian singkat, opsional",
        help_text="Kosongkan jika mengikuti lomba secara individu.",
        filled_answer="I Putu Adi Surya Arthayasa" if filled else None
    )
    add_question_item(
        doc,
        q_num=9,
        title="Nama Anggota 3",
        q_type="isian singkat, opsional",
        help_text="Kosongkan jika tim hanya terdiri dari 1–2 orang.",
        filled_answer="-" if filled else None
    )

    # Page 3: Profil MVP & Masalah yang Diselesaikan
    add_step_heading(doc, "Step 2", "Profil MVP & Masalah yang Diselesaikan (Halaman 3)", "Bantu juri memahami produk Anda secara singkat dan konkret.")
    add_question_item(
        doc,
        q_num=1,
        title="Nama Produk / MVP *",
        q_type="isian singkat",
        help_text="Nama singkat website/produk yang Anda submit.",
        filled_answer="Wayang Bali Interactive" if filled else None
    )
    add_question_item(
        doc,
        q_num=2,
        title="Bidang Solusi *",
        q_type="pilih satu",
        options=["Pendidikan", "UMKM & Bisnis", "Bali Smart Society"],
        filled_answer="Bali Smart Society" if filled else None
    )
    add_question_item(
        doc,
        q_num=3,
        title="Elevator Pitch Produk *",
        q_type="isian panjang",
        help_text="Jelaskan produk dalam 2–4 kalimat: masalah + solusi + siapa penggunanya.",
        answer_box_lines=4,
        filled_answer=(
            "Wayang Bali Interactive adalah aplikasi web interaktif yang memungkinkan masyarakat dan generasi muda "
            "merasakan pengalaman menjadi dalang digital secara langsung di depan kamera web tanpa sensor tambahan. "
            "Menggunakan Computer Vision on-device (Google MediaPipe WASM), gerak tangan fisik pengguna diterjemahkan secara "
            "real-time menjadi artikulasi dinamis tokoh wayang kulit Bali 2D (PixiJS v8) dengan algoritma Two-Bone Inverse Kinematics. "
            "Aplikasi ini juga diperkaya oleh asisten AI Tutor multimodal (Google Gemini & failover OpenAI) berbasis teks dan suara "
            "guna mengedukasi sejarah, filosofi, serta tradisi pewayangan Bali secara modern, menyenangkan, dan inklusif."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=4,
        title="Masalah Utama yang Ingin Diselesaikan *",
        q_type="isian panjang",
        help_text="Apa masalah nyata yang Anda temukan? Mengapa masalah tersebut penting?",
        answer_box_lines=5,
        filled_answer=(
            "1. Kesenjangan Generasi terhadap Seni Tradisi: Kesenian wayang kulit Bali yang sarat filosofi dan kearifan lokal "
            "makin terasing dari generasi muda akibat media edukasi budaya yang umumnya pasif, statis (buku teks/video dokumenter satu arah), "
            "dan minim daya tarik interaktif.\n"
            "2. Hambatan Aksesibilitas Sensor & Biaya: Pengalaman interaktif berbasis motion tracking di museum atau pameran umumnya "
            "memerlukan sensor khusus yang mahal (Kinect, Leap Motion) dan instalasi aplikasi native yang rumit.\n"
            "3. Privasi & Konsumsi Sumber Daya: Aplikasi interaktif berbasis kamera sering mengunggah video ke cloud, memicu kekhawatiran "
            "privasi pengguna, boros bandwidth, serta cepat memanaskan perangkat bergerak."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=5,
        title="Target Pengguna *",
        q_type="isian panjang",
        help_text="Siapa pengguna utama dan dalam konteks apa mereka menggunakan produk ini?",
        answer_box_lines=4,
        filled_answer=(
            "1. Pelajar & Generasi Muda: Mengeksplorasi budaya tradisional wayang Bali melalui simulasi dalang interaktif langsung dari smartphone/laptop.\n"
            "2. Pengunjung Pameran Seni & Kiosk Budaya: Menikmati instalasi budaya digital interaktif sesi kilat (3 menit) di festival seni/museum tanpa instalasi aplikasi.\n"
            "3. Guru & Pendidik Seni Budaya: Sebagai media peraga interaktif modern di kelas yang dilengkapi AI Tutor tanya-jawab budaya.\n"
            "4. Wisatawan Domestik & Mancanegara: Sarana pengenalan karakter, mitologi, dan tradisi Bali secara intuitif dan mandiri."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=6,
        title="Fitur Utama MVP yang Sudah Berfungsi *",
        q_type="isian panjang",
        help_text="Sebutkan fitur yang benar-benar dapat diuji saat ini, bukan fitur rencana.",
        answer_box_lines=6,
        filled_answer=(
            "1. Dual-Hand Independent Puppet Control: Tangan kiri fisik mengendalikan tokoh di slot kiri panggung dan tangan kanan mengendalikan slot kanan panggung (bisa dimainkan 1 atau 2 orang).\n"
            "2. Two-Bone Inverse Kinematics (IK): Translasi jari telunjuk dan jari tengah menggerakkan lengan utama dan lengan kedua wayang dengan batas sendi bahu/siku anatomis.\n"
            "3. Palm Tracking & Tilt: Posisi telapak tangan menggerakkan translasi badan wayang dan sudut kemiringan tangan membuat badan wayang condong dinamis.\n"
            "4. Facing Flip Gesture: Gestur tangan mengepal lalu meluruskan jari untuk membalikkan orientasi hadap tokoh wayang secara real-time.\n"
            "5. Hand Identity Persistence: Sistem pelacakan stabil dengan grace period 300 ms, mencegah wayang tertukar saat kedua tangan bersilangan (hand crossing).\n"
            "6. AI Tutor Wayang Bali Multimodal: Tanya jawab seputar tokoh dan filosofi wayang Bali via teks maupun rekaman suara mikrofon browser (didukung Text-to-Speech audio).\n"
            "7. Dual-Provider AI Failover: Menggunakan Google Gemini sebagai mesin utama dan beralih otomatis ke OpenAI jika batas kuota harian/rate limit (HTTP 429) tercapai.\n"
            "8. 100% On-Device Vision & Privacy: Komputasi AI visi komputer berjalan lokal di browser via WASM; tidak ada frame kamera yang diunggah ke server.\n"
            "9. Cache Offline & Streaming Asset Queue: Dukungan Service Worker untuk cache game dan antrean unduhan saat traffic ramai."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=7,
        title="Status Pengembangan Project *",
        q_type="pilih satu",
        options=[
            "Dibangun khusus/baru untuk kompetisi ini",
            "Sudah pernah dikembangkan sebelumnya dan dikembangkan lebih lanjut untuk kompetisi ini"
        ],
        filled_answer="Sudah pernah dikembangkan sebelumnya dan dikembangkan lebih lanjut untuk kompetisi ini" if filled else None
    )
    add_question_item(
        doc,
        q_num=8,
        title="Disclosure Project Sebelumnya",
        q_type="isian panjang, opsional",
        help_text="Jika project sudah pernah dikembangkan, jelaskan bagian yang sudah ada sebelumnya dan improvement yang dilakukan untuk lomba. Jika project baru, boleh dikosongkan.",
        answer_box_lines=4,
        filled_answer=(
            "Bagian awal berupa eksperimen tracking MediaPipe web prototype 1 tangan. Peningkatan masif (improvement) yang dilakukan khusus untuk Bali DigiFest 2026 meliputi:\n"
            "1. Rekayasa Dual-Hand Puppet System dengan algoritma Two-Bone Inverse Kinematics (IK) dan pencegah tertukar (hand identity persistence).\n"
            "2. Penambahan gesture control baru: gestur mengepal-lurus untuk membalik arah hadap wayang (Facing Flip Gesture).\n"
            "3. Integrasi penuh AI Tutor Multimodal (input suara & teks) dengan arsitektur dual-provider Gemini Flash-Lite dan automatic failover OpenAI di backend PHP.\n"
            "4. Engine rendering PixiJS v8 terkunci 30 FPS adaptif, antarmuka kelir interaktif (cahaya dan bayangan mengikuti kursor/sentuhan), dan PWA offline caching."
        ) if filled else None
    )

    # Page 4: Submission Teknis
    add_step_heading(doc, "Step 3", "Submission Teknis (Halaman 4)", "Pastikan semua link dapat dibuka oleh juri sebelum menekan Submit.")
    add_question_item(
        doc,
        q_num=1,
        title="URL Website MVP / Deployment *",
        q_type="isian singkat",
        help_text="Contoh: https://namaproject.vercel.app. Website harus dapat diakses juri.",
        filled_answer="https://wayangbali.hikari.my.id" if filled else None
    )
    add_question_item(
        doc,
        q_num=2,
        title="Akun Demo / Instruksi Login",
        q_type="isian panjang, opsional",
        help_text="Jika aplikasi membutuhkan login, tulis akun demo dan instruksi akses. Jangan menaruh credential sensitif yang digunakan di production.",
        answer_box_lines=3,
        filled_answer=(
            "Tidak memerlukan login atau akun demo. Aplikasi bersifat instan (zero-install):\n"
            "1. Buka https://wayangbali.hikari.my.id pada browser (Google Chrome / Edge / Safari).\n"
            "2. Izinkan akses kamera webcam saat diminta.\n"
            "3. Posisikan layar ponsel dalam posisi mendatar (Landscape).\n"
            "4. Pilih tokoh wayang untuk slot kiri dan/atau kanan, lakukan kalibrasi tangan 1,5 detik, dan panggung siap dimainkan!"
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=3,
        title="URL Repository GitHub *",
        q_type="isian singkat",
        help_text="Repository dapat public atau private. Jika private, pastikan panitia/juri memperoleh akses sesuai instruksi panitia.",
        filled_answer="https://github.com/harrysantika-hs-inAReality/wayangbali" if filled else None
    )
    add_question_item(
        doc,
        q_num=4,
        title="Status Repository GitHub *",
        q_type="pilih satu",
        options=["Public", "Private — akses juri/panitia sudah/akan diberikan"],
        filled_answer="Public" if filled else None
    )
    add_question_item(
        doc,
        q_num=5,
        title="Git Tag / Release / Commit Hash Submission *",
        q_type="isian singkat",
        help_text="Contoh: v1.0-submission atau commit hash GitHub yang menjadi versi resmi penyisihan.",
        filled_answer="Tag: v0.2.0  (Commit Hash: 7d23d666329aca4f7e1f164ee34ff76c8c67bf13)" if filled else None
    )

    # Page 5: AI & Technology Disclosure
    add_step_heading(doc, "Step 4", "AI & Technology Disclosure (Halaman 5)", "AI harus menjadi bagian material dari fungsi utama solusi. AI yang hanya dipakai untuk membantu coding tidak dihitung sebagai integrasi AI produk.")
    add_question_item(
        doc,
        q_num=1,
        title="Jenis Teknologi AI yang Digunakan *",
        q_type="checkbox, boleh pilih lebih dari satu",
        options=[
            "Large Language Model / Generative AI",
            "Natural Language Processing",
            "Computer Vision",
            "Recommendation System",
            "Prediction / Forecasting",
            "Classification / Machine Learning",
            "OCR / Document Intelligence",
            "Speech / Audio AI",
            "AI Agent / Agentic Workflow",
            "Lainnya"
        ],
        filled_answer=[
            "Large Language Model / Generative AI",
            "Natural Language Processing",
            "Computer Vision",
            "Speech / Audio AI",
            "AI Agent / Agentic Workflow"
        ] if filled else None
    )
    add_question_item(
        doc,
        q_num=2,
        title="Model / API / Layanan AI yang Digunakan *",
        q_type="isian panjang",
        help_text="Contoh: Gemini API, OpenAI API, Hugging Face model, model lokal, TensorFlow/PyTorch model, dsb.",
        answer_box_lines=4,
        filled_answer=(
            "1. Google MediaPipe Tasks Vision (`hand_landmarker.task` v1.0.1 via WebAssembly) — Model Computer Vision edge/on-device untuk pelacakan 21 sendi tangan 3D.\n"
            "2. Google Gemini API (`gemini-3.5-flash-lite`) — Model Large Language Model utama untuk penalaran AI Tutor Wayang Bali.\n"
            "3. OpenAI API (`gpt-4.1-mini`, Whisper Speech-to-Text, OpenAI TTS) — Model LLM cadangan (failover otomatis) serta pemrosesan suara ephemeral."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=3,
        title="Peran AI pada Fungsi Utama Produk *",
        q_type="isian panjang",
        help_text="Jelaskan input → proses AI → output. Jelaskan juga mengapa AI relevan untuk menyelesaikan masalah.",
        answer_box_lines=6,
        filled_answer=(
            "1. Pipeline Computer Vision (Dalang Motion Control):\n"
            "   - Input: Video stream kamera webcam lokal pengguna (640x480 @ 24-30 FPS).\n"
            "   - Proses AI: Model MediaPipe mengekstrak 21 titik landmark sendi 3D secara on-device melalui WASM, membedakan handedness kiri/kanan, dan menghitung kecepatan/posisi telapak. Koordinat diterjemahkan algoritma Inverse Kinematics ke artikulasi sendi wayang dan deteksi gestur.\n"
            "   - Output: Artikulasi gerak 2D real-time yang luwes pada tubuh dan lengan wayang kulit di panggung PixiJS.\n"
            "2. Pipeline AI Tutor Multimodal:\n"
            "   - Input: Pertanyaan teks (1-300 karakter) atau rekaman suara audio pengguna dari mikrofon (format WebM/OGG/MP4 ≤ 256 KiB).\n"
            "   - Proses AI: Transkripsi audio, inferensi konteks budaya Bali dengan model Gemini Flash-Lite (failover ke OpenAI jika rate-limited), filter pembatasan domain budaya wayang Bali, dan perangkuman respons ringkas (maks. 2 kalimat / ~55 kata).\n"
            "   - Output: Respons edukatif teks dan suara sintesis berbahasa Indonesia yang akurat dan komunikatif.\n"
            "Relevansi AI: Tanpa AI Vision on-device, interaksi dalang membutuhkan hardware sensor mahal. Tanpa LLM, transfer pengetahuan budaya hanya berupa teks statis yang kaku."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=4,
        title="AI-assisted Development Tools",
        q_type="isian panjang, opsional",
        help_text="Jika menggunakan ChatGPT, Gemini, GitHub Copilot, Claude, Cursor, atau tools sejenis untuk membantu coding/desain/dokumentasi, sebutkan di sini.",
        answer_box_lines=3,
        filled_answer=(
            "Google Antigravity / Gemini CLI, Claude Code, dan GitHub Copilot (digunakan untuk refactoring TypeScript strict, perancangan modul Inverse Kinematics, pengujian gestur otomatis, dan dokumentasi arsitektur PRD)."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=5,
        title="Third-party Resources & Data Disclosure *",
        q_type="isian panjang",
        help_text="Sebutkan API, library utama, dataset, template, model, atau aset pihak ketiga yang material terhadap produk.",
        answer_box_lines=5,
        filled_answer=(
            "1. Library/Framework: PixiJS v8 (rendering WebGL 2D), Google MediaPipe Tasks Vision (CV WASM), Vite 8 (bundler), TypeScript 7.\n"
            "2. Font Offline: @fontsource/cormorant-garamond & @fontsource/plus-jakarta-sans.\n"
            "3. Server Backend: Runtime PHP 8.1+ dengan ekstensi curl & mbstring untuk API Proxy aman dan token budget limiter.\n"
            "4. Aset Grafis & Audio: Ilustrasi ornamen pewayangan Bali, aset potongan tubuh 4 tokoh punokawan (Twalen, Merdah, Sangut, Delem), dan musik latar Gending Gender Wayang 'Pengrumrum' karya Astadi Jaya."
        ) if filled else None
    )
    add_question_item(
        doc,
        q_num=6,
        title="Catatan Privasi & Keamanan Data *",
        q_type="isian panjang",
        help_text="Jelaskan singkat data apa yang diproses dan langkah dasar untuk mencegah kebocoran data/API key/credential.",
        answer_box_lines=4,
        filled_answer=(
            "1. Privasi Kamera 100% Terjaga: Pemrosesan computer vision dilakukan 100% secara lokal di browser (on-device). Tidak ada frame kamera yang pernah dikirim, disimpan, atau di-stream ke server mana pun.\n"
            "2. Keamanan Kunci API: Seluruh API key (Gemini dan OpenAI) disimpan secara privat di lingkungan server (.env backend PHP). Tidak pernah diekspos ke kode frontend (tanpa awalan VITE_).\n"
            "3. Keamanan Audio Suara: Data rekaman suara pengguna hanya diproses di memori (in-memory) secara sementara untuk inferensi transkripsi dan langsung dibuang tanpa disimpan ke media penyimpanan."
        ) if filled else None
    )

    # Page 6: Proposal & Final Check
    add_step_heading(doc, "Step 5", "Proposal & Final Check (Halaman 6)", "Proposal disiapkan dalam PDF sesuai panduan lomba.")
    add_question_item(
        doc,
        q_num=1,
        title="UPLOAD PROPOSAL PDF *",
        q_type="upload file",
        help_text="Upload 1 supported file. Max 100 MB.",
        answer_box_lines=2,
        filled_answer="Proposal_Wayang_Bali_Interactive_BaliDigiFest2026.pdf (Disiapkan dan diunggah langsung melalui Google Forms)" if filled else None
    )
    add_question_item(
        doc,
        q_num=2,
        title="Link Cadangan Proposal PDF",
        q_type="isian singkat, opsional",
        help_text="Opsional. Gunakan hanya sebagai backup. Jika memakai Google Drive, pastikan juri memiliki akses.",
        filled_answer="https://drive.google.com/file/d/your-backup-proposal-link/view?usp=sharing" if filled else None
    )
    add_question_item(
        doc,
        q_num=3,
        title="Deklarasi Peserta *",
        q_type="checkbox, wajib dicentang",
        help_text=(
            "Dengan mencentang pernyataan ini, saya menyatakan bahwa:\n"
            "1. Data submission benar\n"
            "2. Karya merupakan karya yang sah dikembangkan oleh peserta/tim\n"
            "3. Penggunaan library, API, dataset, model, template, dan aset pihak ketiga telah diungkapkan\n"
            "4. Repository tidak sengaja mengekspos API key/password/secret\n"
            "5. Panitia dan juri diperbolehkan mengakses link submission untuk keperluan verifikasi dan penilaian\n"
            "6. Saya bersedia mengikuti ketentuan lomba dan keputusan juri"
        ),
        options=["Saya menyatakan setuju dan bertanggung jawab atas submission ini."],
        filled_answer=["Saya menyatakan setuju dan bertanggung jawab atas submission ini."] if filled else None
    )

    # Save document
    doc.save(output_path)
    print(f"Berhasil menyimpan dokumen: {output_path}")

if __name__ == "__main__":
    base_dir = r"C:\Users\inAReality\Desktop\wayangbali"
    
    # 1. Generate clean template docx from form-register.md
    out_blank = os.path.join(base_dir, "form-register.docx")
    generate_form_docx(out_blank, filled=False)
    
    # 2. Generate filled submission draft docx with Wayang Bali Interactive data
    out_filled = os.path.join(base_dir, "form-register-jawaban.docx")
    generate_form_docx(out_filled, filled=True)
    print("Semua dokumen DOCX selesai dibuat dengan sukses!")
