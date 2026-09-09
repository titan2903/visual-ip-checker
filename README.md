# Tarum — Visual IP Screening untuk Pelaku Kriya & Fashion

**Owner:** TITANIO YUDISTA  
**Status:** Draft MVP (Submission EKRAF x Google Career Certificates)

Tarum adalah instrumen screening awal kemiripan visual desain berbasis *deep learning* untuk pelaku UMKM kriya dan fashion (fokus MVP: **Batik Indonesia**), divalidasi bersama mitra studi kasus **Datik Batik** (Tangerang Selatan). Sistem mendeteksi potensi kemiripan motif secara visual menggunakan model pretrained **CLIP ViT-B/32** dan pencarian vektor berkecepatan tinggi **FAISS** sebelum produk didaftarkan ke HKI (PDKI) atau diproduksi massal.

---

## 🎯 Studi Kasus Validasi: UMKM Datik Batik (Tangerang Selatan)

Proyek ini divalidasi menggunakan studi kasus nyata dari mitra perajin kriya lokal:
- **Profil Usaha**: **Datik Batik** (beroperasi aktif sejak 2012 di Tangerang Selatan, Banten).
- **Fokus Produk**: Kain batik tulis kontemporer, batik cap flora lokal khas Tangsel (anggrek van douglas & pesisiran), kemeja, outer, dan syal kriya.
- **Tantangan Nyata**: Perajin rentan tersandung sengketa kemiripan motif karena sistem resmi PDKI DJKI hanya melayani pencarian teks kata kunci, sedangkan jasa konsultan HKI independen bertarif mahal (Rp 2 – 5 juta per desain).
- **Dampak Penggunaan Tarum**:
  - **Kecepatan**: Waktu skrining kemiripan visual selesai dalam **< 5 detik**.
  - **Efisiensi Finansial**: Biaya validasi awal ditekan dari jutaan rupiah menjadi **Rp 0 (100% mandiri)**.
  - **Nir-Sengketa (*Zero Dispute*)**: Mencegah pemborosan modal bahan baku (*sunk cost*) sebelum kain dicap/dicanting secara massal.
- **Dokumentasi Produk**: Spesifikasi teknis, persona, dan arah desain lengkap dapat dilihat di [**`PRD.md`**](PRD.md).

---

## 🌟 Fitur Utama

- **Pencarian Kemiripan Visual**: Mengekstraksi fitur semantik motif (bukan teks kata kunci) menggunakan model Vision Transformer (CLIP).
- **Hasil & Penilaian Objektif**: Menampilkan skor kemiripan 0.0% – 100.0% dan 5 karya pembanding paling mirip ber-thumbnail.
- **Kategorisasi Risiko Tiga Tingkat**:
  - `Cukup Orisinal` (< 50%): Disarankan lanjut ke pendaftaran HKI.
  - `Perlu Ditinjau` (50% – 74.99%): Disarankan modifikasi elemen tertentu.
  - `Sangat Mirip` (≥ 75%): Risiko tinggi penolakan/somasi, disarankan revisi menyeluruh.
- **UI/UX Presisi Instrumen**: Mengikuti *Token System* PRD Section 8.1 (Palet Paper, Ink, Indigo Tarum, Line Grey, Signal Amber) dengan layout asimetris 40/60.
- **100% Berjalan Lokal & Hemat Biaya**: Tidak membutuhkan API key pihak ketiga berbayar dan dapat berjalan cepat di CPU laptop/server standar.
- **CI/CD Otomatis Terpisah**: Workflow GitHub Actions terpisah untuk deployment backend (Heroku) dan frontend (Vercel).

---

## 📁 Struktur Direktori Proyek

