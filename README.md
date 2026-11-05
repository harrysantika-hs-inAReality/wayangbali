# 🎭 Wayang Bali Interactive (Wayang Convis)

> **Panggung Wayang Digital Interaktif Berbasis AI, Computer Vision, dan WebAssembly**  
> *Menghidupkan seni tradisi Wayang Bali melalui gerak tangan secara langsung di depan kamera laptop maupun smartphone tanpa memerlukan sensor tambahan.*

---

## 📖 1. Pengenalan Proyek

**Wayang Bali Interactive** adalah aplikasi web interaktif yang memungkinkan siapa saja menjadi seorang *Dalang* digital. Dengan memanfaatkan kecerdasan buatan (*Computer Vision*) melalui kamera web (webcam), gerakan tangan fisik Anda akan langsung diterjemahkan menjadi gerakan tokoh Wayang Bali di layar.

### 🌟 Mengapa Proyek Ini Dibuat?
- **Pelestarian Budaya**: Membawa kebudayaan adiluhung wayang kulit Bali ke generasi muda melalui media digital yang menyenangkan dan interaktif.
- **Kemudahan Akses**: Berjalan langsung di peramban web (*browser*) tanpa perlu mengunduh aplikasi tambahan atau membeli perangkat sensor khusus yang mahal (seperti Leap Motion atau Kinect). Cukup bermodalkan webcam bawaan laptop atau kamera depan smartphone.
- **Privasi 100% Terjaga**: Seluruh proses pemindaian gambar dan pengenalan gerakan dilakukan secara **lokal di perangkat pengguna** (*on-device* via WebAssembly). Tidak ada satu pun frame video atau data kamera yang dikirim ke server.

---

## ✨ 2. Fitur Utama

1. **Kontrol Dua Tangan Independen (Dual-Hand Control)**:
   - Tangan kiri fisik mengendalikan tokoh di panggung sebelah kiri (*Left Slot*).
   - Tangan kanan fisik mengendalikan tokoh di panggung sebelah kanan (*Right Slot*).
   - Anda dapat memainkan 1 tokoh saja atau 2 tokoh sekaligus bersama teman.
2. **Artikulasi Lengan Dinamis dengan Inverse Kinematics (Two-Bone IK)**:
   - Tokoh wayang memiliki sendi pundak dan siku yang bergerak fleksibel seperti wayang kulit asli.
   - Jari telunjuk menggerakkan lengan utama (depan/kiri).
   - Jari tengah menggerakkan lengan sekunder (belakang/kanan).
   - Algoritma *Two-Bone IK* menghitung sudut putaran sendi secara anatomis agar tidak berputar aneh (mencegah putaran 360 derajat yang patah).
3. **Pelacakan Posisi & Sudut Badan (Palm Tracking & Body Tilt)**:
   - Posisi telapak tangan (X dan Y) menggerakkan tubuh wayang di panggung.
   - Kemiringan telapak tangan membuat badan wayang ikut condong secara proporsional.
   - Untuk membalik arah hadap saat bermain, kepalkan tangan sekitar 0,5 detik, lalu luruskan telunjuk, jari tengah, jari manis, dan kelingking dengan ibu jari dilipat ke telapak. Tahan sekitar 1 detik.
   - Satu gestur hanya membalik sekali. Kepalkan kembali sebelum mengulang; jeda pengaman 1,8 detik mencegah pembalikan terlalu cepat. Jika pelacakan terputus, kepalkan lagi untuk mengaktifkan gestur. Masing-masing tangan hanya membalik wayang yang dikendalikannya.
   - Pengujian gestur: `npm run test:gesture` (Node.js 22.6+). Pengaturan durasi ada di `src/controller/FacingGesture.ts`.
4. **Sistem Penguncian Tangan Stabil (Hand Identity Persistence)**:
   - Wayang tidak akan tertukar meskipun kedua tangan Anda bersilangan (*hand crossing*) atau berdekatan.
   - Dilengkapi masa toleransi (*grace period* 300 ms) sehingga jika tangan terhalang sekilas, wayang tidak langsung lenyap atau patah gerakannya.
