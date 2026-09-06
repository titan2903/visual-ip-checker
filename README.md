# Tarum — Visual IP Checker (Backend Core - Fase 1)

Tarum adalah alat screening awal kemiripan visual desain untuk pelaku UMKM kriya dan fashion. Sistem mengecek kemiripan visual motif/pola (batik, tenun, kerajinan) menggunakan model pretrained image embedding (**CLIP ViT-B/32**) dan pencarian vektor berkecepatan tinggi (**FAISS**).

---

## 📁 Struktur Direktori

```text
visual-ip-checker/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py              # Endpoint API (POST /check, GET /health, GET /)
│   │   ├── services/
│   │   │   ├── embedding_service.py   # Ekstraksi fitur CLIP ViT-B/32 (sentence-transformers)
│   │   │   └── search_service.py      # Pencarian vektor FAISS & kalkulasi skor kemiripan
│   │   ├── schemas/
│   │   │   └── check.py               # Skema Pydantic request & response
│   │   ├── config.py                  # Konfigurasi path, batas upload, & threshold risiko
│   │   └── main.py                    # Entrypoint FastAPI & static file mounting
│   ├── data/
│   │   ├── reference_images/          # Dataset gambar referensi produk/motif
│   │   └── index/                     # File FAISS (index.faiss & metadata.json)
│   ├── scripts/
│   │   ├── create_dummy_data.py       # Generator 12 gambar motif dummy kriya & fashion
│   │   └── build_index.py             # Script pembangun indeks FAISS dari dataset
│   ├── tests/
│   │   └── test_api.py                # Unit & integration tests
│   └── requirements.txt
├── frontend/                          # Folder terpisah untuk React + Vite (Fase 2)
│   └── README.md
├── PRD.md                             # Dokumen PRD lengkap
├── PROMPT_PHASE1.md                   # Instruksi spesifikasi Fase 1
└── README.md                          # Panduan eksekusi lokal
```

---

## 🚀 Panduan Menjalankan Secara Lokal

### 1. Prasyarat
- Python 3.10+ (direkomendasikan Python 3.12)
- Package manager: `uv` (sangat cepat) atau `pip` bawaan

### 2. Setup Virtual Environment & Install Dependensi

```bash
# Buat virtual environment
uv venv .venv
# atau: python3 -m venv .venv

# Aktifkan virtual environment
source .venv/bin/activate

# Install dependensi
uv pip install -r backend/requirements.txt
# atau: pip install -r backend/requirements.txt
```

### 3. Siapkan Dataset Referensi & Bangun Indeks FAISS

Jika belum memiliki dataset asli, buat 12 gambar sintetis motif kriya/fashion untuk pengujian:

```bash
python backend/scripts/create_dummy_data.py
```

> **Catatan:** Anda dapat menambahkan gambar motif asli Anda kapan saja ke dalam folder `backend/data/reference_images/`.

Setelah gambar tersedia, bangun indeks vektor FAISS:

```bash
python backend/scripts/build_index.py
```
*Output: `backend/data/index/index.faiss` dan `backend/data/index/metadata.json`.*

### 4. Jalankan Server FastAPI

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Aplikasi akan berjalan di:
- **API Base URL**: [http://localhost:8000](http://localhost:8000)
- **Dokumentasi Interaktif (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Menguji Endpoint `POST /check`

### Menggunakan `curl`:
```bash
curl -X POST "http://localhost:8000/check" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@backend/data/reference_images/batik_parang_01.jpg"
```

### Contoh Respon JSON:
```json
{
  "status": "success",
  "query": {
    "filename": "batik_parang_01.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 62450
  },
  "max_similarity_score": 100.0,
  "risk_level": "Sangat Mirip",
  "recommendation": "Desain memiliki kemiripan visual tinggi dengan karya referensi. Sangat disarankan untuk merevisi motif atau elemen spesifik dan berkonsultasi mengenai HKI sebelum produksi massal.",
  "results": [
    {
      "rank": 1,
      "id": 0,
      "filename": "batik_parang_01.jpg",
      "image_url": "/static/reference_images/batik_parang_01.jpg",
      "title": "Batik Parang Rusak Klasik",
      "category": "batik",
      "similarity_score": 100.0,
      "risk_level": "Sangat Mirip",
      "metadata": {
        "description": "Motif parang diagonal soga cokelat tradisional Surakarta",
        "source": "dummy_dataset_curated"
      }
    }
  ],
  "disclaimer": "Ini bukan opini hukum. Hasil ini membantu kamu memutuskan langkah berikutnya, bukan menggantikan konsultasi HKI resmi.",
  "execution_time_ms": 112.4
}
```

---

## ⚙️ Menjalankan Automated Tests

Jalankan pengujian end-to-end dengan pytest:
```bash
pytest backend/tests/ -v
```

---

## 📌 Asumsi Teknis (Technical Decisions)

1. **Model Embedding**: Menggunakan `clip-ViT-B-32` via `sentence-transformers` sesuai PRD Section 7. Model ini bekerja sangat baik di CPU maupun GPU dan memiliki latensi inferensi cepat (< 150ms per gambar).
2. **Normalisasi Vektor & Indeks FAISS**:
   - Vektor embedding dinormalisasi L2 ($\|v\| = 1$).
   - FAISS dibangun dengan `IndexFlatIP` (Inner Product). Pada vektor yang dinormalisasi, inner product ekuivalen dengan Cosine Similarity ($S = \cos\theta$).
   - Formula konversi skor: $\text{Skor Persentase} = \max(0, \min(100, S \times 100))$.
3. **Threshold Risiko Kemiripan**:
   - **Skor < 50.0%**: *Cukup Orisinal*
   - **50.0% ≤ Skor < 75.0%**: *Perlu Ditinjau*
   - **Skor ≥ 75.0%**: *Sangat Mirip*
4. **Validasi File**: Maksimal 5 MB dengan format JPEG, PNG, atau WEBP sesuai *Must Have* PRD Section 6.
5. **Static File Serving**: Gambar referensi disajikan melalui `/static/reference_images/` agar frontend dapat langsung merender thumbnail karya pembanding.