```text
visual-ip-checker/
├── .github/
│   └── workflows/
│       ├── backend-deploy.yml         # CI/CD Backend ke Heroku
│       └── frontend-deploy.yml        # CI/CD Frontend ke Vercel
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py              # Endpoint API (POST /check, GET /health)
│   │   ├── services/
│   │   │   ├── embedding_service.py   # Ekstraksi fitur CLIP (sentence-transformers)
│   │   │   └── search_service.py      # Pencarian vektor FAISS & kalkulasi skor
│   │   ├── schemas/
│   │   │   └── check.py               # Schema Pydantic request & response
│   │   ├── config.py                  # Konfigurasi aplikasi & load .env
│   │   └── main.py                    # Entrypoint FastAPI & static file mounting
│   ├── data/
│   │   ├── reference_images/          # Dataset gambar referensi produk/motif
│   │   └── index/                     # File biner index.faiss & metadata.json
│   ├── scripts/
│   │   ├── create_dummy_data.py       # Generator 12 motif kriya dummy
│   │   └── build_index.py             # Script pembangun indeks FAISS
│   ├── tests/
│   │   └── test_api.py                # Test suite pytest (7 skenario)
│   ├── .env                           # Konfigurasi environment backend lokal
│   ├── .env.example                   # Template konfigurasi backend
│   ├── .gitignore                     # Git ignore khusus backend
│   ├── Procfile                       # Heroku process file untuk subfolder backend
│   ├── runtime.txt                    # Versi Python Heroku
│   └── requirements.txt               # Dependensi Python
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Komponen utama React & alur pemeriksaan
│   │   ├── App.css                    # Styling layout asimetris 40/60
│   │   ├── index.css                  # Token warna, tipografi, & tekstur tenun
│   │   └── main.jsx                   # Entrypoint React
│   ├── .env                           # Konfigurasi environment frontend lokal
│   ├── .env.example                   # Template konfigurasi frontend
│   ├── .gitignore                     # Git ignore khusus frontend
│   ├── vercel.json                    # Konfigurasi SPA routing & build Vercel
│   ├── vite.config.js                 # Konfigurasi proxy API Vite
│   └── package.json                   # Dependensi React & Vite
├── Procfile                           # Heroku process file di root
├── runtime.txt                        # Versi Python (3.12.8) untuk Heroku
├── .gitignore                         # Git ignore root
├── ARCHITECTURE.md                    # Dokumen Arsitektur Sistem
├── PRD.md                             # [PRD.md](PRD.md) - Dokumen Product Requirement Document
├── PROMPT_PHASE1.md                   # Spesifikasi teknis Fase 1 (Backend Core)
├── PROMPT_PHASE2.md                   # Spesifikasi teknis Fase 2 (Frontend UI)
└── README.md                          # Dokumentasi utama proyek ini
```

---

## 🚀 Panduan Menjalankan Secara Lokal

### 1. Prasyarat Sistem
- **Python**: versi 3.10 ke atas (diuji pada Python 3.12)
- **Node.js**: versi 18 ke atas (diuji pada Node.js 20/22)
- Package manager Python: `uv` (sangat direkomendasikan) atau `pip` bawaan

---

### 2. Menjalankan Backend (FastAPI)

1. **Buat dan aktifkan Virtual Environment**:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependensi Backend**:
   ```bash
   uv pip install -r backend/requirements.txt
   # atau: pip install -r backend/requirements.txt
   ```

3. **Persiapan Dataset & Bangun Indeks FAISS**:
   ```bash
   # Rekomendasi MVP: Mengindeks dataset Hugging Face Batik-Indonesia (2.599 gambar, 38 kelas motif)
   python backend/scripts/build_index.py --source hf

   # Opsi Fallback: Buat 12 motif sintetis & indeks lokal
   python backend/scripts/create_dummy_data.py
   python backend/scripts/build_index.py --source local
   ```
   *(Script otomatis mengunduh, mengekstrak embedding CLIP, menyimpan thumbnail ke `backend/data/reference_images/`, dan membangun `index.faiss`)*.

4. **Jalankan Server FastAPI**:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

### 3. Menjalankan Frontend (React + Vite)

Buka terminal baru:

1. **Masuk ke folder frontend & install dependensi**:
   ```bash
   cd frontend
   npm install
   ```

