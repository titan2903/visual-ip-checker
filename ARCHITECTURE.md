# Arsitektur Teknis Sistem Tarum (Visual IP Screening)

## 1. Ikhtisar Arsitektur
Tarum adalah aplikasi web pendeteksi kemiripan visual (*visual IP screening*) yang dirancang khusus untuk pelaku UMKM kriya dan fashion nusantara. Sistem membandingkan motif kriya baru dengan database motif budaya Indonesia.

Sistem terdiri dari dua komponen utama:
1. **Frontend**: Antarmuka berbasis React 19 + Vite (dihosting di Firebase Hosting - `tarum-visual-ip.web.app`), dibangun dengan Vanilla CSS tokenized (tanpa Tailwind).
2. **Backend**: FastAPI + ONNX Runtime C++ Engine + FAISS (dihosting di Heroku Basic Dyno 512MB RAM).

---

## 2. Diagram Alur Data

```text
┌─────────────────────────────────────────────────────────────┐
│                    Browser Klien / Frontend                │
│        React 19 + Vite (Firebase Hosting Production)        │
│  - Input Gambar: Drag & Drop / File Input (max 5MB)         │
│  - Polling Status Server: GET /api/health                   │
│  - Rendering Hasil: Risk Badge, Top-5 Matches, Rekomendasi │
└──────────────────────────────┬──────────────────────────────┘
                               │
                 HTTP POST /api/check (Multipart)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  FastAPI Backend (Heroku Dyno)              │
│  - Validasi MIME, Ukuran File (max 5MB), dan Integritas PIL │
│  - Pra-pemrosesan: Resize Bicubic 224x224, Center Crop,     │
│    Normalisasi Mean/Std CLIP, Transpose (3, 224, 224)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                Input Tensor: (1, 3, 224, 224)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│           ONNX Runtime INT8 (clip_vision_int8.onnx)         │
│  - Model: OpenAI CLIP ViT-B/32 Vision Encoder (INT8)        │
│  - Ukuran File Model: ~85 MB                                │
│  - Runtime: C++ onnxruntime CPUExecutionProvider (No Torch) │
│  - Penggunaan RAM Total: ~170 MB (Batas Heroku: 512 MB)     │
│  - Output: 512-dimensi visual feature vector                │
│  - Normalisasi L2: ||v|| = 1.0                              │
└──────────────────────────────┬──────────────────────────────┘
                               │
               Normalized Vector: (1, 512)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│             Search Service & FAISS Vector Index             │
│  - Index: faiss.IndexFlatIP (Cosine Similarity)             │
│  - Metadata Lookup: metadata.json (200 Motif Batik)         │
│  - Filter Kategori: Opsional (cth: "batik", "tenun")        │
│  - Scoring: Skor = clamp((u · v) * 100, 0, 100)             │
│  - Risk Tier: Rendah (<50%), Sedang (50-75%), Tinggi (>=75%)│
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Komponen Utama

### 3.1 `EmbeddingService` (`backend/app/services/embedding_service.py`)
- Memuat model `backend/data/models/clip_vision_int8.onnx`.
- Pra-pemrosesan citra murni dengan Pillow dan NumPy.
- Tidak memerlukan PyTorch atau Hugging Face API saat runtime.
- Sangat stabil, hemat memori (~170 MB VmRSS), dan cepat (<150ms per inferensi CPU).

### 3.2 `SearchService` (`backend/app/services/search_service.py`)
- Memuat indeks FAISS `backend/data/index/index.faiss` dan `metadata.json`.
- Menjalankan pencarian top-K terdekat menggunakan operasi Inner Product (karena vektor dinormalisasi L2, ini identik dengan Cosine Similarity).
- Memetakan metadata motif, lisensi, dan gambar referensi untuk ditampilkan di UI.

### 3.3 `API Routes` (`backend/app/api/routes.py`)
- `GET /health`: Pemeriksaan kesehatan sistem, status model ONNX, dan status indeks FAISS.
- `POST /check`: Endpoint utama untuk menganalisis gambar kriya dan mengembalikan hasil pencocokan.
- `/static/reference_images/*`: Static file mounting untuk menyajikan thumbnail gambar referensi.

---

## 4. Keunggulan Solusi ONNX INT8
1. **Akurasi Tinggi**: Menghasilkan skor kemiripan >90% (hingga 97.6%) untuk motif yang identik/serupa.
2. **Efisiensi RAM**: Menurunkan konsumsi RAM dari >1.4GB (PyTorch) menjadi ~170MB (ONNX Runtime).
3. **Mandiri Tanpa API Eksternal**: Bebas dari downtime, rate limit, dan biaya API pihak ketiga.
4. **Deploy Aman di Heroku**: Ukuran slug total ~220MB (jauh di bawah batas 500MB Heroku).
