# Knowledge Base: Tarum — Visual IP Screening untuk Pelaku Kriya & Fashion

**Repository:** `visual-ip-checker`  
**Owner:** TITANIO YUDISTA  
**Versi Sistem:** 0.2 (MVP Validated)  
**Slide Presentasi (Canva):** [canva.link/tarum](https://canva.link/tarum)  
**Tujuan Dokumen:** Referensi tunggal komprehensif (Single Source of Truth) mengenai arsitektur, algoritma, basis data, standar UI/UX, kontrak API, dan pedoman operasional aplikasi **Tarum**.

---

## 📑 Daftar Isi
1. [Ringkasan Proyek & Konteks Bisnis](#1-ringkasan-proyek--konteks-bisnis)
2. [Studi Kasus Pilot: UMKM Datik Batik](#2-studi-kasus-pilot-umkm-datik-batik)
3. [Arsitektur Teknis Sistem](#3-arsitektur-teknis-sistem)
4. [Machine Learning & Algoritma Kemiripan](#4-machine-learning--algoritma-kemiripan)
5. [Data Pipeline & Manajemen Indeks](#5-data-pipeline--manajemen-indeks)
6. [Design System & Standar UI/UX](#6-design-system--standar-uiux)
7. [Spesifikasi API & Kontrak Data](#7-spesifikasi-api--kontrak-data)
8. [Konfigurasi Environment](#8-konfigurasi-environment)
9. [Panduan Operasional & Deployment](#9-panduan-operasional--deployment)
10. [Troubleshooting & Gotchas](#10-troubleshooting--gotchas)
11. [Legal Disclaimer & Batasan Sistem](#11-legal-disclaimer--batasan-sistem)

---

## 1. Ringkasan Proyek & Konteks Bisnis

### 1.1 Latar Belakang
Pelaku usaha mikro, kecil, dan menengah (UMKM) kriya dan fashion di Indonesia secara rutin menciptakan desain motif kain (batik, tenun, anyaman). Namun, perajin menghadapi masalah kritis: **ketiadaan alat verifikasi visual untuk memeriksa orisinalitas rancangan mereka**.
- Sistem resmi pemerintah, yaitu **Pangkalan Data Kekayaan Intelektual (PDKI) DJKI**, hanya mendukung pencarian berbasis **kata kunci teks** (nama karya atau pendaftar). Sistem ini tidak dapat mendeteksi kesamaan visual (geometri, pola garis, atau ornamen isen-isen) jika motif serupa dinamai berbeda.
- Konsultasi penelusuran HKI melalui kantor hukum komersial memakan biaya berkisar **Rp 2.000.000 – Rp 5.000.000 per desain**, melampaui kemampuan anggaran operasional usaha mikro.
- Akibatnya, perajin rentan tersandung sengketa pelanggaran hak cipta tidak disengaja (*unintentional infringement*), somasi pihak ketiga, penolakan permohonan pendaftaran HKI, atau pemborosan modal produksi (*sunk cost*) saat produk sudah terlanjur dicetak ratusan meter.

### 1.2 Solusi Tarum
**Tarum** adalah instrumen screening awal kemiripan visual (*visual IP pre-screening*) berbasis deep learning (Vision Transformer) yang dirancang untuk:
1. Memeriksa kemiripan gambar motif terhadap ribuan data referensi warisan budaya nusantara secara instan (**< 5 detik**).
2. Memberikan skor persentase objektif (0.0% – 100.0%) serta komparasi visual berdampingan (*side-by-side*) dengan top-5 karya paling serupa.
3. Memberikan rekomendasi tindak lanjut yang terarah dan bertanggung jawab sebelum perajin mengeluarkan modal produksi massal atau mendaftar ke DJKI.

---

## 2. Studi Kasus Pilot: UMKM Datik Batik

Proyek ini divalidasi langsung bersama mitra perajin kriya tekstil:
* **Nama Usaha:** Datik Batik
* **Tahun Berdiri:** 2012 (~14 tahun beroperasi)
* **Lokasi:** Tangerang Selatan, Banten
* **Kategori Usaha:** Kriya Tekstil & Fashion Etnik Nusantara (Batik Tulis Kontemporer, Batik Cap, dan Busana Siap Pakai)
* **Kapasitas Produksi:** 60 – 100 potong lembar kain dan pakaian jadi per bulan
* **Ciri Khas Produk:** Eksplorasi motif flora lokal khas Tangerang Selatan (seperti bunga anggrek van douglas dan ragam pesisiran modern)
* **Tantangan Nyata Datik Batik:**
  - Cemas motif baru yang dirancang perajin menyerupai motif batik lain yang sudah terdaftar.
  - Terbatasnya akses penelusuran citra visual di sistem PDKI resmi Kemenkumham.
  - Mahalnya biaya jasa konsultan hukum HKI swasta.
* **Dampak Penerapan Tarum:**
  - Mengeliminasi biaya uji kemiripan awal dari jutaan rupiah menjadi **Rp 0 (100% mandiri)**.
  - Memberi kepastian hukum dan rasa percaya diri bagi perajin sebelum memproduksi canting cap tembaga atau kain mori bernilai jutaan rupiah.
  - Alur pakai praktis dalam 3 langkah (*Upload* → *Cek* → *Baca Rekomendasi*) tanpa membutuhkan keahlian hukum teknis.

---

## 3. Arsitektur Teknis Sistem

### 3.1 Alur Data End-to-End
```text
┌─────────────────────────────────────────────────────────────┐
│                    Browser Klien / Frontend                │
│        React 19 + Vite (Port 5173 / Firebase Hosting)       │
│  - Input Gambar (JPG/PNG max 5MB)                          │
│  - Polling Status Server (/api/health)                     │
│  - Rendering Hasil: Skor Count-Up, Top-5 Match, Rekomendasi│
└──────────────────────────────┬──────────────────────────────┘
                               │
                HTTP POST /api/check (Multipart)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend (Port 8000)              │
│  - Validasi File: Format, Dimensi, Resolusi, Ukuran         │
│  - PIL Image Preprocessing                                  │
└──────────────┬───────────────────────────────▲──────────────┘
               │                               │
        PIL.Image Object                Vektor 512-dimensi
               │                               │
┌──────────────▼───────────────────────────────┴──────────────┐
│       Embedding Service (ONNX Runtime INT8 / C++ Engine)    │
│        Model Pretrained: CLIP ViT-B/32 (clip_vision_int8)   │
│  - Pra-pemrosesan Murni NumPy/Pillow (224x224, Bicubic)     │
│  - Inferensi C++ ONNX Runtime (Tanpa PyTorch, RAM ~170MB)   │
│  - Ekstraksi Feature Map Visual Laten 512-dimensi           │
│  - Normalisasi L2-Norm (||v|| = 1.0)                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                   Normalized Query Vector
                               │
┌──────────────────────────────▼──────────────────────────────┐
│            Search Service & FAISS Vector Index              │
│  - Index: faiss.IndexFlatIP (Inner Product = Cosine Sim)    │
│  - Metadata Lookup: metadata.json (200 motif Batik)         │
│  - Filter Kategori / Motif Opsional                         │
│  - Transformasi Jarak -> Persentase Kemiripan (0 - 100%)    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Teknologi & Library
| Lapisan | Komponen / Library | Versi | Peran |
|---|---|---|---|
| **Backend Framework** | FastAPI | `^0.115.0` | High-performance async REST API, validasi request via Pydantic v2 |
| **ASGI Server** | Uvicorn | `^0.32.0` | Web server ASGI production-grade |
| **Inference Engine** | ONNX Runtime | `^1.18.0` | Runtime inferensi C++ statis (INT8 Quantized, RAM ~170MB) |
| **Model Pretrained** | CLIP ViT-B/32 | INT8 ONNX | Model visi OpenAI CLIP terkuantisasi offline (85 MB) |
| **Vector Database** | `faiss-cpu` | `^1.9.0` | Pencarian tetangga terdekat berkecepatan tinggi (IndexFlatIP) |
| **Dataset Source** | Hugging Face `datasets` | `^2.20.0` | Loader dataset resmi 200 motif Batik Indonesia (dikomit di Git) |
| **Image Processing** | Pillow (PIL) | `^11.0.0` | Validasi format, decoding, dan normalisasi dimensi gambar |
| **Frontend Core** | React | `^19.2.8` | Komponen antarmuka deklaratif |
| **Frontend Bundler** | Vite | `^8.2.2` | Development server cepat & bundler build produksi |
| **Styling** | Vanilla CSS | W3C Standard | Tokenized CSS, zero framework overhead (No Tailwind) |
| **Testing** | Pytest | `^8.3.0` | Test suite backend (9 skenario lulus termasuk verifikasi akurasi) |

---

## 4. Machine Learning & Algoritma Kemiripan

### 4.1 Pemilihan Model: CLIP ViT-B/32 (ONNX Runtime INT8)

Model yang digunakan adalah **OpenAI CLIP (Contrastive Language-Image Pre-training)** varian **ViT-B/32** yang telah dikuantisasi secara statis ke format **ONNX INT8**:
- **Alasan Visual**: Mampu merepresentasikan tekstur, bentuk (parang, kawung, mega mendung), dan perulangan pola kriya ke dalam dimensi vektor matematika dengan presisi tinggi (mencapai skor kemiripan >97% pada motif serupa).
- **Kinerja dan Optimasi Memori**: Berbeda dari PyTorch penuh yang mengonsumsi RAM >1.4GB atau API eksternal yang tidak memiliki image pipeline khusus, model **ONNX INT8** (`clip_vision_int8.onnx`, ukuran 85MB) dieksekusi secara lokal oleh runtime C++ `onnxruntime`. Konsumsi RAM total hanya **~170 MB**, sangat aman untuk kuota Heroku Basic (512 MB).
- **Dimensi**: Menghasilkan 512-dimensi feature vector yang dinormalisasi L2 dan langsung dicari di FAISS `IndexFlatIP`.

### 4.2 Formulasi Matematika Pencocokan Vektor
Setiap vektor representasi gambar kueri ($\mathbf{u}$) dan gambar referensi ($\mathbf{v}$) dinormalisasi dengan $L_2\text{-norm}$:
$$\hat{\mathbf{u}} = \frac{\mathbf{u}}{\|\mathbf{u}\|_2}, \quad \hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2}$$

Dengan normalisasi tersebut, nilai *Inner Product* pada indeks FAISS (`IndexFlatIP`) setara dengan **Cosine Similarity**:
$$\text{sim}(\hat{\mathbf{u}}, \hat{\mathbf{v}}) = \hat{\mathbf{u}} \cdot \hat{\mathbf{v}} = \cos(\theta) \in [-1.0, 1.0]$$

Nilai kemiripan dikonversi menjadi persentase skala $0.0\% - 100.0\%$:
$$\text{Skor Kemiripan (\%)} = \text{clamp}\Big((\hat{\mathbf{u}} \cdot \hat{\mathbf{v}}) \times 100.0, \; 0.0, \; 100.0\Big)$$

### 4.3 Kategorisasi Risiko Tiga Tingkat
Sistem mengelompokkan hasil ke dalam 3 tier risiko sesuai PRD Section 6 & 8:
1. **Risiko Rendah / Cukup Orisinal ($< 50.0\%$)**:
   - *Aksen Warna:* `Indigo Tarum` (`#2B3A67`).
   - *Arti:* Desain memiliki diferensiasi visual yang tinggi terhadap database referensi.
   - *Rekomendasi:* Aman untuk diproduksi dan diajukan ke DJKI sebagai Desain Industri / Hak Cipta.
2. **Risiko Sedang / Perlu Ditinjau ($50.0\% - 74.99\%$)**:
   - *Aksen Warna:* `Signal Amber` (`#B8843A`).
   - *Arti:* Terdapat kemiripan pada elemen ornamen tertentu atau gaya tata letak.
   - *Rekomendasi:* Tinjau ulang bagian pola yang mirip, lakukan diferensiasi ornamen sebelum memproduksi dalam jumlah besar.
3. **Risiko Tinggi / Sangat Mirip ($\ge 75.0\%$)**:
   - *Aksen Warna:* `Ink Solid` (`#1A1A18`) dengan border tebal.
   - *Arti:* Kemiripan visual sangat kuat dengan motif yang sudah ada di database.
   - *Rekomendasi:* Risiko tinggi somasi atau penolakan HKI; perombakan desain secara menyeluruh disarankan.

---

## 5. Data Pipeline & Manajemen Indeks

### 5.1 Sumber Data Referensi (Dataset Batik Indonesia)
Dataset utama berasal dari Hugging Face:
- **Repository:** `muhammadsalmanalfaridzi/Batik-Indonesia`
- **Volume:** 2.599 gambar motif batik asli nusantara
- **Distribusi Kelas:** 38 kelas motif batik (Kawung, Parang, Megamendung, Buketan, Ceplok, Tambal, dll.)
- **Status Lisensi:** Riset non-komersial / Proof-of-Concept (PRD Section 7.1)

### 5.2 Skrip Pembangunan Indeks (`backend/scripts/build_index.py`)
Skrip ini mengotomatiskan pembangunan basis data vektor:
```bash
# Mode Produksi / Dataset Lengkap Hugging Face:
python backend/scripts/build_index.py --source hf

# Opsi Membatasi Jumlah Sampel (misal 200 sampel untuk testing cepat):
python backend/scripts/build_index.py --source hf --limit 200

# Mode Offline / Data Dummy Lokal:
python backend/scripts/build_index.py --source local
```

**Proses yang Dijalankan oleh Skrip:**
1. Membaca dataset gambar via Hugging Face API atau folder lokal.
2. Mengonversi gambar ke RGB dan mengekstrak vektor embedding 512 dimensi via CLIP.
3. Mengompres dan menyimpan thumbnail gambar teroptimasi ke `backend/data/reference_images/` dengan format penamaan `hf_batik_{idx:04d}_{slug}.jpg`.
4. Membangun indeks `faiss.IndexFlatIP` dan menyimpannya ke file biner `backend/data/index/index.faiss`.
5. Menyimpan metadata terstruktur (ID, path thumbnail, label motif, daerah, kategori, lisensi) ke `backend/data/index/metadata.json`.

---

## 6. Design System & Standar UI/UX

### 6.1 Filosofi Desain: Paper & Ink
Mengacu pada PRD Section 8.1, antarmuka Tarum sengaja dirancang menyerupai **instrumen verifikasi ilmiah/presisi**, bukan landing page komersial atau template AI generik:
- Menghindari bayangan tebal (*no blurry box-shadows*), menggunakan garis tipis 1px (`Line Grey`).
- Menghindari sudut membulat berlebihan (*uniform border-radius*).
- Menghindari huruf kapital semua (*NO ALL-CAPS*).

### 6.2 Palet Warna (Design Tokens)
Didefinisikan di `frontend/src/index.css`:
| Token CSS | Hex Code | Karakter & Fungsi |
|---|---|---|
| `--color-paper` | `#F7F6F3` | Background utama, bernuansa kertas netral (bukan krem hangat) |
| `--color-ink` | `#1A1A18` | Teks utama, hampir hitam pekat, serta indikator Risiko Tinggi |
| `--color-indigo` | `#2B3A67` | Aksen brand Tarum (pewarna alami daun indigofera) & status Risiko Rendah |
| `--color-line` | `#D8D5CE` | Garis batas tipis pembagi panel asimetris 40/60 dan kartu |
| `--color-amber` | `#B8843A` | Indikator status Risiko Sedang & status reconnecting sistem |
| `--color-ink-secondary` | `#4E4C47` | Teks keterangan, paragraf deskripsi |
| `--color-ink-muted` | `#7D7A73` | Metadata teknis, ukuran file, latency ms |
| `--color-paper-contrast` | `#FFFFFF` | Background panel upload kiri dan kartu pembanding |

### 6.3 Tipografi
- **UI & Teks Konten:** `Inter Tight` (Grotesk modern, bersih, terbaca jelas).
- **Data Skor & Metadata:** `IBM Plex Mono` (Memberikan nuansa angka metrologi / instrumen pengukuran presisi).

### 6.4 Layout Asimetris 40/60
Halaman utama dibagi menjadi dua panel proporsional:
- **Panel Kiri (40%):** Form unggah file (drag-and-drop), seleksi kategori, tombol eksekusi "Cek Sekarang", dan status sistem.
- **Panel Kanan (60%):** Kanvas hasil verifikasi, skor kemiripan hero (animasi count-up 0 → skor final), daftar kartu pembanding top-5 berdampingan, dan kartu rekomendasi legal.

---

## 7. Spesifikasi API & Kontrak Data

### 7.1 `GET /health`
Digunakan untuk liveness & readiness probe server serta polling status oleh frontend.
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "index_loaded": true,
  "total_indexed_images": 200,
  "embedding_dimension": 512,
  "timestamp": "2026-09-09T08:00:00.000000"
}
```

### 7.2 `POST /check`
Endpoint inti untuk mengevaluasi kemiripan visual gambar desain.
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: `UploadFile` (Wajib, format: JPG/JPEG/PNG/WEBP, max 5 MB).
  - `category`: `str` (Opsional, query/filter kategori).
- **Response `200 OK`:**
```json
{
  "query": {
    "filename": "sketsa_batik_anggrek.jpg",
    "size_bytes": 1048576
  },
  "max_similarity_score": 38.42,
  "overall_risk_level": "Cukup Orisinal",
  "recommendation": "Karya ini memiliki tingkat orisinalitas tinggi (< 50%). Aman untuk diproduksi dan didaftarkan ke DJKI.",
  "matches": [
    {
      "id": "hf_batik_0012",
      "score": 38.42,
      "risk_level": "Cukup Orisinal",
      "category": "batik",
      "image_url": "/static/reference_images/hf_batik_0012_anggrek.jpg",
      "metadata": {
        "motif": "Anggrek",
        "region": "Banten",
        "source": "Hugging Face Batik-Indonesia",
        "license_notice": "Riset non-komersial / Proof of Concept (PRD Sec 7.1)"
      }
    }
  ],
  "execution_time_ms": 142.5
}
```
- **Error Responses:**
  - `400 Bad Request`: Ekstensi file tidak didukung atau file gambar rusak/korup.
  - `413 Payload Too Large`: Ukuran file melebihi 5 MB.
  - `503 Service Unavailable`: Model atau indeks FAISS belum siap dimuat.

### 7.3 `GET /static/reference_images/{filename}`
Menyajikan file gambar thumbnail referensi secara statis ke peramban.

---

## 8. Konfigurasi Environment

### 8.1 Backend (`backend/.env`)
| Variabel | Tipe Data | Default | Keterangan |
|---|---|---|---|
| `TARUM_MODEL_NAME` | String | `clip-ViT-B-32` | Nama model pretrained CLIP vision encoder |
| `TARUM_ONNX_MODEL_PATH` | String | `backend/data/models/clip_vision_int8.onnx` | Lokasi model ONNX INT8 terkuantisasi |
| `TARUM_HF_DATASET` | String | `muhammadsalmanalfaridzi/Batik-Indonesia` | Nama dataset Hugging Face referensi |
| `TARUM_HOST` | String | `0.0.0.0` | Host listener server |
| `TARUM_PORT` | Integer | `8000` | Port listener server |
| `TARUM_CORS_ORIGINS` | String | `http://localhost:5173,...` | Daftar origin diizinkan (dipisah koma) |
| `TARUM_MAX_UPLOAD_SIZE_MB` | Float | `5.0` | Batas maksimum ukuran file upload |
| `TARUM_DEFAULT_TOP_K` | Integer | `5` | Jumlah pembanding yang dikembalikan |
| `TARUM_RISK_THRESHOLD_LOW` | Float | `50.0` | Ambang batas batas bawah orisinalitas |
| `TARUM_RISK_THRESHOLD_HIGH`| Float | `75.0` | Ambang batas kemiripan tinggi |

### 8.2 Frontend (`frontend/.env`)
| Variabel | Default | Keterangan |
|---|---|---|
| `VITE_API_BASE_URL` | *(Kosong)* | Kosong jika memakai Vite proxy internal (`/api`); isi URL jika backend terpisah |
| `VITE_APP_TITLE` | `Tarum — Visual IP Screening` | Judul aplikasi di browser |
| `VITE_MAX_UPLOAD_SIZE_MB` | `5` | Validasi awal ukuran file di browser sebelum upload |
| `VITE_PDKI_URL` | `https://pdki-indonesia.dgip.go.id` | Tautan navigasi ke portal resmi HKI |

---

## 9. Panduan Operasional & Deployment

### 9.1 Menjalankan Secara Lokal
```bash
# 1. Menjalankan Backend
source .venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Menjalankan Frontend
cd frontend
npm run dev
# Buka http://localhost:5173 di browser
```

### 9.2 Menjalankan Pengujian Kualitas (Testing)
```bash
# Pengujian Unit Test Backend (Pytest)
PYTHONPATH=. pytest -p no:launch_testing backend/tests/ -v

# Pengujian Build Frontend
cd frontend && npm run build
```

### 9.3 Pipeline CI/CD Otomatis
- **Backend ([`.github/workflows/backend-deploy.yml`](.github/workflows/backend-deploy.yml))**: Menjalankan pengujian `pytest`. Jika lulus, otomatis merilis ke Heroku melalui `Procfile` dan `runtime.txt`.
- **Frontend**: Memverifikasi build Vite (`npm run build`) dan merilis bundle produksi ke Firebase Hosting (`https://tarum-visual-ip.web.app`) via Firebase CLI (`firebase deploy --only hosting`).

---

## 10. Troubleshooting & Gotchas

### 10.1 Penanganan Waktu Inisialisasi Backend
* **Karakteristik Inisialisasi:** Dengan model **ONNX Runtime INT8**, inisialisasi sesi model berlangsung sangat cepat (**< 300 milidetik**) saat Uvicorn pertama kali berjalan, jauh lebih cepat dibanding runtime PyTorch terdahulu (~15–20 detik).
* **Mekanisme Ketahanan Frontend:**
  1. Frontend tetap dilengkapi polling liveness setiap 4 detik ke `/api/health`.
  2. Frontend menampilkan status "Backend sedang bersiap / terputus" secara informatif jika server backend belum selesai startup atau sedang proses restart/deploy.

### 10.2 Konflik Pytest dengan Plugin ROS 2 (`launch_testing`)
* **Gejala:** Muncul error `launch_testing.pytest.hooks` saat menjalankan `pytest` di lingkungan Linux dengan instalasi ROS 2.
* **Solusi:** Selalu jalankan pytest dengan flag pembatalan plugin ROS:
  ```bash
  pytest -p no:launch_testing backend/tests/
  ```

### 10.3 Gambar Thumbnail Tidak Muncul di Frontend
* **Penyebab:** Path static folder belum termuat atau file gambar belum diunduh ke `backend/data/reference_images/`.
* **Solusi:** Pastikan skrip `python backend/scripts/build_index.py --source hf` sudah dijalankan sekali untuk mengunduh thumbnail batik.

---

## 11. Legal Disclaimer & Batasan Sistem

Pernyataan legal berikut dicantumkan secara eksplisit pada antarmuka pengguna:
> *"Ini bukan opini hukum resmi. Tarum adalah instrumen screening awal mandiri berbasis kemiripan visual citra untuk membantu pelaku usaha kriya dan fashion memutuskan langkah berikutnya sebelum memproduksi massal atau mengajukan pendaftaran Desain Industri / Hak Cipta ke DJKI."*

Sistem **tidak memberikan keputusan keabsahan hukum**, melainkan menyediakan alat bantu kurasi visual yang objektif bagi perajin kriya Indonesia.