5. **Performa Ringan, Adem & Hemat Baterai**:
   - **Batas Maksimal 30 FPS**: Aplikasi dibatasi pada 30 FPS untuk mencegah CPU/GPU perangkat bekerja terlalu keras dan mencegah perangkat cepat panas (*thermal throttling*).
   - **Pemisahan Jalur AI & Grafis**: Pembacaan AI (MediaPipe) berjalan santai pada rentang 15–20 FPS, sementara visualisasi wayang dihaluskan (*interpolated*) pada 30 FPS menggunakan mesin rendering PixiJS.
   - **Mode Hemat Otomatis**: Jika tab browser diminimalkan atau disembunyikan (*background tab*), pelacakan AI otomatis dijeda.
6. **Desain Antarmuka Eksklusif**:
   - Tampilan bernuansa kaca modern (*glassmorphism*) dengan sentuhan ornamen emas Bali.
   - Pengaman orientasi layar (*orientation guard*) yang ramah untuk smartphone dalam posisi *landscape*.
7. **AI Tutor dengan Dua API (Gemini + OpenAI)**:
   - Tanya jawab seputar wayang Bali melalui teks atau rekaman suara.
   - Gemini menjadi layanan utama; OpenAI otomatis mengambil alih saat kuota/rate limit Gemini tercapai (HTTP 429), termasuk transkripsi dan pembacaan jawaban.

---

## 👥 3. Katalog Karakter Wayang

Aplikasi ini menyediakan 4 karakter Wayang Bali yang siap dimainkan:

| ID Tokoh | Nama Karakter | Jumlah Lengan Artikulasi | Kontrol Lengan |
| :--- | :--- | :--- | :--- |
| **wayang01** | Wayang 01 | 2 Lengan (Kiri & Kanan) | Telunjuk (Lengan Kiri) & Jari Tengah (Lengan Kanan) |
| **wayang02** | Wayang 02 | 1 Lengan Tunggal | Telunjuk (Lengan Utama) |
| **wayang03** | Wayang 03 | 2 Lengan (Kiri & Kanan) | Telunjuk (Lengan Kiri) & Jari Tengah (Lengan Kanan) |
| **wayang04** | Wayang 04 | 2 Lengan (Kiri & Kanan) | Telunjuk (Lengan Kiri) & Jari Tengah (Lengan Kanan) |

Setiap aset potongan tubuh wayang (badan, tangkai wayang/cempurit, lengan atas, lengan bawah + telapak tangan) dipisahkan secara presisi dalam format gambar PNG berkualitas tinggi.

---

## 🎮 4. Alur Permainan (User Journey)

```
[ 1. HALAMAN UTAMA ]
         │
         ▼
[ 2. PEMILIHAN WAYANG ] ──▶ Tentukan tokoh untuk Tangan Kiri dan/atau Tangan Kanan
         │
         ▼
[ 3. IZIN KAMERA & KALIBRASI ] ──▶ Tunjukkan tangan selama 1,5 detik di depan kamera
         │
         ▼
[ 4. PANGGUNG INTERAKTIF ] ──▶ Mainkan wayang sesukamu (Durasi sesi: 3 Menit)
         │
         ▼
[ 5. SESI SELESAI ] ──▶ Opsi: Main Lagi / Ganti Wayang / Menu Utama
```

1. **Menu Utama (*Home*)**: Pengenalan panggung wayang dan tinjauan koleksi karakter.
2. **Pilih Wayang (*Character Selection*)**: Pengguna memilih tokoh yang ingin dimainkan dan menetapkannya ke tangan kiri (`L`) atau tangan kanan (`R`).
3. **Mulai Kamera & Kalibrasi (*Start Camera & Calibration*)**: Browser meminta izin webcam. Setelah aktif, pemain memperlihatkan tangan yang dipilih selama 1,5 detik untuk pengenalan identitas tangan awal.
4. **Panggung Bermain (*Playing*)**: Layar menampilkan wayang di atas panggung. Gerakkan telapak tangan ke kiri/kanan/atas/bawah, miringkan pergelangan tangan, serta tekuk atau lambaikan jari telunjuk dan jari tengah untuk memainkan tangkai lengan wayang.
5. **Sesi Selesai (*Session Complete*)**: Setelah waktu sesi 3 menit selesai (atau tidak ada tangan selama 25 detik), kamera otomatis dimatikan demi menghemat daya.

