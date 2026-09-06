# Tarum — Frontend (React + Vite)

Antarmuka pengguna untuk **Tarum (Visual IP Checker)** yang dirancang khusus untuk pelaku UMKM kriya dan fashion guna mengecek kemiripan visual desain motif sebelum didaftarkan ke HKI (PDKI) atau dirilis ke marketplace.

UI ini dibangun dengan **React + Vite** dan **Vanilla CSS murni**, mengimplementasikan secara ketat **Token System & Wireframe PRD Section 8.1 & 8.2**.

---

## 🎨 Token System & Pedoman Desain

Sesuai dengan PRD Section 8.1, antarmuka ini dirancang sebagai **instrumen verifikasi/pengukuran**, bukan landing page promosi dan secara eksplisit menghindari gaya klise template AI:
- ❌ **Tanpa Drop Shadow Generik**: Pembagian ruang murni memakai garis tipis 1px `Line Grey` (`#D8D5CE`).
- ❌ **Tanpa Border-Radius Seragam**: Elemen bertepi tegas (*crisp edges*) untuk kesan instrumen presisi.
- ❌ **Tanpa ALL-CAPS**: Hierarki dibangun dari font-weight dan ukuran font.
- ❌ **Tanpa Ikon Panah "→" di Tombol**: Menggunakan label aktif yang lugas (*"Cek Sekarang"*).

### Palet Warna (5 Named Colors):
| Token | Hex Code | Peran / Penggunaan |
|---|---|---|
| **Paper** | `#F7F6F3` | Background utama kanvas, netral, tidak bernuansa krem hangat. |
| **Ink** | `#1A1A18` | Teks utama dan warna badge status risiko tinggi (*"Sangat Mirip"*). |
| **Indigo Tarum** | `#2B3A67` | Aksen utama merujuk warna alami tenun/batik, tombol aksi, dan status *"Cukup Orisinal"*. |
| **Line Grey** | `#D8D5CE` | Garis pembatas tipis 1px antar panel dan kartu. |
| **Signal Amber** | `#B8843A` | Satu-satunya warna penanda status risiko menengah (*"Perlu Ditinjau"*). |

### Tipografi:
- **UI & Teks Umum**: **Inter Tight** (Google Fonts) — modern grotesk netral.
- **Angka Skor & Data**: **IBM Plex Mono** (Google Fonts) — khusus angka persentase kemiripan dan metadata teknis (latensi, ukuran file, ID).

### Tata Letak (Asymmetric Split 40 / 60):
- **Panel Kiri (40%)**: Upload desain (drag-and-drop zone), preview gambar, pilihan kategori produk, tombol *"Cek Sekarang"*, dan disclaimer hukum permanen.
- **Panel Kanan (60%)**: Hasil evaluasi kemiripan, skor mono besar di kanan atas, ringkasan kontekstual, top-5 kartu pembanding ber-thumbnail, dan panduan tindak lanjut ke portal resmi PDKI.

---

## 🚀 Panduan Menjalankan Frontend

### 1. Prasyarat
- Node.js versi 18+ (direkomendasikan Node.js 20/22)
- Backend FastAPI sudah berjalan di port `8000`

### 2. Instalasi Dependensi
```bash
cd frontend
npm install
```

### 3. Menjalankan Server Pengembangan (Vite)
```bash
npm run dev
```
Aplikasi akan aktif di: **[http://localhost:5173](http://localhost:5173)**

### 4. Build untuk Produksi
```bash
npm run build
```
Output bundle produksi akan tersimpan di folder `frontend/dist/`.

---

## 🔌 Integrasi API Backend

Vite telah dikonfigurasi dengan proxy internal di [`vite.config.js`](vite.config.js):
- Request `/api/check` otomatis diteruskan ke backend FastAPI: `http://127.0.0.1:8000/check`
- Request `/api/health` memeriksa kesiapan model CLIP dan FAISS index.
- Request `/static/reference_images/...` menyajikan thumbnail gambar pembanding langsung dari server backend.
