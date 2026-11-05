# Wayang Bali Interactive — Product Requirements Document (PRD)

> **Versi produk:** 0.2.0 · **Dokumen diperbarui:** 2026-11-05
> **Status:** Living document — *source of truth* untuk produk, arsitektur, dan batas performa.
> **Pengganti:** `agent/PROJECT_SPEC.md` (baseline technical specification).
> **Aturan:** Perubahan berarti pada fitur, arsitektur, atau target performa **wajib memperbarui dokumen ini lebih dulu**.

Legenda status: ✅ sudah diimplementasi · 🟡 sebagian · ⏳ backlog (belum ada di kode).

---

## 1. Ringkasan Produk

Wayang Bali Interactive adalah aplikasi web yang menjadikan siapa pun *dalang* digital. Kamera laptop/HP membaca gerak tangan secara lokal (MediaPipe via WebAssembly), lalu tiap tangan fisik menggerakkan satu tokoh Wayang Bali di panggung PixiJS. AI Tutor (Gemini dengan fallback OpenAI) menjawab pertanyaan seputar wayang Bali lewat teks atau suara.

```text
Tangan kiri fisik  -> Slot LEFT  -> Wayang A
Tangan kanan fisik -> Slot RIGHT -> Wayang B
```

## 2. Masalah & Tujuan

**Masalah**
- Wayang kulit Bali makin jauh dari generasi muda; media belajarnya statis.
- Pengalaman interaktif berbasis gerak biasanya butuh sensor mahal (Kinect, Leap Motion) atau aplikasi native.

**Tujuan produk**
1. Pengunjung bisa memainkan wayang dengan tangan sendiri dalam < 1 menit sejak membuka halaman, tanpa instalasi atau sensor tambahan.
2. Gerak wayang terasa stabil, halus, dan tidak tertukar antar tangan.
3. Pengunjung bisa belajar sejarah, tokoh, dan tradisi wayang Bali lewat AI Tutor.
4. Berjalan baik di HP kelas menengah tanpa cepat panas atau boros baterai.
5. Privasi terjaga: video kamera tidak pernah keluar dari perangkat.

**Ukuran keberhasilan**
| Metrik | Target |
|---|---|
| Waktu HOME → PLAYING | < 60 detik (termasuk izin kamera dan kalibrasi 1,5 dtk) |
| Render FPS | stabil ≤ 30, tanpa jank yang terlihat |
| Tertukarnya wayang saat tangan bersilangan | tidak terjadi pada uji silang normal |
| Sesi berulang (kiosk) | stabil, tanpa kebocoran memori atau kamera menggantung |
| Jawaban AI Tutor | ≤ 2 kalimat / ±55 kata, relevan dengan wayang Bali |

## 3. Pengguna & Konteks

| Persona | Kebutuhan |
|---|---|
| **Pelajar / generasi muda** | Pengalaman seru dan cepat, belajar budaya tanpa terasa seperti pelajaran |
| **Pengunjung pameran / kiosk** | Sesi singkat (3 menit), langsung main, reset otomatis untuk pengunjung berikutnya |
| **Guru / pemandu budaya** | Bahan peraga interaktif + tutor yang menjawab pertanyaan murid |
| **Pemilik proyek (klien)** | Mudah dideploy di hosting Apache + PHP, biaya API AI terkendali |

Perangkat target: Android phone/tablet, iPhone, iPad, laptop, desktop (browser modern). HP wajib *landscape* saat bermain.

## 4. Ruang Lingkup

**Dalam scope**
- Panggung wayang dua tangan (1 atau 2 tokoh), 4 tokoh di katalog.
- Kalibrasi tangan, sesi 3 menit, layar selesai.
- Gestur membalik arah hadap wayang.
- AI Tutor teks + suara (Gemini dengan fallback OpenAI, backend PHP).
- Cache offline aset game + antrean unduhan saat traffic ramai.