---

## 🏛️ 5. Arsitektur Teknis & Cara Kerja Sistem

Aplikasi dibangun dengan arsitektur modular yang bersih menggunakan prinsip **Pemisahan Tanggung Jawab (*Separation of Concerns*)**:

```
 ┌──────────────┐
 │  Kamera Web  │ (640x480 @ 24-30 FPS)
 └──────┬───────┘
        ▼
 ┌──────────────────────┐
 │   VideoFrameLoop     │ Hanya membaca jika ada frame kamera baru
 └──────┬───────────────┘
        ▼
 ┌──────────────────────┐
 │ HandLandmarkerManager│ MediaPipe Tasks Vision mendeteksi 21 titik sendi tangan
 └──────┬───────────────┘
        ▼
 ┌──────────────────────┐
 │   HandTrackManager   │ Menjaga identitas tangan (Kiri/Kanan) agar tidak tertukar
 └──────┬───────────────┘
        ▼
 ┌──────────────────────┐
 │ HandPuppetController │ Memetakan telapak tangan ke badan & ujung jari ke target lengan
 └──────┬───────────────┘
        ▼
 ┌──────────────────────┐
 │      TwoBoneIK       │ Menghitung sudut sendi bahu & siku secara anatomis
 └──────┬───────────────┘
        ▼
 ┌──────────────────────┐
 │      PuppetRig       │ Menggerakkan kontainer hierarki potongan tubuh wayang
 └──────┬───────────────┘
        ▼
 ┌──────────────────────┐
 │     PixiRenderer     │ Menggambar panggung visual di canvas WebGL (Maksimal 30 FPS)
 └──────────────────────┘
```

### Penjelasan Modul Kode:
- **`src/camera/CameraManager.ts`**: Mengatur siklus hidup kamera (permintaan izin browser, pengaturan resolusi ideal 640x480, penutupan *stream* ketika selesai).
- **`src/camera/VideoFrameLoop.ts`**: Mengoptimalkan pembacaan frame video menggunakan `requestVideoFrameCallback()` agar proses AI tidak membebani perangkat secara berlebihan.
- **`src/vision/HandLandmarkerManager.ts`**: Menginisialisasi model kecerdasan buatan Google MediaPipe (`hand_landmarker.task`) secara lokal melalui WebAssembly (`wasm`).
- **`src/tracking/HandTrackManager.ts`**: Algoritma pelacak identitas tangan. Menggunakan posisi, vektor kecepatan, sudut orientasi, dan probabilitas handedness untuk memastikan tangan kiri fisik selalu mengontrol slot wayang kiri dan tangan kanan fisik mengontrol slot wayang kanan.
- **`src/controller/HandPuppetController.ts`**: Mengolah data koordinat tangan menjadi perintah gerakan wayang, lengkap dengan filter penghalus (*Exponential Moving Average* / EMA) agar wayang tidak bergetar.
- **`src/puppet/TwoBoneIK.ts`**: Perhitungan matematis *Inverse Kinematics* dua tulang untuk melenturkan sendi bahu dan siku sesuai tarikan jari.
- **`src/puppet/PuppetRig.ts`**: Struktur hierarki visual 2D wayang berbasis PixiJS (badan, tongkat penggerak, lengan atas, dan lengan bawah).
- **`src/rendering/PixiRenderer.ts`**: Pengelola panggung grafis WebGL 2D dengan *ticker* khusus yang terkunci stabil di 30 FPS.
- **`src/app/GameApp.ts`**: Pengendali utama mesin permainan (*State Machine*), transisi antarmuka, penghitung waktu sesi 3 menit, dan pembersihan memori (*garbage collection*).

---

## 🛠️ 6. Teknologi yang Digunakan