2. **Jalankan Vite Dev Server**:
   ```bash
   npm run dev
   ```
   - Buka di browser: **[http://localhost:5173](http://localhost:5173)**
   - Frontend sudah terhubung secara otomatis ke backend port `8000` via proxy Vite (`/api`).

---

## ⚙️ Konfigurasi Environment (`.env`)

### Backend (`backend/.env`)
| Variabel | Default | Keterangan |
|---|---|---|
| `TARUM_MODEL_NAME` | `clip-ViT-B-32` | Model CLIP via sentence-transformers |
| `TARUM_HF_DATASET` | `muhammadsalmanalfaridzi/Batik-Indonesia` | Dataset Hugging Face referensi batik (PRD Section 7.1) |
| `TARUM_HOST` | `0.0.0.0` | Host binding server FastAPI |
| `TARUM_PORT` | `8000` | Port listening server |
| `TARUM_CORS_ORIGINS` | `http://localhost:5173,...` | Daftar origin yang diizinkan CORS |
| `TARUM_MAX_UPLOAD_SIZE_MB` | `5.0` | Batas maksimum ukuran file unggahan (MB) |
| `TARUM_DEFAULT_TOP_K` | `5` | Jumlah karya pembanding yang diambil |
| `TARUM_RISK_THRESHOLD_LOW` | `50.0` | Ambang batas kategori *Cukup Orisinal* |
| `TARUM_RISK_THRESHOLD_HIGH` | `75.0` | Ambang batas kategori *Sangat Mirip* |

### Frontend (`frontend/.env`)
| Variabel | Default | Keterangan |
|---|---|---|
| `VITE_API_BASE_URL` | *kosong* | Kosong untuk proxy internal Vite; isi URL backend jika terpisah |
| `VITE_APP_TITLE` | `Tarum — Visual IP Screening` | Judul aplikasi pada UI |
| `VITE_MAX_UPLOAD_SIZE_MB` | `5` | Batasan validasi ukuran file di sisi browser |
| `VITE_PDKI_URL` | `https://pdki-indonesia.dgip.go.id` | Tautan portal resmi HKI DJKI |

---

## 🧪 Pengujian & Quality Assurance

### Menjalankan Test Suite Backend:
```bash
# Dari root direktori proyek
PYTHONPATH=. pytest -p no:launch_testing backend/tests/ -v
```
*Menguji 7 skenario: endpoint root, health check, static file thumbnail, kalkulasi kemiripan valid, validasi ekstensi tidak sah, validasi file rusak, dan penolakan file > 5MB.*

### Menguji Build Frontend:
```bash
cd frontend
npm run build
```

---

## 🚢 CI/CD & Deployment Otomatis

Proyek ini telah dilengkapi dengan GitHub Actions yang otomatis berjalan ketika ada perubahan di-push ke branch utama (`main` / `master`):

1. **Backend Deploy to Heroku** ([`.github/workflows/backend-deploy.yml`](.github/workflows/backend-deploy.yml)):
   - Menjalankan test suite `pytest` terlebih dahulu.
   - Jika tes lulus, deploy ke Heroku menggunakan `Procfile` dan `runtime.txt`.
   - *GitHub Secrets*: `HEROKU_API_KEY`, `HEROKU_APP_NAME`, `HEROKU_EMAIL`.

2. **Frontend Deploy to Vercel** ([`.github/workflows/frontend-deploy.yml`](.github/workflows/frontend-deploy.yml)):
   - Menjalankan pengujian build bundle Vite.
   - Melakukan rilis produksi ke Vercel via CLI resmi.
   - *GitHub Secrets*: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.

---

## 📌 Asumsi Teknis & Dasar Validasi

1. **Model Machine Learning**: Menggunakan model **CLIP ViT-B/32** (Contrastive Language-Image Pre-training) yang mengekstraksi 512 dimensi vektor visual laten ternormalisasi ($L_2\text{-norm} = 1$).
2. **Kalkulasi Kemiripan**: Menggunakan **Cosine Similarity** via **FAISS IndexFlatIP**:
   $$\text{Skor Kemiripan (\%)} = \text{clamp}((\mathbf{u} \cdot \mathbf{v}) \times 100.0, 0.0, 100.0)$$
3. **Pernyataan Hukum (Legal Disclaimer)**:
   > *"Ini bukan opini hukum. Hasil ini membantu kamu memutuskan langkah berikutnya, bukan menggantikan konsultasi HKI resmi."*
   Alat ini adalah instrumen screening awal mandiri untuk memberikan bukti pembanding visual bagi pengrajin UMKM kriya sebelum mengajukan Desain Industri atau Hak Cipta ke DJKI.

---

## 📚 Dokumen Spesifikasi & Terkait

- 📄 [**PRD.md**](PRD.md) — Product Requirement Document (spesifikasi fungsional, persona Datik Batik, & token desain UI/UX).
- 🏗️ [**ARCHITECTURE.md**](ARCHITECTURE.md) — Dokumen arsitektur teknis sistem dan integrasi service.
