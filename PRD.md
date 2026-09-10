# PRD: Tarum — Visual IP Screening untuk Pelaku Kriya & Fashion

**Versi:** 0.2 (Diselaraskan dengan Studi Kasus UMKM Datik Batik — Submission EKRAF x Google Career Certificates)  
**Status:** Draft MVP Validated  
**Owner:** TITANIO YUDISTA  
**Slide Presentasi (Canva):** [canva.link/tarum](https://canva.link/tarum)  
**Terakhir diperbarui:** 10 September 2026  

---

## 1. Ringkasan Eksekutif

**Tarum** adalah alat screening awal kemiripan visual (*image-similarity search*) yang membantu pelaku UMKM kriya dan fashion — seperti mitra studi kasus kami, **Datik Batik** (Tangerang Selatan) — mengecek apakah rancangan motif produk mereka (motif batik, pola, tata letak ornamen) memiliki potensi kemiripan dengan karya yang sudah beredar di pasar publik atau database warisan budaya nusantara, sebelum mereka merilis produk ke pasar atau mendaftarkannya ke Direktorat Jenderal Kekayaan Intelektual (DJKI).

Ini bukan pengganti jasa hukum HKI atau vonis pengadilan. Tarum adalah **instrumen screening awal (pre-screening instrument)** mandiri yang cepat (< 5 detik), gratis, dan dapat diakses langsung oleh perajin di bengkel kerja kriya tanpa membutuhkan pemahaman hukum rumit — menutup celah sistem resmi pemerintah (PDKI/DJKI) yang hingga saat ini hanya mendukung pencarian berbasis kata kunci teks, bukan pencocokan visual gambar motif.

---

## 2. Problem Statement

### 2.1 Masalah Inti (Studi Kasus: Datik Batik, Tangerang Selatan)
UMKM Datik Batik yang telah memproduksi kriya batik tulis dan cap di Tangerang Selatan sejak tahun 2012 secara rutin menciptakan ragam hias motif baru (misalnya eksplorasi flora anggrek van douglas khas Tangsel). Namun, perajin menghadapi risiko besar yang berakar dari ketiadaan alat verifikasi visual:

1. **Risiko Pelanggaran Tak Sengaja (*Unintentional Infringement*):** Motif baru yang digambar perajin ternyata memiliki kesamaan pola dengan karya pihak lain yang sudah terdaftar, berujung pada somasi hukum, penolakan pendaftaran HKI di DJKI, serta kerugian fatal modal bahan baku (*sunk cost*) jika kain sudah terlanjur diproduksi massal.
2. **Keterbatasan Aksesibilitas Jasa Legal:** Biaya penelusuran HKI melalui biro jasa hukum atau konsultan independen berkisar antara Rp 2 – 5 juta per desain—beban biaya yang mustahil dipenuhi secara berkala oleh kas usaha mikro kriya.

### 2.2 Kenapa Masalah Ini Valid (Evidence)
- **Keterbatasan Sistem Resmi:** Pangkalan Data Kekayaan Intelektual (PDKI) DJKI hanya menyediakan pencarian teks berdasarkan nama karya atau nama pemilik. Motif batik yang memiliki kemiripan visual hingga 80% namun dinamai berbeda dipastikan luput dari deteksi penelusuran manual.
- **Ketiadaan Tools Visual untuk Kriya:** Seluruh plagiarism checker populer (seperti Quetext, Turnitin, Copyleaks) hanya menangani teks dokumen, belum ada yang dirancang khusus untuk menganalisis karakteristik visual motif fisik tekstil/kriya.
- **Kesenjangan Digital Ekraf:** Riset menunjukkan pelaku usaha mikro kriya memiliki talenta seni tinggi namun terbatas dalam literasi hukum dan modal teknologi, sehingga rentan menjadi korban sengketa hak cipta.

### 2.3 Siapa yang Terdampak
- **Primer:** Pelaku UMKM kriya & fashion skala mikro-kecil, dipersonifikasikan oleh perajin dan desainer Datik Batik di Tangerang Selatan serta pengrajin batik nusantara.
- **Sekunder:** Dinas Koperasi & UKM, Dekranasda daerah, konsultan HKI, dan inkubator komunitas ekraf yang mendampingi legalitas karya binaan.

---

## 3. Goals & Non-Goals

### 3.1 Goals (untuk MVP Hackathon & Validasi Pilot)
- **G1:** Pengguna dapat mengunggah 1 foto rancangan desain/kain dan memperoleh skor kemiripan visual terhadap 2.599 motif referensi Batik Indonesia dalam waktu **< 5 detik**.
- **G2:** Sistem menyajikan tampilan visual berdampingan (*side-by-side*) antara gambar pengguna dengan top-5 karya paling mirip beserta transparansi asal-usul motif.
- **G3:** Sistem menyajikan rekomendasi tindakan terarah berbasis tiga tingkat risiko (`Cukup Orisinal`, `Perlu Ditinjau`, `Sangat Mirip`) dilengkapi tautan rujukan ke PDKI DJKI.
- **G4:** Alur pengoperasian sangat intuitif (maksimal 3 langkah: *Upload* → *Cek* → *Baca Rekomendasi*) yang dapat dipakai mandiri oleh perajin tanpa pelatihan teknis.

### 3.2 Non-Goals (Eksplisit di Luar Cakupan MVP)
- Bukan pengganti pendaftaran HKI resmi, bukan opini hukum resmi, dan tidak mengeluarkan vonis hukum ("sah" / "melanggar").
- Bukan pendeteksi plagiarisme teks nama merek atau audio/musik.
- Bukan alat *generative AI* untuk membuat atau memodifikasi desain gambar secara otomatis.
- Tidak memproses berkas pendaftaran HKI secara end-to-end ke sistem DJKI (hanya screening dan navigasi rujukan).

---

## 4. User Personas

| Persona | Profil & Deskripsi | Kebutuhan Utama |
|---|---|---|
| **Ibu Rina / Tim Desain, Datik Batik** | Usaha kriya batik tulis & cap di Tangerang Selatan, berdiri sejak 2012 (~14 tahun), kapasitas 60–100 pcs/bulan, minim latar belakang hukum HKI | Cara cepat, mandiri, dan gratis untuk mengecek orisinalitas motif baru (misal motif flora anggrek Tangsel) sebelum diproduksi massal dan diajukan ke DJKI |
| **Kevin, Founder Brand Fashion Lokal** | Startup fashion kriya kontemporer, memasarkan produk lewat marketplace & media sosial, melek teknologi | Alat screening instan dan bukti komparasi visual pendukung saat merancang koleksi musiman baru |
| **Pendamping UMKM Dekranasda / Dinas Koperasi** | Instansi pembina UMKM kriya daerah di Tangerang Selatan dan sekitarnya | Instrumen kurasi digital praktis untuk memfasilitasi legalitas motif binaan sebelum fasilitasi HKI massal |

---

## 5. User Flow

```
[Landing] → [Upload Foto Desain] → [Proses (loading state jujur, bukan spinner generik)]
                                          │
                                          ▼
                              [Hasil: Skor Kemiripan + Gambar Pembanding]
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                 Skor Rendah       Skor Menengah      Skor Tinggi
              "Cukup Orisinal"   "Perlu Ditinjau"   "Sangat Mirip"
                    │                  │                   │
                    ▼                  ▼                   ▼
          Panduan lanjut ke      Rekomendasi         Rekomendasi revisi
          pendaftaran HKI        modifikasi          + link edukasi HKI
          (link PDKI resmi)      elemen spesifik      & konsultasi
```

---

## 6. Functional Requirements (MoSCoW)

**Must Have**
- Upload gambar (JPEG/PNG, max 5MB) dari kamera atau galeri.
- Image embedding via model pretrained (CLIP atau setara).
- Similarity search terhadap index vektor (top-5 hasil paling mirip).
- Tampilan hasil: skor kemiripan (%), thumbnail pembanding, kategori risiko (rendah/menengah/tinggi).
- Disclaimer yang jelas dan tidak bisa di-dismiss tanpa dibaca: alat ini bukan opini hukum.

**Should Have**
- Riwayat pengecekan tersimpan per user (biar bisa dibandingkan dari waktu ke waktu).
- Panduan singkat "langkah selanjutnya" sesuai kategori risiko, dengan link resmi ke PDKI (pdki-indonesia.dgip.go.id).
- Filter kategori produk (batik, tenun, kerajinan kayu, fashion, dll) untuk mempersempit index pencarian.

**Could Have**
- Highlight area gambar mana yang berkontribusi paling besar terhadap skor kemiripan (visual explainability).
- Ekspor hasil sebagai PDF ringkas — berguna sebagai lampiran pendukung saat konsultasi HKI.

**Won't Have (MVP ini)**
- Integrasi otomatis ke sistem pendaftaran HKI DJKI.
- Multi-image batch upload.
- Akun berbayar/monetisasi.

---

## 7. Technical Architecture

Prinsip: **jangan bangun ulang apa yang sudah ada.** Semua komponen inti pakai model pretrained dan library open-source — tidak ada training model dari nol untuk MVP.

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Frontend    │────▶│  Backend API      │────▶│  Vector Search   │
│  (upload UI) │     │  (FastAPI/Flask)  │     │  (FAISS/pgvector)│
└─────────────┘     └──────────────────┘     └─────────────────┘
                              │                         ▲
                              ▼                         │
                     ┌──────────────────┐               │
                     │  Embedding Model  │───────────────┘
                     │  (CLIP ViT-B/32)  │
                     └──────────────────┘
                              ▲
                              │
                     ┌──────────────────┐
                     │  Dataset Referensi│
                     │  (kurasi manual + │
                     │   scraping ringan)│
                     └──────────────────┘
```

**Stack yang disarankan (budget bootstrap-friendly):**
- Embedding: ONNX Runtime INT8 (`clip_vision_int8.onnx`, ~85MB) dari OpenAI CLIP ViT-B/32, berjalan lokal via C++ runtime sangat cepat, berakurasi tinggi (>90%), dan hemat RAM (~170MB, tanpa PyTorch).
- Vector index: FAISS (in-memory, gratis) untuk demo; Supabase pgvector (tier gratis) kalau butuh persistence.
- Backend: FastAPI, deploy di Heroku Basic / Eco dyno (512MB RAM).
- Frontend: React + Vite, deploy di Firebase Hosting (`tarum-visual-ip.web.app`).
- Storage gambar: Direktori statis lokal yang diindeks ke FAISS.

**Contoh inti pipeline implementasi (menggunakan ONNX Runtime INT8):**
```python
import faiss
import numpy as np
import onnxruntime as ort

# 1. Muat session model ONNX INT8 (RAM ~170MB, tanpa PyTorch)
session = ort.InferenceSession(
    "backend/data/models/clip_vision_int8.onnx", 
    providers=["CPUExecutionProvider"]
)

# 2. Muat FAISS IndexFlatIP (Cosine Similarity via vektor ternormalisasi L2)
index = faiss.read_index("backend/data/index/index.faiss")

# 3. Pra-pemrosesan citra kueri (224x224 Bicubic, normalisasi ImageNet) & ekstraksi
# query_tensor shape: (1, 3, 224, 224)
raw_vec = session.run(["embedding"], {"pixel_values": query_tensor})[0]
norm_vec = raw_vec / np.linalg.norm(raw_vec)  # L2 normalization (unit vector)

# 4. Pencarian top-k di FAISS
similarities, indices = index.search(norm_vec.astype(np.float32), k=5)
# -> skor kemiripan = clamp(similarities[0][i] * 100.0, 0.0, 100.0)
```

### 7.1 Data Requirements

**Dataset terpilih untuk MVP:** [HuggingFace — Batik-Indonesia (muhammadsalmanalfaridzi)](https://huggingface.co/datasets/muhammadsalmanalfaridzi/Batik-Indonesia)

```python
from datasets import load_dataset
ds = load_dataset("muhammadsalmanalfaridzi/Batik-Indonesia")
```

Alasan pemilihan:
- Volume terbesar dari semua kandidat (2.599 gambar) → cukup untuk index similarity search yang tidak terlalu sparse.
- Format `imagefolder` via `datasets` library — langsung kompatibel dengan pipeline embedding (section 7), tidak perlu preprocessing manual seperti unzip/rename dari Kaggle.
- Sudah dalam bentuk HuggingFace Dataset object → gampang diiris untuk train/index-build vs held-out test set saat validasi kualitatif (lihat section 9).

Yang harus dicek/dikerjakan tim sebelum dipakai ke index produksi (bukan blocker untuk demo):
- Baca ulang dataset card untuk detail lisensi per-gambar — belum ada pernyataan lisensi tunggal yang eksplisit di level dataset, jadi perlakukan sebagai *"riset non-komersial"* untuk MVP (lihat catatan provenance di bawah).
- Cek distribusi kelas/daerah asal di dalam dataset — kalau timpang (misalnya dominan motif Jawa), catat sebagai limitasi saat presentasi, jangan diklaim representatif se-Indonesia.

**Dataset cadangan/pelengkap** (kalau butuh menambah variasi kelas atau butuh data beranotasi lisensi jelas):

| Sumber | Isi | Lisensi | Kegunaan |
|---|---|---|---|
| Kaggle — Dataset Batik Indonesia (on dev) | 20 kelas motif batik, ±150 gambar/kelas, sudah ada split train/val/test | CC0 | Cadangan kalau butuh split siap pakai |
| Roboflow — Motif Batik | 950 gambar beranotasi jenis batik | Public Domain | Kalau butuh anotasi kelas sekaligus |
| PDKI (pdki-indonesia.dgip.go.id) | Desain industri terdaftar resmi | Data publik pemerintah, akses manual per-item (bukan bulk/API) | Kurasi manual puluhan contoh "ground truth" desain yang sudah resmi terdaftar |

Untuk kategori **tenun/kriya non-batik**, tidak ditemukan dataset publik siap-download yang setara — yang ada hanya dataset internal di beberapa paper akademik (misal riset klasifikasi motif tenun Flores/Sikka-Ende-Nagekeo-Manggarai) yang harus diminta langsung ke penulis, tanpa garansi respons. Implikasinya: **cakupan MVP realistis difokuskan ke batik dulu** memakai dataset HuggingFace di atas, tenun/kriya lain masuk roadmap V1 setelah ada kemitraan data.

**⚠️ Catatan kritis — provenance & lisensi data (wajib dibahas di pitch):**

Sebagian besar dataset batik publik di atas awalnya dikumpulkan lewat *image scraping* dari Google Image, Bing, atau Instagram — artinya status hak cipta gambar sumber aslinya sendiri ambigu. Ini berisiko jadi celah kritik langsung dari juri: sebuah alat cek-orisinalitas yang index referensinya dibangun dari data yang provenance hak ciptanya sendiri tidak jelas adalah kontradiksi yang harus diantisipasi, bukan disembunyikan.

Mitigasi yang harus masuk ke pitch:
- **Untuk demo/hackathon:** dataset di atas dipakai eksplisit sebagai *"dataset riset non-komersial untuk proof-of-concept"*, bukan diklaim sebagai index produksi final.
- **Untuk roadmap V1 (lihat section 11):** strategi data yang defensible secara hukum dan lebih kredibel di depan juri adalah index dibangun dari kombinasi:
  1. Foto yang di-*submit* sendiri oleh pengrajin/UMKM secara opt-in (mereka pemilik hak atas foto sendiri) — sekaligus jadi mekanisme "pendaftaran mandiri" desain ke sistem.
  2. Koleksi warisan budaya yang sudah berstatus domain publik (misal koleksi Museum Tekstil Jakarta yang sedang didigitalkan lewat inisiatif Jakarta Digital Collections/KoleksiKita, dan koleksi yang sudah dipublikasikan via Google Arts & Culture).
  3. Data desain industri resmi dari PDKI sebagai referensi "desain yang sudah terdaftar sah".
- Tidak perlu dataset besar untuk membuktikan konsep — kualitas kurasi dan kejelasan provenance lebih penting daripada kuantitas di tahap demo.

---

## 8. UI/UX Design Direction

**Prinsip dasar:** ini alat verifikasi, bukan landing page promosi. Nuansanya harus terasa presisi dan dapat dipercaya (trustworthy), bukan playful atau generik seperti kebanyakan produk "AI wrapper". Hindari pola yang langsung terlihat template AI: background krem hangat + serif besar + aksen terracotta; kartu-kartu seragam dengan shadow lembut yang sama; label ALL-CAPS di atas tiap heading; ikon panah "→" di tiap tombol.

### 8.1 Token System

**Warna (base palette, 5 warna bernama):**
| Nama | Hex | Peran |
|---|---|---|
| Paper | `#F7F6F3` | Background utama, netral, tidak krem hangat |
| Ink | `#1A1A18` | Teks utama, hampir hitam tapi bukan `#000`/`#111` generik |
| Indigo Tarum | `#2B3A67` | Aksen utama — merujuk pewarna indigo alami pada tenun/batik tradisional, bukan terracotta/vermilion klise |
| Line Grey | `#D8D5CE` | Garis pembatas, border tipis (bukan shadow) |
| Signal Amber | `#B8843A` | Satu-satunya warna untuk status "perlu ditinjau" — dipakai sangat terbatas, bukan dekorasi |

Skor risiko memakai gradasi Indigo Tarum (rendah) → Signal Amber (menengah) → Ink solid dengan border tebal (tinggi) — bukan traffic-light hijau-kuning-merah yang klise.

**Tipografi:**
- Judul & UI label: **Inter Tight** atau **General Sans** (grotesk modern, netral, tidak berkesan "AI generated" seperti pasangan serif-display + sans yang jadi default).
- Data/skor kemiripan: **IBM Plex Mono** — dipakai khusus untuk angka persentase dan metadata teknis, memberi kesan "instrumen pengukuran" yang sesuai dengan fungsi alat ini sebagai alat cek/verifikasi.
- Tidak ada penggunaan huruf kapital semua untuk label. Hierarki dibangun lewat ukuran dan weight, bukan case.

**Layout:**
- Split asimetris, bukan grid kartu seragam: panel kiri (40%) untuk upload/input, panel kanan (60%) untuk hasil — karena hasil (gambar pembanding + skor) adalah konten yang paling butuh ruang visual.
- Pembatas antar panel: garis tipis 1px (`Line Grey`), bukan shadow atau card border-radius seragam.
- Skor kemiripan ditampilkan besar dalam mono font di kanan atas panel hasil — elemen paling "berani" di halaman ini, sisanya tenang dan disiplin.
- Latar belakang boleh punya tekstur sangat halus garis-garis tipis menyilang (referensi pola tenun/anyaman) di area kosong — dekorasi minimal yang terhubung langsung ke subject matter (kriya/tekstil), bukan gradient abstrak generik.

ASCII wireframe kasar:
```
┌──────────────────────┬─────────────────────────────────┐
│  UPLOAD DESAIN        │  HASIL PENGECEKAN                │
│                        │                                   │
│  [drop zone]           │              87%  ← mono, besar   │
│                        │        "Sangat Mirip"             │
│  [pilih kategori ▾]    │                                   │
│                        │  ┌────┐ ┌────┐ ┌────┐            │
│  [Cek Sekarang]        │  │img │ │img │ │img │  pembanding │
│                        │  └────┘ └────┘ └────┘            │
│  disclaimer teks kecil │                                   │
│  (selalu terlihat)     │  Rekomendasi: [teks kontekstual]  │
└──────────────────────┴─────────────────────────────────┘
```

**Motion:**
- Satu momen animasi saja: transisi saat hasil muncul (skor fade-in dengan sedikit count-up angka dari 0 ke skor final) — bukan fade-slide-up di setiap elemen.
- Tidak ada hover effect dekoratif di kartu gambar pembanding; cukup outline saat difokus (accessibility).

### 8.2 Voice & Copy
- Bahasa Indonesia, aktif, langsung ke sasaran. Contoh tombol: "Cek Sekarang" bukan "Submit" atau "Analisis".
- Hasil ditulis dari sudut pandang pengguna: "Desainmu 87% mirip dengan produk ini" — bukan "Similarity score: 0.87".
- Disclaimer ditulis jelas tanpa nada minta maaf berlebihan: "Ini bukan opini hukum. Hasil ini membantu kamu memutuskan langkah berikutnya, bukan menggantikan konsultasi HKI resmi."

---

## 9. Success Metrics & Indikator Keberhasilan

| Metrik / Indikator | Target MVP / Validasi Pilot Datik Batik |
|---|---|
| **Kecepatan Proses (Latency)** | Ekstraksi embedding & pencarian kemiripan selesai dalam **< 5 detik** per gambar |
| **Cakupan Indeks Referensi** | **100% dari 2.599 motif Batik Indonesia** (38 kelas motif nusantara) terindeks aktif di FAISS |
| **Efisiensi Biaya Validasi Awal** | Menekan biaya skrining awal dari Rp 2.000.000+ (konsultan HKI swasta) menjadi **Rp 0 (100% mandiri)** |
| **Akurasi Kualitatif Pembanding** | Top-5 hasil pembanding relevan pada ≥ 85% kasus uji motif kriya/batik |
| **Kejelasan Alur & Adopsi Pengguna** | 100% perajin Datik Batik mampu menyelesaikan alur pengecekan dalam **≤ 3 langkah** tanpa bantuan teknis |
| **Nir-Sengketa (Zero Dispute)** | **0 kasus sengketa atau penolakan pendaftaran HKI** atas motif baru yang telah diverifikasi berisiko rendah oleh Tarum |
| **Pemahaman Disclaimer Legal** | Pengguna paham bahwa Tarum adalah alat bantu screening awal (bukan vonis pengadilan) setelah 1x pemakaian |

---

## 10. Risks & Assumptions

| Risiko | Mitigasi |
|---|---|
| Similarity score disalahartikan sebagai vonis hukum | Copy disclaimer wajib dibaca + framing hasil sebagai "rekomendasi tindak lanjut", bukan "putusan" |
| Dataset referensi kecil → hasil tidak representatif | Jujur di pitch: MVP adalah proof-of-concept, roadmap scaling butuh kemitraan data |
| Model CLIP general-purpose kurang sensitif ke detail motif tekstil halus | Fine-tuning ringan jadi item roadmap V2, bukan blocker MVP |
| Kekhawatiran privasi (upload desain belum dirilis ke publik) | Nyatakan kebijakan retensi data secara eksplisit di UI, opsi hapus data setelah sesi |

---

## 11. Roadmap Ringkas

- **V0 (Hackathon/Demo):** Upload → embedding → similarity search → hasil statis dengan dataset kurasi manual. Fokus ke Product & Innovation dari rubrik penilaian.
- **V1 (Pasca-hackathon):** Riwayat pengguna, kategori produk, integrasi link resmi PDKI, dataset lebih besar via kemitraan.
- **V2:** Fine-tuning model untuk sensitivitas motif tekstil, explainability visual (area gambar yang mirip), kemitraan dengan dinas koperasi/asosiasi kriya untuk distribusi.

---

## 12. Referensi
- Sistem pencarian HKI resmi: https://pdki-indonesia.dgip.go.id