- **Bahasa Pemrograman**: TypeScript (Strict Mode)
- **Bundler & Tooling**: Vite
- **Engine Computer Vision**: Google MediaPipe Tasks Vision (`@mediapipe/tasks-vision`)
- **Engine Grafis 2D**: PixiJS v8
- **Antarmuka & Styling**: Modern Semantic HTML5 & Vanilla CSS3 (Glassmorphism & Responsive Flex/Grid)

---

## 🚀 7. Cara Menjalankan Proyek

### Prasyarat
- **Node.js 22.6 atau lebih baru** (NPM ikut terpasang). Versi ini dibutuhkan oleh Vite 8 dan `npm run test:gesture`.
- **PHP 8.1+** dengan ekstensi `curl` dan `mbstring`. Hanya dibutuhkan untuk AI Tutor; di Windows bisa memakai PHP bawaan Laragon/XAMPP.
- Browser modern dengan WebGL dan WebAssembly (Chrome, Edge, Firefox, atau Safari terbaru).
- Webcam atau kamera laptop yang berfungsi.

Buka terminal di folder proyek, lalu pasang dependensi (cukup sekali):
```bash
npm install
```

### ⭐ Cara termudah — satu perintah (Vite + PHP)
```bash
npm run serve-all
```
Buka `http://localhost:5173`. Perintah ini menjalankan server Vite (dengan hot reload) **dan** server PHP di port `8124` sekaligus; `/tutor.php` dan `/queue.php` otomatis diteruskan ke PHP, jadi AI Tutor ikut berjalan tanpa perlu build. Isi `GEMINI_API_KEY` dan `OPENAI_API_KEY` di `.env` untuk mengaktifkan dua layanan tutor (lihat Opsi B langkah 1). Tekan `Ctrl+C` untuk menghentikan keduanya.
Port PHP bisa diganti: `PHP_PORT=9000 npm run serve-all` (PowerShell: `$env:PHP_PORT=9000; npm run serve-all`). Jika `php` tidak ada di PATH, set variabel `PHP` ke lokasi `php.exe`.

### Opsi A — Main wayang saja (paling cepat)
```bash
npm run dev
```
Buka `http://localhost:5173`, lalu izinkan kamera.
Skrip `predev` otomatis menyalin runtime WebAssembly MediaPipe ke `public/mediapipe/wasm/`.

> AI Tutor **tidak berjalan** di mode ini karena server Vite tidak mengeksekusi PHP. Gunakan `npm run serve-all` atau Opsi B untuk mencoba tutor.

### Opsi B — Uji hasil build produksi dengan AI Tutor
1. Salin konfigurasi, lalu isi `GEMINI_API_KEY` dan `OPENAI_API_KEY` untuk cadangan di file `.env` (cukup sekali):
   ```bash
   cp .env.example .env    # Windows PowerShell: Copy-Item .env.example .env
   ```
2. Build, lalu jalankan server PHP bawaan:
   ```bash
   npm run build
   php -S 127.0.0.1:8123 -t dist
   ```
3. Buka `http://127.0.0.1:8123`.

Catatan:
- Port boleh diganti (misalnya `8000`) selama tidak dipakai program lain.
- Perubahan di `src/` perlu `npm run build` ulang. Perubahan di `server/tutor.php` langsung berlaku tanpa build.
- Jika `GEMINI_API_KEY` kosong tetapi `OPENAI_API_KEY` terisi, tutor langsung memakai OpenAI. Jika kedua key kosong, tutor menampilkan pesan *"AI tutor belum aktif…"*; permainan tetap berjalan normal.

### Layar persiapan awal

Saat aplikasi menyiapkan aset dan mengunduh paket pada kunjungan awal, layar menampilkan **“Mohon tunggu, sedang menyiapkan aset dan aplikasi”**. Persentase dan bar progres tetap ditampilkan dari 0% hingga 100%, tanpa teks ukuran file, jumlah MB, maupun keterangan “Paket hanya diunduh sekali di perangkat ini”. Pengunjung diminta tidak menutup halaman selama proses berlangsung.

Progres mengikuti data yang diterima dan ditampilkan selama minimal 2 detik sebelum berpindah layar. Aset disimpan dalam cache perangkat agar kunjungan berikutnya lebih cepat; AI Tutor tetap memerlukan internet.