**Di luar scope (non-goals)** — jangan ditambahkan tanpa memperbarui PRD:
- Mode 60 FPS atau rendering 3D/Three.js.
- Unggah, simpan, atau streaming frame kamera ke server.
- Database, login/akun, multiplayer online.
- Efek suara gameplay (selain backsound F13) dan sistem partikel berat.
- Editor pivot atau halaman debug publik.
- Riwayat chat tutor (tiap pertanyaan berdiri sendiri).

## 5. Alur Pengguna

```text
HOME ──▶ TUTOR (opsional, bisa dari HOME atau pemilihan wayang)
  │
  ▼
CHARACTER_SELECTION  (pilih tokoh untuk slot LEFT dan/atau RIGHT)
  ▼
START_CAMERA         (izin kamera, satu stream, muat MediaPipe)
  ▼
CALIBRATION          (tangan terpilih terdeteksi stabil 1,5 dtk)
  ▼
PLAYING              (3 menit; berakhir lebih cepat jika tidak ada tangan 25 dtk)
  ▼
SESSION_COMPLETE     (kamera mati, rig dihancurkan)
                     Opsi: MAIN LAGI · GANTI WAYANG · MENU UTAMA
```

- **GANTI WAYANG** tersedia saat startup, kalibrasi, dan bermain: hentikan tracking, lepas kamera, hancurkan rig, kembali ke pemilihan.
- **MENU UTAMA** selalu tersedia saat bermain.
- State dikelola satu *state machine* terpusat (`src/app/GameApp.ts`), bukan kumpulan boolean.

## 6. Kebutuhan Fungsional

### F1. Katalog & pemilihan tokoh ✅
- Tepat 4 tokoh: `wayang01`–`wayang04`. Jumlah lengan: 01=2, 02=1, 03=2, 04=2.
- Pilih minimal 1, maksimal 2 tokoh sebelum kamera menyala. Satu tokoh per slot; tokoh yang sama tidak boleh di dua slot. Tangan tanpa slot tidak punya wayang.
- Slot ditentukan eksplisit (LEFT/RIGHT), bukan dari urutan klik atau posisi X layar.
- Gambar `reference` hanya untuk thumbnail beranda/pemilihan, tidak pernah dimuat oleh rig gameplay.
- Hanya rig tokoh terpilih (maks. 2) yang dibuat dan dimuat.
- **Desain layar:** latar kayu yang sama dengan beranda. Tiap tokoh tampil di kartu kelir kecil (berdiri di gedebong, bayangan statis); tombol Kiri/Kanan per kartu. Kartu terpilih diberi bingkai merah *plangkan* + label sisi di sudut yang sesuai, dan tokoh dibalik agar menghadap ke tengah panggung. Dock bawah menampilkan slot tangan kiri/kanan (thumbnail + nama) dan tombol Mulai bermain. Grid: 4 kolom desktop, 2 tablet, 2 HP; landscape pendek memuat semuanya dalam satu layar.

### F2. Kamera ✅
- Mati selama HOME dan CHARACTER_SELECTION. Satu stream dipakai ulang sepanjang sesi.
- Constraint: `audio: false`, `facingMode: "user"`, ideal 640×480, frameRate ideal 24 / max 30. Jangan minta 1080p.
- Preview video mentah, *mirrored*, kecil di kiri bawah (180×135 desktop, 140×105 mobile, z=20). Background z=0, canvas Pixi transparan z=1, UI z=10.
- **Overlay kerangka tangan** (`src/camera/HandOverlay.ts`, canvas z=21 di atas preview): 21 titik sendi + garis tulang untuk tiap tangan yang dilacak — emas = tangan kiri (slot LEFT), krem = tangan kanan (slot RIGHT); ujung telunjuk & jari tengah (pengendali lengan) diberi lingkaran. Digambar hanya saat hasil MediaPipe tiba (tanpa loop sendiri), mengikuti crop `object-fit: cover` dan mirroring preview; dibersihkan saat sesi berakhir.
- Semua track dihentikan (`track.stop()`) saat sesi selesai, ganti wayang, error, atau keluar halaman. Menyembunyikan video saja tidak cukup.

