# Tutor fallback implementation plan

**Goal:** Hapus wayang05 dan sediakan fallback OpenAI untuk teks dan suara saat kuota Gemini habis.
**Architecture:** Gemini utama, OpenAI pada HTTP 429 atau key Gemini kosong. Backend menjaga rahasia, validasi, dan budget lokal; frontend memutar MP3 dan membersihkan playback.
**Tech Stack:** PHP cURL, TypeScript, CSS.
**Spec:** agent/PRD.md F1, F11, §7.5.

- [x] Hapus definisi/aset wayang05, sesuaikan katalog dan layout empat tokoh.
- [x] Tambah helper OpenAI untuk transkripsi di memori, Responses, dan TTS; integrasikan fallback tanpa melewati batas lokal.
- [x] Tambah env server dan dokumentasi; integrasikan audio, replay, stop, visibility, dan timeout frontend.
- [x] Jalankan PHP lint, satu build (termasuk typecheck), dan uji fallback terarah tanpa API berbayar. Tidak menjalankan test gestur karena tidak diubah.

Review: Gemini sukses tidak memanggil OpenAI; 429 beralih sekali; key tidak ada/error OpenAI menghasilkan pesan aman; TTS gagal tetap memberi teks; audio tidak lanjut setelah stop/dispose.

Validasi: PHP lint lulus; delapan simulasi routing/teks/audio/error/budget lulus dengan cURL stub, tanpa API eksternal. Pemeriksaan kamera/gerak dan audio pada perangkat fisik tidak dilakukan.