### Kamera & mikrofon
Browser hanya mengizinkan kamera dan mikrofon di `localhost`/`127.0.0.1` atau di alamat **HTTPS**. Untuk mencoba dari HP, buka aplikasi lewat URL HTTPS (hasil deploy atau tunnel HTTPS).

### Perintah lain
| Perintah | Fungsi |
|---|---|
| `npm run serve-all` | Vite dev + PHP sekaligus (game + AI Tutor) |
| `npm run typecheck` | Cek tipe TypeScript |
| `npm run test:gesture` | Tes gestur balik arah wayang |
| `npm run build` | Typecheck + build produksi ke `dist/` + manifest cache offline |
| `npm run preview` | Pratinjau hasil build tanpa PHP (AI Tutor tidak aktif) |
| `php -l server/tutor.php` | Cek sintaks backend tutor |

Sebelum commit, pastikan `npm run build`, `npm run test:gesture`, dan `php -l server/tutor.php` lulus.

### Deploy
Unggah folder `dist/`, `server/`, dan file `.env` dengan struktur direktori yang sama ke hosting Apache + PHP, dengan `dist/` sebagai document root. Detailnya ada di bagian **AI Tutor Wayang Bali** di bawah.

---

## 💡 8. Tips Bermain untuk Hasil Terbaik

1. **Pencahayaan yang Cukup**: Pastikan ruangan Anda memiliki pencahayaan yang merata agar kamera dapat mengenali sendi-sendi jari dengan jelas.
2. **Jarak Ideal**: Duduklah sekitar 50 cm hingga 1 meter di depan kamera, sehingga pergelangan tangan dan jari-jemari terlihat utuh di layar.
3. **Latar Belakang Bersih**: Hindari latar belakang yang terlalu ramai dengan warna yang menyerupai warna kulit tangan.
4. **Perangkat Smartphone**: Jika membuka melalui ponsel, selalu gunakan posisi **Horizontal / Landscape** agar panggung terlihat luas dan penuh.

---

## 📜 9. Lisensi & Hak Cipta

Proyek ini dikembangkan untuk tujuan edukasi, pelestarian budaya tradisional, dan eksplorasi teknologi kreatif berbasis web. Seluruh aset ilustrasi wayang merupakan karya seni digital yang dilindungi hak cipta masing-masing pemilik karya.

## AI Tutor Wayang Bali — Gemini + OpenAI (v0.2.0)

AI Tutor menggunakan **dua penyedia API: Google Gemini sebagai layanan utama dan OpenAI sebagai cadangan otomatis (fallback)**. Pertanyaan dikirim ke Gemini terlebih dahulu; saat Gemini mengembalikan HTTP 429 karena kuota/rate limit, backend melanjutkan pertanyaan tersebut ke OpenAI.

| Penyedia API | Peran | Pertanyaan dan jawaban suara | Konfigurasi key |
| --- | --- | --- | --- |
| Google Gemini | Utama | Menerima teks atau rekaman; jawaban dibacakan oleh sintesis suara perangkat | `GEMINI_API_KEY` |
| OpenAI | Fallback saat Gemini 429; langsung dipakai jika key Gemini kosong | Mentranskripsikan rekaman, menjawab pertanyaan, dan menghasilkan suara MP3 jika **Bacakan jawaban** aktif | `OPENAI_API_KEY` |

Isi kedua key pada `.env` server agar alur utama dan fallback tersedia:

```dotenv
GEMINI_API_KEY=isi_key_gemini_anda
OPENAI_API_KEY=isi_key_openai_anda
```

Kedua key hanya dibaca backend PHP dan tidak boleh dimasukkan ke bundle frontend atau diberi awalan `VITE_`.

Menu **AI Tutor** tersedia di beranda dan pemilihan wayang. Empat tokoh ditampilkan sebagai galeri. Pengunjung langsung mengetik pertanyaan atau menekan **Bicara** tanpa memilih tokoh. Tutor membahas semua tokoh, jenis, sejarah, perkembangan, dan tradisi wayang yang hidup di Bali, termasuk yang tidak ada dalam galeri. Izinkan mikrofon, bicara, lalu tekan **Selesai & kirim**; rekaman otomatis selesai setelah 15 detik. Rekaman dikirim melalui backend ke Gemini atau fallback OpenAI dan jawaban dibacakan jika opsi suara aktif. Menggunakan MediaRecorder melalui HTTPS, termasuk format MP4 untuk iPhone, tanpa bergantung pada SpeechRecognition. Dukungan suara Indonesia bergantung perangkat. Teks tetap tersedia jika izin mikrofon ditolak.

