# AGENTS.md — Wayang Bali Interactive

Instruksi wajib untuk **semua** AI coding agent (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, Antigravity, dll.).

## 1. Wajib dibaca sebelum bekerja

1. **`agent/PRD.md`** — Product Requirements Document, *source of truth* produk, arsitektur, dan batas performa. Baca seluruhnya di awal setiap sesi, sebelum merencanakan atau mengedit kode.
2. **Skill project** di `.agents/skills/<nama>/SKILL.md` (salinan untuk Claude Code di `.claude/skills/`). Sebelum mengerjakan tugas, buka dan ikuti `SKILL.md` dari setiap skill yang cocok di tabel §2. Jika agent kamu tidak memuat skill otomatis, baca file-nya secara manual.

Jika instruksi pengguna bertentangan dengan `agent/PRD.md`, ikuti pengguna lalu usulkan pembaruan PRD.

## 2. Peta skill

| Saat mengerjakan… | Baca skill |
|---|---|
| Fitur baru, perubahan perilaku, permintaan klien | `brainstorming`, lalu `writing-plans` |
| PixiJS: rendering, rig, ticker, performa | `pixijs` (router), `pixijs-core-concepts`, `pixijs-application`, `pixijs-performance`, `pixijs-scene-graphics` |
| Konfigurasi build / Vite | `vite` |
| Kode TypeScript apa pun | `typescript-best-practices` |
| Backend `server/*.php`, `public/*.php` | `php-pro` |
| Integrasi Gemini / AI Tutor | `gemini-api-dev` |
| UI, tampilan, aksesibilitas, review desain | `web-design-guidelines` |
| Audit performa / a11y / best practice web | `web-quality-audit` |
| SEO teknis (meta, structured data, sitemap) | `seo` |
| AEO / tampil & dikutip di AI search | `ai-seo` |
| Menulis pesan commit | `conventional-commit` |

Daftar skill dan sumbernya terkunci di `skills-lock.json`. Pulihkan dengan `npx skills experimental_install` atau pasang ulang dari sumber di file itu.

## 3. Perintah

```bash
npm install
npm run serve-all      # Vite dev + PHP (port 8124, di-proxy) — game + AI Tutor
npm run dev            # Vite saja (AI Tutor tidak jalan: PHP tidak dieksekusi)
npm run typecheck
npm run test:gesture   # Node >= 22.6
npm run build          # typecheck + build + cache manifest
php -S localhost:8000 -t dist   # setelah build; dengan AI Tutor (butuh .env)
php -l server/tutor.php
```

## 4. Aturan inti (detail di `agent/PRD.md` §10)

- Render maks. 30 FPS, tanpa mode 60 FPS. MediaPipe normal ±20 FPS, maks. 30, tidak terus-menerus 30.
- Jangan hapus identitas tangan persisten; wayang tidak boleh tertukar.
- Jangan sederhanakan rig wayang menjadi satu gambar rigid.
- Jangan pernah mengirim frame webcam ke backend.
- `GEMINI_API_KEY` hanya di `.env` server; jangan pernah memberi awalan `VITE_`.
- Jaga batas modul: camera / vision / tracking / controller / puppet / rendering / app / tutor.
- Nilai khusus tokoh hanya di `src/puppet/characters/`, tidak di controller atau rig.
- Periksa kode yang ada sebelum mengedit; ubah seminimal mungkin dan jangan menulis ulang yang sudah bekerja.
- Setelah perubahan: penuhi Definition of Done di PRD §11.
- Commit memakai Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `chore:`).
- Perbarui `agent/PRD.md` lebih dulu bila mengubah fitur, arsitektur, atau target performa.
