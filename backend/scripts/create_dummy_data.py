import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.config import REFERENCE_IMAGES_DIR


def create_batik_parang(output_path: Path):
    """Batik Parang: Motif garis diagonal parang / soga cokelat & krem."""
    img = Image.new("RGB", (400, 400), color=(240, 230, 210))
    draw = ImageDraw.Draw(img)
    # Garis-garis diagonal parang
    for offset in range(-400, 800, 40):
        draw.line([(offset, 0), (offset + 400, 400)], fill=(120, 65, 30), width=18)
        draw.line([(offset + 12, 0), (offset + 412, 400)], fill=(70, 35, 15), width=6)
        # Bentuk 'lidah' parang
        for y in range(20, 400, 50):
            x = offset + y
            draw.polygon([(x, y), (x + 20, y + 10), (x + 10, y + 25)], fill=(180, 130, 80))
    img.save(output_path, "JPEG", quality=95)


def create_batik_kawung(output_path: Path):
    """Batik Kawung: Lingkaran elips empat arah teratur, hitam & soga."""
    img = Image.new("RGB", (400, 400), color=(30, 25, 20))
    draw = ImageDraw.Draw(img)
    step = 80
    for cx in range(0, 480, step):
        for cy in range(0, 480, step):
            # 4 kelopak elips menyerupai buah kolang-kaling (kawung)
            draw.ellipse([cx - 35, cy - 15, cx + 35, cy + 15], fill=(195, 155, 100), outline=(240, 220, 180), width=2)
            draw.ellipse([cx - 15, cy - 35, cx + 15, cy + 35], fill=(195, 155, 100), outline=(240, 220, 180), width=2)
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(245, 235, 210))
    img.save(output_path, "JPEG", quality=95)


def create_tenun_ikat_sumba(output_path: Path):
    """Tenun Ikat Sumba: Pola pita horizontal etnik indigo, terakota, krem."""
    img = Image.new("RGB", (400, 400), color=(43, 58, 103))  # Indigo Tarum
    draw = ImageDraw.Draw(img)
    bands = [
        (40, 90, (184, 132, 58)),   # Amber / Terakota
        (130, 210, (230, 225, 215)), # Krem
        (250, 310, (150, 60, 45)),   # Merah bata
        (340, 380, (184, 132, 58)),  # Amber
    ]
    for y1, y2, color in bands:
        draw.rectangle([0, y1, 400, y2], fill=color)
        # Motif belah ketupat / zigzag ikat
        for x in range(0, 400, 30):
            mid_y = (y1 + y2) // 2
            draw.polygon([(x, mid_y), (x + 15, y1 + 5), (x + 30, mid_y), (x + 15, y2 - 5)], fill=(43, 58, 103))
    img.save(output_path, "JPEG", quality=95)


def create_tenun_songket(output_path: Path):
    """Tenun Songket: Benang emas geometris di atas merah marun."""
    img = Image.new("RGB", (400, 400), color=(110, 20, 30))
    draw = ImageDraw.Draw(img)
    for x in range(0, 400, 50):
        for y in range(0, 400, 50):
            # Belah ketupat emas
            draw.polygon([(x + 25, y), (x + 50, y + 25), (x + 25, y + 50), (x, y + 25)], outline=(225, 185, 75), width=3)
            draw.polygon([(x + 25, y + 12), (x + 38, y + 25), (x + 25, y + 38), (x + 12, y + 25)], fill=(215, 175, 65))
            draw.rectangle([x + 23, y + 23, x + 27, y + 27], fill=(255, 235, 150))
    img.save(output_path, "JPEG", quality=95)


def create_batik_megamendung(output_path: Path):
    """Batik Megamendung: Pola awan berlapis gradasi biru khas Cirebon."""
    img = Image.new("RGB", (400, 400), color=(20, 35, 75))
    draw = ImageDraw.Draw(img)
    colors = [
        (40, 70, 130),
        (65, 110, 180),
        (100, 160, 220),
        (160, 210, 245),
        (240, 248, 255),
    ]
    for row in range(4):
        base_y = row * 100 + 20
        for col in range(3):
            base_x = col * 150 - 30
            for idx, colr in enumerate(colors):
                w = 120 - idx * 18
                h = 65 - idx * 9
                draw.chord([base_x + idx * 8, base_y + idx * 4, base_x + w, base_y + h], 0, 180, fill=colr)
    img.save(output_path, "JPEG", quality=95)