### F3. Deteksi tangan ✅
- MediaPipe Hand Landmarker: `runningMode = VIDEO`, `numHands = 2`, satu instance per sesi.
- Hanya memproses frame kamera baru: `requestVideoFrameCallback()` dengan identitas `presentedFrames`, fallback decoded-frame/currentTime untuk Safari/Android lama.
- API MediaPipe harus diverifikasi terhadap versi yang terpasang (`@mediapipe/tasks-vision` 1.0.1).

### F4. Identitas tangan persisten ✅
- Wayang **tidak boleh tertukar** saat tangan bersilangan, berdekatan, hilang beberapa frame, handedness berubah, confidence turun, atau keluar-masuk frame.
- Pencocokan track memakai posisi telapak terprediksi, kecepatan, orientasi, dan handedness sebagai *soft prior*. Cukup evaluasi 2 kemungkinan assignment (tanpa Hungarian).
- Hasil landmark valid boleh memulai track walau confidence handedness < 0,65; label handedness tetap sinyal utama LEFT/RIGHT.
- Mirroring preview CSS tidak mengubah kepemilikan tangan.
- **Grace period 300 ms:** saat tracking hilang sebentar, pertahankan target badan dan lengan terakhir; jangan langsung tukar, reset, atau sembunyikan wayang.

### F5. Kalibrasi ✅
- Hanya tangan fisik yang dipakai slot terpilih, terdeteksi konsisten 1,5 detik (jeda > 300 ms mereset hitungan).
- Feedback visual jelas selama kalibrasi.

### F6. Gerak badan wayang ✅
- Palm X/Y → posisi wayang; orientasi telapak → kemiringan badan (tidak 1:1, mis. ±90° → ±15°, configurable per tokoh).
- Batas gerak X per slot: LEFT 5%–65%, RIGHT 35%–95%; tumpang tindih di tengah diizinkan. Clamp halus, tanpa *hard snap*.

### F7. Artikulasi lengan (Two-Bone IK) ✅
- Telunjuk → lengan utama/kiri; jari tengah → lengan sekunder/kanan (hanya jika tokoh punya lengan kedua).
- Target: landmark jari → target batang virtual → target tangan wayang → IK 2 tulang → rotasi bahu & siku.
- Tiap sendi punya batas rotasi; tidak boleh berputar 360° tak terkendali. Tiap lengan mendeklarasikan `elbowDirection` tetap.
- Lengan dominan/telunjuk memakai gain lebih besar dari lengan sekunder. Gain awal Wayang01: 4.0/4.0 dan 2.5/2.5.

### F8. Gestur balik arah hadap ✅
- Kepal ±0,5 dtk → luruskan 4 jari dengan ibu jari terlipat, tahan ±1 dtk → wayang berbalik arah.
- Satu gestur = satu kali balik; harus kepal lagi untuk mengulang. Cooldown 1,8 dtk. Tiap tangan hanya membalik wayangnya sendiri.
- Konfigurasi durasi: `src/controller/FacingGesture.ts`. Tes: `npm run test:gesture`.

### F9. Sesi ✅
- Durasi default 3 menit; sesi berakhir lebih awal jika tidak ada tangan 25 detik.
- **Layar Sesi selesai:** tokoh yang baru dimainkan (gambar `reference` seperti beranda, dengan bayangan) tertancap di gedebong pada kelir yang diterangi dan saling berhadapan; keempat tokoh jika tidak ada pilihan. Tokoh naik sekali saat layar muncul (mati saat `prefers-reduced-motion`). Teks menyebut tokoh yang baru dimainkan; tombol Main lagi · Ganti wayang · Menu utama. Di HP landscape: gunungan kiri, teks kanan, muat satu layar.
- Pembersihan akhir sesi: hentikan loop inference, kosongkan track, reset gestur dan pose, bersihkan timer/listener, lepas kamera, hancurkan rig/grafis sementara. Harus stabil untuk sesi berulang (kiosk).

