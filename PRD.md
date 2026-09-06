# PRD: Cek Orisinalitas — Visual IP Checker untuk Pelaku Kriya & Fashion

**Versi:** 0.1 (Draft untuk submission EKRAF x Google Career Certificates)
**Status:** Draft
**Owner:** [Nama Tim]
**Terakhir diperbarui:** 6 September 2026

---

## 1. Ringkasan Eksekutif

Cek Orisinalitas adalah alat berbasis image-similarity search yang membantu pelaku UMKM kriya dan fashion mengecek apakah desain produk mereka (motif, pola, bentuk) sudah terlalu mirip dengan karya yang sudah ada di pasar atau database budaya publik — sebelum mereka mendaftarkan Hak Kekayaan Intelektual (HKI) atau merilis produk ke marketplace.

Ini bukan pengganti jasa hukum HKI. Ini adalah **alat screening awal** yang murah, cepat, dan dapat diakses pelaku usaha mikro yang selama ini tidak punya cara praktis untuk cek kemiripan visual — karena sistem resmi (PDKI/DJKI) hanya mendukung pencarian berbasis kata kunci teks, bukan kemiripan gambar.

---

## 2. Problem Statement

### 2.1 Masalah Inti
Pelaku UMKM kriya (batik, tenun, kerajinan) dan fashion menghadapi dua risiko yang berlawanan arah tapi berakar dari masalah yang sama — **tidak ada cara mudah untuk mengecek kemiripan visual desain**:

1. **Risiko sebagai peniru (tidak sengaja):** Desainer UMKM membuat motif/produk yang ternyata sangat mirip karya pihak lain, lalu gagal saat mendaftar HKI, atau kena somasi setelah produk terlanjur diproduksi massal.
2. **Risiko sebagai korban:** Karya asli mereka ditiru pihak lain sebelum sempat didaftarkan, dan mereka tidak tahu cara mendeteksi maupun membuktikannya.

### 2.2 Kenapa Masalah Ini Valid (Evidence)
- Sistem pencarian resmi DJKI (PDKI) hanya mendukung pencarian berbasis kata kunci/nama karya, bukan kemiripan visual — sehingga motif yang mirip secara visual tapi diberi nama berbeda tidak akan terdeteksi lewat pencarian manual.
- Tools plagiarism-checker yang sudah beredar luas (Quetext, ZeroGPT, Plag.id, dll) seluruhnya dirancang untuk teks, bukan gambar/motif — celah ini belum digarap untuk kebutuhan produk fisik/kriya.
- Riset IBM mencatat kesenjangan strategi digital antara UMKM dan korporasi besar, dengan literasi digital dan talenta teknis sebagai hambatan utama — pelaku kriya kecil jelas tidak punya akses ke jasa cek HKI profesional yang berbayar mahal.

### 2.3 Siapa yang Terdampak
- **Primer:** Pelaku UMKM kriya & fashion skala mikro-kecil (pengrajin batik/tenun independen, brand fashion lokal, reseller produk kriya).
- **Sekunder:** Konsultan HKI, dinas koperasi/UMKM daerah, komunitas ekraf yang mendampingi pelaku usaha sebelum pendaftaran merek/desain industri.

---

## 3. Goals & Non-Goals

### 3.1 Goals (untuk MVP hackathon)
- G1: User bisa upload 1 foto desain/produk dan mendapatkan skor kemiripan terhadap dataset referensi dalam < 10 detik.
- G2: Sistem menampilkan gambar pembanding paling mirip beserta skornya, bukan hanya angka mentah.
- G3: Sistem memberi rekomendasi tindak lanjut yang jelas dan bertanggung jawab (bukan vonis hukum).
- G4: Alur pakai cukup sederhana untuk pengguna dengan literasi digital dasar-menengah (maks 3 langkah dari upload sampai hasil).

### 3.2 Non-Goals (secara eksplisit di luar cakupan MVP)
- Bukan pengganti pendaftaran HKI resmi atau opini hukum — sistem tidak boleh mengklaim "aman secara hukum" atau "melanggar hukum".
- Bukan pendeteksi plagiarisme teks, merek dagang (nama), atau audio/musik.
- Bukan alat generative AI untuk membuat desain baru.
- Tidak menangani proses pendaftaran HKI end-to-end (cukup memberi link/panduan ke DJKI).

---

## 4. User Personas

| Persona | Deskripsi | Kebutuhan Utama |
|---|---|---|
| **Bu Rina, Pengrajin Batik Tulis** | Usaha rumahan, 5 tahun berjalan, belum pernah daftar HKI, minim literasi digital | Cara cepat & murah cek apakah motif barunya "aman" sebelum diproduksi |
| **Kevin, Founder Brand Fashion Lokal** | Startup fashion kecil, sudah jualan di marketplace, agak melek teknologi | Bukti awal untuk memperkuat kasus jika mau somasi pihak yang meniru produknya |
| **Pendamping UMKM Dinas Koperasi** | Memfasilitasi banyak UMKM sekaligus | Alat yang bisa direkomendasikan massal ke binaan tanpa training rumit |

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
- Embedding: `sentence-transformers` dengan model `clip-ViT-B-32` (gratis, jalan di CPU, tidak butuh GPU untuk skala demo).
- Vector index: FAISS (in-memory, gratis) untuk demo; Supabase pgvector (tier gratis) kalau butuh persistence.
- Backend: FastAPI, deploy di Render/Railway free tier.
- Frontend: React + Vite atau Next.js, deploy di Vercel free tier.
- Storage gambar: Supabase Storage atau Cloudflare R2 (free tier).

**Contoh inti pipeline (bukan production-ready, ilustrasi alur):**
```python
from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer('clip-ViT-B-32')

# Index dibangun sekali dari dataset referensi
reference_embeddings = model.encode(reference_images)
index = faiss.IndexFlatL2(reference_embeddings.shape[1])
index.add(reference_embeddings)

# Saat user upload gambar baru
query_embedding = model.encode([uploaded_image])
distances, indices = index.search(query_embedding, k=5)
# -> mapping distance ke skor kemiripan (0-100%) + ambil metadata gambar pembanding
```

### 7.1 Data Requirements
- Dataset referensi MVP: 300–1000 gambar kurasi manual dari kategori kriya/fashion yang relevan (scraping ringan dari marketplace kategori kriya + dataset motif budaya publik yang tersedia untuk riset).
- Tidak perlu dataset besar untuk membuktikan konsep — kualitas kurasi lebih penting daripada kuantitas di tahap demo.
- Untuk versi pasca-hackathon: perlu strategi kemitraan data (asosiasi kriya, dinas koperasi, atau DJKI) untuk scale.

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

## 9. Success Metrics

| Metrik | Target MVP/Demo |
|---|---|
| Waktu proses upload → hasil | < 10 detik |
| Akurasi kualitatif (validasi manual tim) | Top-5 hasil relevan pada ≥ 80% kasus uji |
| Kejelasan alur (usability test internal) | User baru bisa selesai 1 pengecekan tanpa panduan dalam < 2 menit |
| Pemahaman disclaimer | User paham status hukum alat ini setelah 1x pemakaian (validasi lewat wawancara singkat) |

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