def create_anyaman_rotan(output_path: Path):
    """Anyaman Rotan: Anyaman diagonal silang warna cokelat jerami & bambu."""
    img = Image.new("RGB", (400, 400), color=(215, 190, 145))
    draw = ImageDraw.Draw(img)
    for x in range(0, 400, 25):
        draw.line([(x, 0), (x, 400)], fill=(185, 155, 110), width=10)
    for y in range(0, 400, 25):
        draw.line([(0, y), (400, y)], fill=(160, 130, 90), width=10)
    # Bayangan tekstur anyam silang
    for i in range(0, 400, 50):
        for j in range(0, 400, 50):
            draw.rectangle([i, j, i + 25, j + 25], fill=(225, 205, 165))
    img.save(output_path, "JPEG", quality=95)


def create_ukiran_kayu_jepara(output_path: Path):
    """Ukiran Kayu Jepara: Relief sulur daun dan bunga pada kayu jati."""
    img = Image.new("RGB", (400, 400), color=(115, 65, 35))
    draw = ImageDraw.Draw(img)
    # Lingkaran konsentris sulur bunga
    for center in [(120, 120), (280, 280), (120, 280), (280, 120)]:
        cx, cy = center
        for r in range(70, 10, -15):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(175, 110, 65), width=4)
        draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(70, 35, 15))
        # Daun sulur melengkung
        draw.arc([cx - 80, cy - 80, cx + 80, cy + 80], 45, 225, fill=(195, 130, 80), width=6)
    img.save(output_path, "JPEG", quality=95)


def create_tas_kulit_etnik(output_path: Path):
    """Tas Kulit Tatah: Tekstur kulit samak cokelat dengan cap motif etnik."""
    img = Image.new("RGB", (400, 400), color=(90, 50, 30))
    draw = ImageDraw.Draw(img)
    for x in range(25, 400, 60):
        for y in range(25, 400, 60):
            draw.rectangle([x - 20, y - 20, x + 20, y + 20], outline=(60, 30, 15), width=3)
            draw.line([(x - 15, y), (x + 15, y)], fill=(130, 80, 50), width=2)
            draw.line([(x, y - 15), (x, y + 15)], fill=(130, 80, 50), width=2)
            draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(155, 100, 60))
    img.save(output_path, "JPEG", quality=95)


def create_kain_lurik(output_path: Path):
    """Kain Lurik Tradisional: Garis vertikal rapat warna hitam, krem, dan hijau botol."""
    img = Image.new("RGB", (400, 400), color=(25, 30, 25))
    draw = ImageDraw.Draw(img)
    stripe_colors = [
        (190, 175, 140),  # Krem
        (40, 75, 55),     # Hijau botol
        (130, 50, 40),    # Cokelat marun
        (220, 205, 170),  # Krem terang
    ]
    for x in range(0, 400, 8):
        c = stripe_colors[(x // 8) % len(stripe_colors)]
        draw.line([(x, 0), (x, 400)], fill=c, width=3)
    img.save(output_path, "JPEG", quality=95)


def create_batik_truntum(output_path: Path):
    """Batik Truntum: Pola bintang melati kecil teratur di atas latar gelap."""
    img = Image.new("RGB", (400, 400), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    for x in range(20, 400, 40):
        for y in range(20, 400, 40):
            # Kelopak bunga bintang 8 titik
            draw.line([(x - 10, y), (x + 10, y)], fill=(235, 220, 185), width=2)
            draw.line([(x, y - 10), (x, y + 10)], fill=(235, 220, 185), width=2)
            draw.line([(x - 7, y - 7), (x + 7, y + 7)], fill=(185, 150, 100), width=2)
            draw.line([(x - 7, y + 7), (x + 7, y - 7)], fill=(185, 150, 100), width=2)
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 245, 220))
    img.save(output_path, "JPEG", quality=95)


def create_fashion_outer_etnik(output_path: Path):
    """Fashion Outer Etnik Modern: Color-block modern navy, mustard, dan terakota."""
    img = Image.new("RGB", (400, 400), color=(43, 58, 103))  # Indigo Tarum
    draw = ImageDraw.Draw(img)
    draw.polygon([(0, 0), (220, 0), (140, 400), (0, 400)], fill=(184, 132, 58)) # Signal Amber
    draw.polygon([(220, 0), (400, 0), (400, 250), (290, 400), (140, 400)], fill=(170, 65, 45))
    draw.rectangle([200, 150, 360, 320], outline=(247, 246, 243), width=4)
    draw.line([(200, 150), (360, 320)], fill=(247, 246, 243), width=3)
    img.save(output_path, "JPEG", quality=95)


def create_selendang_batik_pekalongan(output_path: Path):
    """Batik Pesisir Pekalongan: Rangkaian bunga berwarna cerah merah muda & toska."""
    img = Image.new("RGB", (400, 400), color=(250, 245, 235))
    draw = ImageDraw.Draw(img)
    centers = [(100, 100), (300, 120), (180, 260), (320, 310)]
    for cx, cy in centers:
        # Kelopak bunga cerah
        for angle in range(0, 360, 45):
            rad = angle * 3.14159 / 180.0
            import math
            px = cx + int(35 * math.cos(rad))
            py = cy + int(35 * math.sin(rad))
            draw.ellipse([px - 14, py - 14, px + 14, py + 14], fill=(215, 60, 95), outline=(245, 180, 200))
        draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(245, 200, 50))
        # Daun toska
        draw.chord([cx + 20, cy + 20, cx + 70, cy + 50], 0, 180, fill=(35, 145, 130))
    img.save(output_path, "JPEG", quality=95)