Backend PHP `public/tutor.php` (disalin ke `dist/` saat build) memuat `server/tutor.php`. Deploy **dist, server, dan .env** dengan struktur direktori ini tetap utuh. Apache harus mengeksekusi PHP dengan ekstensi curl dan mbstring. `.env` berada di root proyek, di luar document root `dist`; jangan gunakan awalan `VITE_` untuk rahasia.

Salin `.env.example` menjadi `.env`, isi `GEMINI_API_KEY` dan `OPENAI_API_KEY` untuk cadangan, dan beri akses baca hanya kepada pemilik serta grup PHP/Apache. Model default `gemini-3.5-flash-lite`; keluaran model berupa teks, jadi masukan suara direkam browser dan diproses Gemini, lalu jawaban dibacakan sintesis suara perangkat, bukan Gemini Live. Rekaman tidak disimpan oleh aplikasi; rekaman dikirim ke backend/Gemini atau OpenAI; kamera permainan tetap diproses lokal.

Batas hemat biaya: pertanyaan teks 300 karakter atau rekaman maksimal 15 detik di browser (payload audio maksimal 256 KiB di server), satu pertanyaan tanpa riwayat, target jawaban dua kalimat/55 kata, maksimum 180 token keluaran (dapat diatur melalui `.env`, batas keras 240). Backend membatasi total 12 permintaan/menit dan default 300/hari UTC untuk seluruh situs. Satu pertanyaan dihitung sekali, termasuk jika memakai fallback; batas situs tidak memicu fallback. Instruksi server menolak topik di luar wayang Bali serta perubahan peran; pembatasan model bukan jaminan absolut. Jangan menyediakan alat atau akses data sensitif ke tutor.

Verifikasi: `npm run build`, `php -l server/tutor.php`, dan POST JSON ke `/tutor.php` dengan `message` tanpa pilihan `character`, atau `audio: {data: "base64", mimeType: "audio/mp4"}` menggantikan `message`. Format audio: MP4, WebM, OGG; header kontainer dan ukuran divalidasi server. Batas durasi diberlakukan oleh browser, batas ukuran dan jumlah permintaan oleh server. Endpoint dan konfigurasi tidak masuk cache offline. AI memerlukan koneksi internet.


Fallback OpenAI otomatis berjalan saat Gemini merespons HTTP 429 (kuota/rate limit), atau langsung jika key Gemini kosong. Error lain dan penolakan konten tidak memicu fallback. Isi key asli pada `OPENAI_API_KEY` di `.env`; jangan memakai awalan `VITE_`. Default: `OPENAI_MODEL=gpt-4.1-mini`, `OPENAI_TRANSCRIBE_MODEL=gpt-transcribe`, `OPENAI_TTS_MODEL=gpt-4o-mini-tts`, `OPENAI_TTS_VOICE=coral`, `OPENAI_MAX_OUTPUT_TOKENS=180` (maks. 240). Semua dapat disetel sesuai akses model akun. Transkripsi dikirim dari memori (PHP >= 8.1 dengan curl dan mbstring); rekaman tidak ditulis ke disk.

Pada fallback, OpenAI menjawab teks dan rekaman suara. Jika **Bacakan jawaban** aktif (`speak: true` pada request), backend juga menghasilkan MP3; jika TTS gagal, teks tetap tampil dan perangkat mencoba membacakannya. Dengarkan ulang menggunakan audio yang sama tanpa request tambahan. Suara berhenti saat merekam, menekan Hentikan suara, berpindah tab, atau keluar tutor. Timeout frontend 85 detik mencakup Gemini dan rangkaian fallback. Deploy seluruh direktori `server/`, termasuk `openai.php`.
