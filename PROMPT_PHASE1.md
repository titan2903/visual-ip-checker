Saya punya PRD lengkap di file [PRD](PRD.md) untuk project bernama "Tarum" — 
alat cek kemiripan visual desain kriya/fashion pakai image embedding search.

Tolong baca dulu seluruh PRD ini sebelum mulai coding. Kerjakan HANYA fase berikut, 
jangan bangun fitur di luar scope ini dulu:

FASE 1 — Backend core:
1. Setup project structure: FastAPI backend + folder terpisah untuk frontend (React+Vite)
2. Implementasikan pipeline embedding sesuai section 7 (CLIP ViT-B/32 via sentence-transformers 
   + FAISS index) — pakai kode contoh di PRD sebagai starting point, bukan reimplementasi dari nol
3. Buat endpoint POST /check yang menerima upload gambar, return top-5 similarity results 
   dengan skor 0-100%
4. Buat script untuk build index awal dari folder dataset referensi (boleh dummy images dulu 
   untuk testing, saya akan isi dataset asli belakangan)
5. Tulis README singkat cara run project ini secara lokal

JANGAN kerjakan frontend/UI dulu di fase ini. JANGAN tambah fitur di luar Must Have 
(section 6) tanpa tanya saya dulu.

Setelah selesai, kasih ringkasan apa yang sudah dibuat dan asumsi teknis apa yang kamu ambil.