### F10. Antarmuka ✅
- **Beranda = kelir.** Layar wayang (kain diterangi *blencong*) di dalam bingkai kayu gelap dengan tepi merah (*plangkan*). Keempat tokoh berdiri di *gedebong* (batang pisang) dan menebar bayangan di kelir. **Kursor/sentuhan = lampu:** bayangan tiap tokoh bergeser menjauhi posisi kursor (maks. ±70 px X, ±34 px Y) dan cahaya kelir mengikuti kursor (`src/app/KelirLight.ts`); kursor keluar → lampu kembali ke posisi awal. Dihitung hanya saat ada event pointer (satu `requestAnimationFrame` per frame), tanpa loop idle. Ditambah kedip lampu halus (hanya `transform`/`opacity`; mati saat `prefers-reduced-motion`). Di bawahnya: 3 langkah cara bermain dan kredit musik.
- Font di-*self-host* lewat `@fontsource` (Cormorant Garamond untuk judul, Plus Jakarta Sans untuk teks) agar ikut cache offline. Jangan memakai CDN font.
- Breakpoint beranda: desktop (2 kolom), ≤ 900 px (teks di atas panggung), ≤ 560 px (tombol penuh lebar), landscape ≤ 560 px tinggi (2 kolom, muat satu layar).
- Layar lain memakai antarmuka kaca (*glassmorphism*) off-white responsif dengan ornamen emas Bali di sisi.
- HP harus landscape sebelum mulai; jika kembali portrait saat bermain, tampilkan pemberitahuan rotasi yang memblokir.
- Pesan error harus mudah dipahami pengguna awam (bahasa Indonesia).
- **Instruksi saat bermain** (pesan status kalibrasi/tangan hilang dan petunjuk gestur): font besar (±21 px desktop, ±17 px HP landscape), latar kayu gelap, lebar dibatasi agar tidak menutupi preview kamera. Saat teks berganti → animasi fade-up 320 ms; tidak diputar ulang bila instruksi berganti lebih cepat dari 450 ms (anti kedip), dan mati saat `prefers-reduced-motion`. DOM hanya ditulis saat teks benar-benar berubah (bukan tiap frame).

### F11. AI Tutor Wayang Bali ✅
- Masuk dari beranda dan pemilihan wayang. Empat tokoh tampil sebagai galeri; pengguna langsung mengetik atau menekan **Bicara** tanpa memilih tokoh.
- Cakupan: semua tokoh, jenis, sejarah, perkembangan, dan tradisi wayang yang hidup di Bali (termasuk yang tidak ada di galeri). Topik di luar wayang Bali dan upaya mengubah peran ditolak.
- **Teks:** maks. 300 karakter. **Suara:** MediaRecorder (MP4 untuk iPhone, WebM/OGG lainnya), rekaman maks. 15 dtk lalu dikirim otomatis; payload audio maks. 256 KiB di server; header kontainer divalidasi. Tidak bergantung pada SpeechRecognition. Dilengkapi indikator visual animasi gelombang suara dan hitung mundur saat pengguna berbicara (tersembunyi saat belum memakai audio). Hasil transkripsi rekaman suara pengguna ditampilkan pada bubble percakapan chatbot.
- Gemini tetap utama; pada HTTP 429 (kuota/rate limit), server mencoba OpenAI sekali. Jika key Gemini kosong, OpenAI dapat dipakai langsung. Batas lokal situs tetap berlaku, dihitung sekali per pertanyaan.
- OpenAI memakai Responses API untuk jawaban, transkripsi rekaman di memori, dan Speech API untuk MP3 bila opsi suara aktif. Key/model/voice di `.env` server. Kegagalan TTS tidak membatalkan jawaban teks.
- Jawaban Gemini dibacakan `speechSynthesis` perangkat; jawaban fallback memakai suara OpenAI (suara buatan AI) dengan cadangan `speechSynthesis` jika audio gagal. Audio berhenti saat tab tersembunyi, merekam, atau tutor ditutup. Teks tetap bisa dipakai bila izin mikrofon ditolak.
- Satu pertanyaan tanpa riwayat; target 2 kalimat/55 kata; `maxOutputTokens` default 180 (hard limit 240).
- Rekaman tidak disimpan aplikasi. Endpoint tutor tidak masuk cache offline; tutor butuh internet.

