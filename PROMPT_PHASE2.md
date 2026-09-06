Sekarang kerjakan frontend untuk project Tarum berdasarkan [PRD](PRD.md).

WAJIB ikuti persis token system di section 8.1 PRD ini — jangan pakai default styling-mu sendiri:
- Palet warna: Paper #F7F6F3, Ink #1A1A18, Indigo Tarum #2B3A67, Line Grey #D8D5CE, 
  Signal Amber #B8843A (baca deskripsi peran tiap warna di PRD, jangan asal pakai)
- Tipografi: Inter Tight/General Sans untuk UI, IBM Plex Mono KHUSUS untuk angka skor
- Layout: split asimetris 40/60 (upload kiri, hasil kanan) — BUKAN kartu-kartu seragam 
  dengan shadow, BUKAN centered single-column layout
- Ikuti wireframe ASCII di section 8.1 sebagai referensi struktur

HINDARI SECARA EKSPLISIT (ini generic AI design tells yang HARUS dihindari):
- Border-radius seragam di semua elemen
- Shadow lembut generik (rgba(0,0,0,.1)) di bawah setiap card
- Label ALL-CAPS di atas heading
- Ikon panah "→" di tombol
- Gradient dekoratif tanpa makna

Copy/microcopy ikuti section 8.2 — bahasa aktif, dari sudut pandang user, disclaimer 
hukum harus selalu terlihat (tidak collapsible/dismissible).

Hubungkan ke endpoint POST /check dari backend Fase 1.

Setelah selesai, screenshot hasilnya kalau environment kamu bisa, dan kritisi sendiri: 
bagian mana yang masih terasa seperti default template AI?