GENERATORS = [
    ("batik_parang_01.jpg", "Batik Parang Rusak Klasik", "batik", "Motif parang diagonal soga cokelat tradisional Surakarta", create_batik_parang),
    ("batik_kawung_02.jpg", "Batik Kawung Empat Pola", "batik", "Motif elips empat arah beraturan buah kawung/kolang-kaling", create_batik_kawung),
    ("tenun_ikat_sumba_03.jpg", "Tenun Ikat Sumba Timur", "tenun", "Pola pita geometris tenun ikat pewarna alam indigo dan terakota", create_tenun_ikat_sumba),
    ("tenun_songket_palembang_04.jpg", "Tenun Songket Lepus Emas", "tenun", "Songket tenun benang emas khas Palembang berlatar marun", create_tenun_songket),
    ("batik_megamendung_05.jpg", "Batik Megamendung Cirebon", "batik", "Pola awan megamendung khas pesisir Cirebon gradasi biru", create_batik_megamendung),
    ("anyaman_rotan_lombok_06.jpg", "Anyaman Rotan Motif Selisih", "anyaman", "Pola silang anyaman rotan natural khas Lombok", create_anyaman_rotan),
    ("ukiran_kayu_jepara_07.jpg", "Relief Ukiran Kayu Jepara", "kerajinan", "Motif sulur daun dan bunga ukiran kayu jati Jepara", create_ukiran_kayu_jepara),
    ("tas_kulit_tatah_08.jpg", "Tas Kulit Tatah Manding", "fashion", "Pola cap tatah etnik geometris pada kulit nabati", create_tas_kulit_etnik),
    ("kain_lurik_yogyakarta_09.jpg", "Kain Lurik Garis Klasik", "tenun", "Garis vertikal rapat tradisional Yogyakarta", create_kain_lurik),
    ("batik_truntum_solo_10.jpg", "Batik Truntum Bintang Melati", "batik", "Motif truntum bunga melati bintang kecil berulang", create_batik_truntum),
    ("outer_tenun_modern_11.jpg", "Outer Etnik Geometris Modern", "fashion", "Desain blazer tenun asimetris color block kontemporer", create_fashion_outer_etnik),
    ("selendang_batik_pekalongan_12.jpg", "Selendang Batik Buketan Pekalongan", "batik", "Motif buketan bunga pesisiran cerah khas Pekalongan", create_selendang_batik_pekalongan),
]


def generate_all_dummy_images(target_dir: Path = REFERENCE_IMAGES_DIR):
    target_dir.mkdir(parents=True, exist_ok=True)
    metadata_list = []

    print(f"Generating {len(GENERATORS)} dummy reference images in: {target_dir}")
    for filename, title, category, desc, func in GENERATORS:
        out_path = target_dir / filename
        func(out_path)
        metadata_list.append({
            "filename": filename,
            "title": title,
            "category": category,
            "description": desc,
            "source": "dummy_dataset_curated",
        })
        print(f"  ✓ Created: {filename} ({title})")

    meta_path = target_dir / "raw_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2, ensure_ascii=False)
    print(f"Raw metadata saved to {meta_path}")


if __name__ == "__main__":
    generate_all_dummy_images()