### F12b. Aturan semua layar loading ✅
- Progress tampil berjalan dari **0% sampai 100%** dan layar baru berganti **setelah** tampilan mencapai 100%.
- **Minimal 2 detik** per layar loading, walau datanya sudah siap lebih cepat. Lebih lama jika data asli memang lebih lama.
- Diatur oleh `src/progressPacer.ts`: tampilan mengejar progress asli, dibatasi naik maks. 100% per 2 detik; timer 30 fps (tetap berjalan di tab latar), berhenti sendiri saat menunggu.
- Pengecualian: tepat setelah unduhan pertama selesai (bar sudah mencapai 100%), reload berikutnya langsung membuka aplikasi tanpa mengulang bar.

### F12a. Progress "Menyiapkan panggung" ✅
- Panel di tengah panggung saat START_CAMERA: persen besar, bar gedebong yang terisi cahaya, dan label tahap. Diperbarui langsung di DOM (tanpa render ulang UI).
- Bobot: gambar wayang 0–35% (per file) → kamera 35–50% (label meminta izin kamera) → unduh model pelacak tangan 52–90% (per byte, streaming) → inisialisasi 90–100%. Persen tidak pernah mundur.

### F12. Offline cache & antrean unduhan ✅
- Layar unduhan "Mohon tunggu, sedang menyiapkan aset dan aplikasi" bergaya kelir (latar kayu, gunungan bercahaya, persen besar, bar gedebong). Progress dihitung **per potongan data (streaming)**, bukan per file, sehingga naik mulus 0–100%; ukuran file/unduhan dan keterangan paket hanya diunduh sekali tidak ditampilkan. Body disimpan ke cache tanpa header `content-encoding`. Font dimuat dari `bootstrap.ts` agar layar ini memakai font yang sama.
- Service worker (`public/sw.js`) menyimpan aset game agar kunjungan berikutnya cepat/offline. Manifest cache dibuat saat build (`scripts/generate-cache-manifest.mjs`).
- `public/queue.php` membatasi maks. 3 unduhan aktif bersamaan (TTL klien 45 dtk) agar server tidak kewalahan.

### F13. Backsound ✅
- Musik latar (`assett/backsound.mp3`) berulang, volume 0,5; mulai pada interaksi pertama (kebijakan autoplay browser).
- Tombol AUDIO ON/OFF selalu tersedia; musik tidak diputar di layar AI Tutor agar tidak bertabrakan dengan suara tutor.

## 7. Kebutuhan Non-Fungsional

### 7.1 Prioritas (urutan tidak boleh dibalik)
1. Stabilitas tracking
2. Konsistensi interaksi
3. Latensi rendah
4. Efisiensi baterai
5. Efisiensi termal
6. Gerak wayang halus
7. Kompatibilitas mobile
8. Arsitektur mudah dirawat
9. Efek visual

Efek visual tidak boleh mengorbankan tracking, suhu perangkat, atau baterai.

### 7.2 Performa
| Komponen | Target | Batas keras |
|---|---|---|
| Renderer PixiJS | 30 FPS, satu ticker untuk seluruh panggung, drift-corrected | **30 FPS** |
| Kamera | 640×480 @ 24 FPS | 30 FPS |
| MediaPipe | 20 FPS normal (1 atau 2 wayang) | 30 FPS |
| Device pixel ratio | — | `min(devicePixelRatio, 2)` |
| Tekstur | 1K–2K per bagian | hindari 4K PNG transparan |

