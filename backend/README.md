# Tarum — Backend API & Core Pipeline

Layanan backend untuk **Tarum (Visual IP Checker)** yang bertugas melakukan inferensi embedding visual desain kriya/fashion menggunakan model **CLIP ViT-B/32** (dioptimasi menggunakan PyTorch Dynamic Quantization untuk efisiensi RAM) dan pencarian kemiripan vektor menggunakan **FAISS**.

---

## 🏗️ Arsitektur & Struktur Direktori

```text
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # Endpoint: POST /check, GET /health
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding_service.py   # Ekstraksi fitur CLIP (sentence-transformers)
│   │   └── search_service.py      # Pencarian vektor FAISS & skor kemiripan
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── check.py               # Model Pydantic untuk request & response
│   ├── config.py                  # Konfigurasi path, batas upload, & threshold
│   ├── main.py                    # Aplikasi FastAPI, CORS, & static file serving
│   └── __init__.py
├── data/
│   ├── reference_images/          # Gambar referensi pembanding (.jpg, .png, .webp)
│   └── index/
│       ├── index.faiss            # File indeks vektor biner FAISS
│       └── metadata.json          # Metadata karya referensi (ID, judul, kategori, dll.)
├── scripts/
│   ├── __init__.py
│   ├── create_dummy_data.py       # Generator 12 gambar motif kriya dummy
│   └── build_index.py             # Script pembuat indeks vektor FAISS dari data/
├── tests/
│   ├── __init__.py
│   └── test_api.py                # Test suite pytest (7 skenario pengujian)
├── requirements.txt               # Dependensi Python
└── README.md                      # Dokumentasi teknis backend ini
```

---

## 🚀 Setup & Menjalankan Backend

### 1. Prasyarat
- Python 3.10 ke atas (diuji pada Python 3.12)
- Virtual environment aktif (misal `.venv` di root project)

### 2. Instalasi Dependensi
Dari direktori root proyek:
```bash
# Aktifkan virtual environment
source .venv/bin/activate

# Install dependensi backend
pip install -r backend/requirements.txt
# Atau dengan uv (jauh lebih cepat):
uv pip install -r backend/requirements.txt
```

### 3. Persiapan Dataset & Pembangunan Indeks