- **Tidak ada mode 60 FPS**, termasuk di layar 90/120/144 Hz. 30 FPS adalah *ceiling*, bukan target minimum.
- Inference dan render terpisah: tiap hasil MediaPipe memperbarui target controller sekali; render 30 FPS menginterpolasi semua wayang di antara hasil.
- **Adaptif ✅ (sederhana, `src/app/CameraSession.ts`):** rata-rata waktu inference > 55 ms → 12 FPS; > 35 ms → 15 FPS; < 25 ms → kembali 20 FPS; dievaluasi tiap ≥ 2 dtk setelah ≥ 20 frame. Tanpa tangan terdeteksi → maks. 12 FPS.
- **Tab tersembunyi ✅:** Page Visibility API menjeda inference, render, dan suara tutor. Resume tidak boleh membuat loop ganda.

### 7.3 Smoothing
- Landmark mentah tidak boleh langsung menggerakkan sprite.
  `RAW → FILTERED → PUPPET TARGET → INTERPOLATED RENDER STATE`
- Baseline EMA, *frame-rate independent* (alpha dihitung dari deltaMS). Smoothing badan terpisah dari smoothing per lengan. Rotasi di-smooth dengan penanganan *angle wrapping*.
- Arsitektur harus memungkinkan One Euro Filter ditambahkan nanti.

### 7.4 Baterai & termal — hindari
MediaPipe 30 FPS terus-menerus · input CV 1080p · DPR tinggi · loop ganda · filter Pixi berlebihan · partikel besar · alokasi per-frame yang tidak perlu · kamera aktif saat idle · inference di tab latar belakang.

### 7.5 Privasi & keamanan
- Pemrosesan kamera 100% lokal. **Tidak ada frame webcam yang diunggah ke backend.** Teks privasi: *"Video kamera diproses langsung pada perangkat dan tidak disimpan."*
- Audio tutor dikirim ke backend/Gemini atau OpenAI hanya saat pengguna menekan Bicara, dan tidak disimpan aplikasi.
- `GEMINI_API_KEY` dan `OPENAI_API_KEY` hanya di `.env` server, **tidak pernah** berawalan `VITE_` atau masuk bundle frontend. `.env` di luar document root `dist`; `.htaccess` menolak akses `.env*`.
- Rate limit tutor: 12 permintaan/menit dan default 300/hari UTC untuk seluruh situs (`TUTOR_DAILY_LIMIT`); percobaan koneksi Gemini ikut dihitung.
- Tutor tidak boleh diberi alat atau akses data sensitif. Pembatasan lewat prompt bukan jaminan absolut.

### 7.6 Penanganan error
Izin kamera ditolak · kamera tidak tersedia/terputus · browser tidak didukung · gagal memuat/inisialisasi MediaPipe · gagal inisialisasi Pixi/WebGL · perubahan orientasi & resize · tab latar/kembali · kamera restart · gagal/limit tutor.

### 7.7 Aksesibilitas & SEO
- Semantic HTML, kontras teks cukup di atas latar kaca, tombol dapat diakses keyboard, label jelas berbahasa Indonesia.
- Halaman publik punya title, meta description, Open Graph, dan konten yang bisa dikutip AI search (lihat skill `seo`, `ai-seo`).

## 8. Arsitektur

### 8.1 Teknologi
| Lapisan | Teknologi |
|---|---|
| Bahasa | TypeScript 7 (strict) |
| Build | Vite 8 |
| Computer vision | `@mediapipe/tasks-vision` 1.0.1 — Hand Landmarker (WASM, lokal) |
| Rendering 2D | PixiJS 8 (WebGL) |
| UI | HTML5 semantik + Vanilla CSS (tanpa framework) |
| Backend tutor | PHP >= 8.1 (ekstensi curl, mbstring) + Google Gemini API (`gemini-3.5-flash-lite` default) + fallback OpenAI |
| Hosting | Apache + `.htaccess`; deploy `dist/`, `server/`, `.env` dengan struktur direktori utuh |
| Test | Node test runner (`node --test`) |