Tarum mengadopsi dataset referensi resmi Hugging Face [`muhammadsalmanalfaridzi/Batik-Indonesia`](https://huggingface.co/datasets/muhammadsalmanalfaridzi/Batik-Indonesia) yang memuat **2.599 gambar** dalam format `imagefolder` mencakup **38 kelas motif batik nusantara** (Aceh, Bali, Megamendung, Parang, Kawung, Asmat, dll.).

#### Pilihan A: Mengindeks Dataset Hugging Face (Rekomendasi MVP)
```bash
# Mengindeks dataset Hugging Face Batik Indonesia (otomatis unduh & simpan thumbnail)
python backend/scripts/build_index.py --source hf

# Opsi: batasi jumlah gambar untuk pengujian cepat (misal 300 gambar)
python backend/scripts/build_index.py --source hf --limit 300
```

#### Pilihan B: Fallback Dataset Lokal / Sintetis
```bash
# 1. Buat 12 motif sintetis (jika ingin mencoba offline)
python backend/scripts/create_dummy_data.py

# 2. Bangun indeks dari folder lokal backend/data/reference_images/
python backend/scripts/build_index.py --source local
```

#### Opsi Parameter CLI `build_index.py`:
- `--source [hf|local]`: Sumber dataset (`hf` untuk Hugging Face, `local` untuk folder lokal). Default: `hf`
- `--dataset-name <str>`: Nama dataset Hugging Face (default: `muhammadsalmanalfaridzi/Batik-Indonesia`)
- `--limit <int>`: Batas maksimal gambar yang diindeks (opsional, default: seluruh data)
- `--data-dir <path>`: Folder penyimpan thumbnail gambar referensi (default: `backend/data/reference_images`)
- `--output-dir <path>`: Folder output indeks (default: `backend/data/index`)
- `--metric [ip|l2]`: Metrik pencarian FAISS (`ip` untuk Cosine Similarity, `l2` untuk Euclidean Distance)
- `--batch-size <int>`: Ukuran batch inferensi CLIP (default: 32)

> ⚠️ **Catatan Provenance & Lisensi (PRD Section 7.1):**
> Dataset batik publik ini digunakan secara eksplisit sebagai *"dataset riset non-komersial untuk proof-of-concept (MVP)"*. Pada roadmap V1 pasca-hackathon, indeks akan diperluas melalui kemitraan data opt-in pengrajin UMKM, digitalisasi koleksi domain publik museum tekstil, dan pangkalan data PDKI resmi.

### 4. Menjalankan Server FastAPI
Dari direktori root:
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
Jika Anda sedang berada di dalam folder `backend/`:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 Dokumentasi Endpoint API

### 1. `POST /check` — Screening Kemiripan Desain
Endpoint utama untuk memeriksa kemiripan visual gambar desain yang diunggah pengguna terhadap database referensi.

- **Content-Type**: `multipart/form-data`
- **Parameter Body**:
  - `file`: File gambar desain (`image/jpeg`, `image/png`, `image/webp`).
  - **Batas Ukuran**: Maksimum 5 MB.

#### Contoh Request (`curl`):
```bash
curl -X POST "http://localhost:8000/check" \
  -F "file=@backend/data/reference_images/batik_parang_01.jpg"
```

#### Contoh Response (`200 OK`):
```json
{
  "status": "success",
  "query": {
    "filename": "batik_parang_01.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 120987
  },
  "max_similarity_score": 100.0,
  "risk_level": "Sangat Mirip",
  "recommendation": "Desain memiliki kemiripan visual tinggi dengan karya referensi. Sangat disarankan untuk merevisi motif atau elemen spesifik dan berkonsultasi mengenai HKI sebelum produksi massal.",
  "results": [
    {
      "rank": 1,
      "id": 3,
      "filename": "batik_parang_01.jpg",
      "image_url": "/static/reference_images/batik_parang_01.jpg",
      "title": "Batik Parang Rusak Klasik",
      "category": "batik",
      "similarity_score": 100.0,
      "risk_level": "Sangat Mirip",
      "metadata": {
        "width": 400,
        "height": 400,
        "description": "Motif parang diagonal soga cokelat tradisional Surakarta",
        "source": "dummy_dataset_curated"
      }
    },
    {
      "rank": 2,
      "id": 0,
      "filename": "anyaman_rotan_lombok_06.jpg",
      "image_url": "/static/reference_images/anyaman_rotan_lombok_06.jpg",
      "title": "Anyaman Rotan Motif Selisih",
      "category": "anyaman",
      "similarity_score": 87.38,
      "risk_level": "Sangat Mirip",
      "metadata": {
        "width": 400,
        "height": 400,
        "description": "Pola silang anyaman rotan natural khas Lombok",
        "source": "dummy_dataset_curated"
      }
    }
  ],
  "disclaimer": "Ini bukan opini hukum. Hasil ini membantu kamu memutuskan langkah berikutnya, bukan menggantikan konsultasi HKI resmi.",
  "execution_time_ms": 115.42
}
```

#### Kode Respon Error:
- `400 Bad Request`: Format file tidak didukung, file kosong, atau data gambar rusak/tidak valid.
- `413 Content Too Large`: Ukuran file melebihi 5 MB.
- `503 Service Unavailable`: Indeks FAISS belum dibangun di server.

---

### 2. `GET /health` — Health Check
Memeriksa kesiapan model CLIP dan status indeks FAISS.

#### Contoh Response:
```json
{
  "status": "healthy",
  "model_name": "clip-ViT-B-32",
  "model_loaded": true,
  "index_loaded": true,
  "total_indexed_images": 12
}
```

---

### 3. `GET /static/reference_images/{filename}` — Static Thumbnail
Menyajikan file gambar referensi yang tersimpan di server secara statis sehingga frontend dapat langsung merender thumbnail karya pembanding.

---

## ⚙️ Logika Teknis & Kalkulasi Skor

1. **Ekstraksi Embedding**:
   - Model `clip-ViT-B-32` via `sentence-transformers` menghasilkan vektor fitur berdimensi 512.
   - Model dikuantisasi secara dinamis (PyTorch Dynamic Quantization ke `qint8`) saat berjalan untuk menghemat RAM (ideal untuk tier Heroku Basic/Eco).
   - Vektor secara eksplisit dinormalisasi ke satuan L2 norm ($\|v\|_2 = 1.0$).

2. **Perhitungan Skor Kemiripan (%)**:
   - Indeks FAISS menggunakan `IndexFlatIP` (Inner Product).
   - Karena vektor ternormalisasi L2, Inner Product ekuivalen dengan **Cosine Similarity**:
     $$\text{Cosine Similarity } S = u \cdot v = \cos(\theta)$$
   - Skor kemiripan dipetakan ke skala 0% – 100%:
     $$\text{Similarity Score (\%)} = \min(100.0, \max(0.0, S \times 100.0))$$

3. **Klasifikasi Risiko Kemiripan**:
   - **Skor < 50.0%**: `Cukup Orisinal` (Potensi pelanggaran rendah, panduan pendaftaran HKI).
   - **50.0% ≤ Skor < 75.0%**: `Perlu Ditinjau` (Kemiripan sedang pada elemen motif tertentu).
   - **Skor ≥ 75.0%**: `Sangat Mirip` (Kemiripan tinggi, rekomendasi revisi motif & konsultasi HKI).

---

## 🧪 Menjalankan Automated Tests

Jalankan test suite menggunakan pytest:
```bash
# Dari root proyek
pytest backend/tests/ -v

# Atau jika ada konflik dengan plugin sistem lokal:
PYTHONPATH=. pytest -p no:launch_testing backend/tests/ -v
```
Test suite mencakup:
- Root and health check endpoint verification.
- Static file serving endpoint test.
- Valid image similarity check execution and schema conformance.
- Validation for invalid file extensions (.pdf, .txt).
- Corrupted image binary handling.
- Enforcement of max 5 MB upload limits.