### 8.2 Pipeline gameplay
```text
Kamera (640x480) → VideoFrameLoop (frame baru saja, FPS adaptif)
  → HandLandmarkerManager (MediaPipe)
  → HandTrackManager (identitas LEFT/RIGHT persisten)
  → HandPuppetController (pemetaan + EMA + FacingGesture)
  → TwoBoneIK → PuppetRig → PixiRenderer (≤ 30 FPS)
```

### 8.3 Struktur modul (aktual)
```text
src/
├── main.ts, bootstrap.ts       # entry, service worker, antrean unduhan
├── app/        GameApp.ts (state machine, UI, sesi), CameraSession.ts (loop inference + FPS adaptif)
├── camera/     CameraManager.ts, VideoFrameLoop.ts
├── vision/     HandLandmarkerManager.ts
├── tracking/   HandTrackManager.ts
├── controller/ HandPuppetController.ts, FacingGesture.ts
├── puppet/     PuppetDefinition.ts, PuppetRig.ts, TwoBoneIK.ts, characters/ (catalog + wayang01–04)
├── rendering/  PixiRenderer.ts
├── tutor/      Tutor.ts, VoiceRecorder.ts
└── style.css
server/tutor.php     # validasi, budget, Gemini dan routing fallback (di luar document root)
server/openai.php    # Responses API, transkripsi di memori, dan TTS
public/tutor.php     # pemuat tipis → server/tutor.php
public/queue.php     # antrean unduhan
public/sw.js         # service worker
```

### 8.4 Batas tanggung jawab
Camera ≠ Vision ≠ Tracking ≠ Gesture ≠ Puppet/Rendering ≠ App state ≠ Tutor.
Jangan gabungkan kalkulasi MediaPipe, logika gestur, rendering Pixi, dan lifecycle kamera dalam satu file. Konversi koordinat (kamera → normalized → stage, termasuk mirroring dan aspect ratio) tidak boleh tersebar di banyak file.

### 8.5 Data tokoh (data-driven)
`src/puppet/PuppetDefinition.ts` + `src/puppet/characters/catalog.ts`.

```ts
interface PuppetDefinition {
  id: string;
  name: string;
  canvas: { width: number; height: number };
  defaultScale: number;
  assets: { body: string; mainRod?: string; reference?: string };
  rootPivot: PuppetPoint;
  arms: readonly PuppetArmDefinition[]; // 0, 1 atau 2
  layers: readonly string[];
  movementBounds: MovementBounds;
  smoothing: number;
  bodyRotation: { gain: number; max: number };
}
```

- Tiap lengan: path aset, pivot bahu/siku, anchor tangan, batas rotasi bahu/siku, `elbowDirection`, pemetaan telunjuk/tengah, gain X/Y, smoothing.
- Nilai khusus tokoh **hanya** di konfigurasi, tidak pernah di controller atau rig generik.
- Aset per tokoh: `public/assets/characters/<id>/` — `body.png`, lengan atas, lengan bawah + telapak, batang (cempurit) opsional, `reference.png` opsional. Rig: PNG/SVG rigid + rotasi pivot lokal + transform parent-child; tanpa mesh deformation berlebihan. Z-order: lengan belakang → badan → lengan depan.
- Tokoh baru (Arjuna, Bima, Hanoman, Rahwana, dll.) = definisi + artwork baru, **tanpa** menulis ulang controller.

## 9. Backlog (belum diimplementasi)

| Item | Status | Catatan |
|---|---|---|
| Profil performa LOW/MEDIUM/HIGH dengan benchmark startup (warmup 10–20 frame, benchmark 20–30 frame) | ⏳ | Saat ini hanya FPS adaptif sederhana (F7.2) |
| Deteksi degradasi termal dengan hysteresis & p95 inference | 🟡 | Rata-rata inference sudah memicu turun/naik FPS |
| MediaPipe di Web Worker | ⏳ | Hanya jika stabil di semua browser target; robust > dipaksakan |
| Debug overlay `?debug=true` (FPS, inference ms, track, handedness, confidence) | ⏳ | Tidak boleh tampil default di production |
| Gesture state machine lengkap (pinch, greeting, attack) dengan enter/exit threshold, durasi minimum, cooldown | ⏳ | Baru gestur balik arah (F8) |
| Transisi bertahap ke pose idle setelah grace period (300–800 ms) dan indikator tracking hilang | ⏳ | |
| One Euro Filter | ⏳ | Opsional |
| Sprite atlas & sprite ter-crop dengan metadata pivot/offset | ⏳ | Saat ini PNG ukuran kanvas sama |
| Kompres backsound (saat ini ±6 MB, diunduh di beranda) | ⏳ | Berat untuk data seluler |

## 10. Requirement Kritis (non-negotiable)

Hanya boleh dilanggar jika dokumen ini diperbarui secara eksplisit.

1. Render FPS maks. 30; tidak ada mode 60 FPS, termasuk di perangkat high-end.
2. MediaPipe FPS maks. 30; normal ±15–20; tidak dipaksa 30 terus-menerus.
3. Renderer dan inference terpisah (decoupled).
4. Kamera 640×480, preferred 24 FPS, maks. 30 FPS; tidak aktif saat tidak perlu; dimatikan setelah sesi.
5. Maks. 2 tangan; satu tangan fisik = satu wayang persisten; tidak mudah tertukar; tangan bersilangan dan kehilangan tracking sesaat ditangani.
6. Landmark mentah selalu di-smooth.
7. Lengan wayang dari artwork terpisah, pivot configurable, IK 2 tulang, rotasi sendi dibatasi. Jangan sederhanakan jadi satu gambar rigid.
8. Inference berat berhenti saat halaman tersembunyi.
9. Sesi default 3 menit; stabil untuk sesi berulang.
10. Tidak ada frame webcam yang dikirim ke backend.
11. API key hanya di server; tidak pernah di bundle frontend.
12. DPR dibatasi maks. 2; mobile adalah target utama.
13. Tokoh baru memakai arsitektur controller generik.

## 11. Definition of Done (per perubahan)

Sebuah fitur/perbaikan dianggap selesai jika:
- Memenuhi requirement terkait di PRD ini (atau PRD sudah diperbarui).
- `npm run build` lulus (sudah termasuk `npm run typecheck`).
- `npm run test:gesture` lulus jika menyentuh gestur/controller.
- `php -l server/tutor.php` lulus jika menyentuh backend.
- Tidak melanggar Requirement Kritis (§10).
- Dicek manual di browser: kamera menyala/mati benar, wayang bergerak halus, sesi bisa diulang.
- Commit memakai Conventional Commits.

## 12. Instruksi untuk AI Agent

Berlaku untuk semua AI coding assistant (Claude Code, Codex, Cursor, Copilot, Gemini, dll.). Ringkasan wajib juga ada di `AGENTS.md` di root repo.

```text
- Baca PRD ini sebelum perubahan arsitektur atau implementasi. PRD = source of truth.
- Baca skill yang relevan di .agents/skills/<nama>/SKILL.md sebelum mengerjakan tugasnya.
- Periksa kode yang ada sebelum mengedit; jangan menulis ulang fungsi yang sudah bekerja.
- Patuhi §10 Requirement Kritis dan §4 Non-goals.
- Jaga batas modul (§8.4).
- Jalankan build/test sesuai §11 setelah perubahan berarti; perbaiki error yang kamu buat.
- Perbarui PRD lebih dulu bila mengubah fitur, arsitektur, atau target performa.
```

Format laporan di akhir tiap tahap:

```text
DONE   - fitur yang diimplementasi
FILES  - file ditambah / diubah
TEST   - perintah yang dijalankan + hasil
NEXT   - rekomendasi langkah berikutnya
```
