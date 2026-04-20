import csv
import random
import os
from datetime import datetime, timedelta

random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "structured")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROVINSI_KOTA = {
    "DKI Jakarta": ["Jakarta Pusat", "Jakarta Selatan", "Jakarta Barat", "Jakarta Utara", "Jakarta Timur"],
    "Jawa Barat": ["Bandung", "Bekasi", "Depok", "Bogor", "Cirebon", "Tasikmalaya"],
    "Jawa Tengah": ["Semarang", "Solo", "Yogyakarta", "Purwokerto", "Magelang"],
    "Jawa Timur": ["Surabaya", "Malang", "Sidoarjo", "Kediri", "Jember"],
    "Bali": ["Denpasar", "Badung", "Gianyar"],
    "Sumatera Utara": ["Medan", "Binjai", "Pematang Siantar"],
    "Sumatera Selatan": ["Palembang", "Prabumulih"],
    "Kalimantan Timur": ["Balikpapan", "Samarinda"],
    "Sulawesi Selatan": ["Makassar", "Pare-Pare"],
    "Banten": ["Tangerang", "Tangerang Selatan", "Serang", "Cilegon"],
}

REGION_MAP = {
    "DKI Jakarta": "Region Jakarta",
    "Jawa Barat": "Region Jawa Barat",
    "Jawa Tengah": "Region Jawa Tengah",
    "Jawa Timur": "Region Jawa Timur",
    "Bali": "Region Bali Nusra",
    "Sumatera Utara": "Region Sumatera",
    "Sumatera Selatan": "Region Sumatera",
    "Kalimantan Timur": "Region Kalimantan",
    "Sulawesi Selatan": "Region Sulawesi",
    "Banten": "Region Jakarta",
}

NAMA_DEPAN = ["Ahmad", "Budi", "Cahya", "Dewi", "Eko", "Fajar", "Gita", "Hadi", "Indra", "Joko",
    "Kartika", "Lestari", "Mega", "Nuri", "Omar", "Putri", "Rahmat", "Siti", "Tari", "Umar",
    "Vina", "Wahyu", "Yanti", "Zahra", "Andi", "Bambang", "Citra", "Dian", "Fitri", "Galih",
    "Hendra", "Irwan", "Joni", "Kurnia", "Linda", "Mira", "Nanda", "Oki", "Pandu", "Rina",
    "Surya", "Tri", "Utami", "Wawan", "Yusuf", "Agus", "Bayu", "Candra", "Desi", "Erna"]

NAMA_BELAKANG = ["Pratama", "Wijaya", "Sari", "Hidayat", "Nugroho", "Santoso", "Rahayu", "Putra",
    "Wibowo", "Handoko", "Setiawan", "Kurniawan", "Saputra", "Lestari", "Utami", "Purnama",
    "Kusuma", "Hartono", "Suryadi", "Permana", "Susanto", "Gunawan", "Siregar", "Harahap",
    "Nasution", "Hutapea", "Sirait", "Panjaitan", "Situmorang", "Manurung", "Lubis", "Simbolon",
    "Sinaga", "Siagian", "Tampubolon", "Aritonang", "Pasaribu", "Purba", "Simanjuntak", "Hutabarat"]

SEGMEN = ["Retail", "Retail", "Retail", "Retail", "Priority", "Priority", "SME", "SME", "Corporate", "Private Banking"]
JENIS_KELAMIN = ["Laki-laki", "Perempuan"]


def gen_nik(provinsi_idx, kota_idx, birth):
    area = f"{provinsi_idx:02d}{kota_idx:02d}{random.randint(1,9):02d}"
    tgl = f"{birth.day:02d}{birth.month:02d}{str(birth.year)[2:]}"
    seq = f"{random.randint(1,9999):04d}"
    return area + tgl + seq


def gen_phone():
    prefix = random.choice(["0812", "0813", "0857", "0858", "0878", "0877", "0821", "0822", "0852", "0853"])
    return prefix + f"{random.randint(10000000,99999999)}"


def create_dim_cabang():
    rows = []
    cabang_id = 1
    tipe_options = ["KC", "KC", "KCP", "KCP", "KCP", "KK"]
    for prov, kotas in PROVINSI_KOTA.items():
        for kota in kotas:
            n = random.randint(1, 3)
            for i in range(n):
                tipe = random.choice(tipe_options)
                nama = f"Bank Nusantara {tipe} {kota}" + (f" {i+1}" if i > 0 else "")
                rows.append({
                    "cabang_id": f"CAB{cabang_id:04d}",
                    "nama_cabang": nama,
                    "kota": kota,
                    "provinsi": prov,
                    "region": REGION_MAP[prov],
                    "tipe_cabang": tipe,
                    "jumlah_karyawan": random.randint(8, 120) if tipe == "KC" else random.randint(5, 30),
                    "tanggal_berdiri": (datetime(2000, 1, 1) + timedelta(days=random.randint(0, 8000))).strftime("%Y-%m-%d"),
                    "status_aktif": random.choice(["Aktif"] * 19 + ["Tidak Aktif"]),
                })
                cabang_id += 1
    with open(os.path.join(OUTPUT_DIR, "dim_cabang.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Created: dim_cabang.csv ({len(rows)} rows)")
    return [r["cabang_id"] for r in rows if r["status_aktif"] == "Aktif"]


def create_dim_nasabah(cabang_ids, n=10000):
    rows = []
    for i in range(1, n + 1):
        birth = datetime(1960, 1, 1) + timedelta(days=random.randint(0, 20000))
        prov_idx = random.randint(1, 34)
        kota_idx = random.randint(1, 15)
        nama = random.choice(NAMA_DEPAN) + " " + random.choice(NAMA_BELAKANG)
        segmen = random.choice(SEGMEN)
        tgl_buka = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 5500))
        rows.append({
            "nasabah_id": f"NSB{i:07d}",
            "nama_lengkap": nama,
            "nik": gen_nik(prov_idx, kota_idx, birth),
            "no_hp": gen_phone(),
            "email": f"{nama.lower().replace(' ','.')}_{i}@email.com",
            "tanggal_lahir": birth.strftime("%Y-%m-%d"),
            "jenis_kelamin": random.choice(JENIS_KELAMIN),
            "segmen_nasabah": segmen,
            "cabang_id": random.choice(cabang_ids),
            "tanggal_buka_rekening": tgl_buka.strftime("%Y-%m-%d"),
            "status_aktif": random.choice(["Aktif"] * 9 + ["Tidak Aktif"]),
            "pekerjaan": random.choice(["PNS", "Karyawan Swasta", "Wiraswasta", "Profesional", "Ibu Rumah Tangga", "Pensiunan", "Mahasiswa", "Petani", "Nelayan", "TNI/Polri"]),
            "penghasilan_bulanan": random.choice([3000000, 5000000, 7500000, 10000000, 15000000, 20000000, 30000000, 50000000, 75000000, 100000000]),
        })
    with open(os.path.join(OUTPUT_DIR, "dim_nasabah.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Created: dim_nasabah.csv ({len(rows)} rows)")
    return [r["nasabah_id"] for r in rows]


def create_fact_transaksi(nasabah_ids, n=100000):
    jenis = ["Transfer", "Transfer", "Transfer", "Tarik Tunai", "Setor Tunai", "Pembayaran Tagihan", "Top Up e-Wallet", "Pembelian", "QRIS Payment"]
    channel = ["Mobile Banking", "Mobile Banking", "Mobile Banking", "ATM", "ATM", "Teller", "Internet Banking", "EDC", "QRIS"]
    rows = []
    for i in range(1, n + 1):
        j = random.choice(jenis)
        tgl = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 480), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        if j in ["Transfer", "Pembayaran Tagihan"]:
            jumlah = random.choice([50000, 100000, 250000, 500000, 1000000, 2500000, 5000000, 10000000, 25000000, 50000000])
        elif j == "Tarik Tunai":
            jumlah = random.choice([100000, 200000, 500000, 1000000, 2500000, 5000000])
        elif j == "Setor Tunai":
            jumlah = random.choice([500000, 1000000, 2000000, 5000000, 10000000, 25000000, 50000000])
        else:
            jumlah = random.randint(10000, 2000000)
        rows.append({
            "transaksi_id": f"TRX{i:09d}",
            "nasabah_id": random.choice(nasabah_ids),
            "tanggal_transaksi": tgl.strftime("%Y-%m-%d %H:%M:%S"),
            "jenis_transaksi": j,
            "jumlah": jumlah,
            "channel": random.choice(channel),
            "status": random.choice(["Berhasil"] * 19 + ["Gagal"]),
            "keterangan": f"Transaksi {j.lower()}"
        })
    with open(os.path.join(OUTPUT_DIR, "fact_transaksi.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Created: fact_transaksi.csv ({len(rows)} rows)")


def create_fact_kredit(nasabah_ids, n=5000):
    jenis_kredit = ["KPR", "KPR", "KKB", "Kredit Modal Kerja", "Kredit Investasi", "KUR Mikro", "KUR Kecil", "Kredit Multiguna", "Kartu Kredit"]
    status_kol = [("1-Lancar", 70), ("2-Dalam Perhatian Khusus", 12), ("3-Kurang Lancar", 8), ("4-Diragukan", 5), ("5-Macet", 5)]
    kol_choices = []
    for s, w in status_kol:
        kol_choices.extend([s] * w)
    rows = []
    for i in range(1, n + 1):
        jk = random.choice(jenis_kredit)
        if jk == "KPR":
            plafon = random.choice([200000000, 300000000, 500000000, 750000000, 1000000000, 1500000000])
            tenor = random.choice([120, 180, 240])
        elif jk == "KKB":
            plafon = random.choice([100000000, 150000000, 200000000, 300000000, 500000000])
            tenor = random.choice([36, 48, 60])
        elif jk == "KUR Mikro":
            plafon = random.choice([5000000, 10000000, 15000000, 20000000, 25000000])
            tenor = random.choice([12, 24, 36])
        elif jk == "KUR Kecil":
            plafon = random.choice([50000000, 100000000, 200000000, 300000000, 500000000])
            tenor = random.choice([36, 48, 60])
        else:
            plafon = random.choice([50000000, 100000000, 250000000, 500000000, 1000000000])
            tenor = random.choice([12, 24, 36, 48, 60])
        bunga = 6.0 if "KUR" in jk else random.choice([7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 12.0])
        tgl = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1900))
        outstanding = int(plafon * random.uniform(0.1, 0.95))
        rows.append({
            "kredit_id": f"KRD{i:06d}",
            "nasabah_id": random.choice(nasabah_ids),
            "jenis_kredit": jk,
            "jumlah_pinjaman": plafon,
            "outstanding": outstanding,
            "tenor_bulan": tenor,
            "suku_bunga_persen": bunga,
            "tanggal_pencairan": tgl.strftime("%Y-%m-%d"),
            "tanggal_jatuh_tempo": (tgl + timedelta(days=tenor * 30)).strftime("%Y-%m-%d"),
            "status_kolektibilitas": random.choice(kol_choices),
            "agunan": random.choice(["Sertifikat Tanah", "BPKB", "Deposito", "Mesin/Peralatan", "Personal Guarantee", "Tanpa Agunan"]),
            "sektor_ekonomi": random.choice(["Perdagangan", "Manufaktur", "Jasa", "Pertanian", "Perikanan", "Konstruksi", "Transportasi", "Properti", "F&B", "Retail"]),
        })
    with open(os.path.join(OUTPUT_DIR, "fact_kredit.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Created: fact_kredit.csv ({len(rows)} rows)")


def create_fact_simpanan(nasabah_ids, n=15000):
    jenis = ["Tabungan", "Tabungan", "Tabungan", "Tabungan", "Deposito", "Deposito", "Giro"]
    rows = []
    for i in range(1, n + 1):
        js = random.choice(jenis)
        if js == "Tabungan":
            saldo = random.choice([100000, 500000, 1000000, 5000000, 10000000, 25000000, 50000000, 100000000, 250000000])
            bunga = random.choice([0.5, 1.0, 1.5, 2.0])
        elif js == "Deposito":
            saldo = random.choice([10000000, 25000000, 50000000, 100000000, 250000000, 500000000, 1000000000])
            bunga = random.choice([3.5, 4.0, 4.5, 5.0, 5.5])
        else:
            saldo = random.choice([5000000, 10000000, 50000000, 100000000, 500000000, 1000000000])
            bunga = random.choice([0.25, 0.5, 1.0])
        tgl = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 3650))
        rows.append({
            "simpanan_id": f"SMP{i:07d}",
            "nasabah_id": random.choice(nasabah_ids),
            "jenis_simpanan": js,
            "saldo": saldo,
            "suku_bunga_persen": bunga,
            "tanggal_buka": tgl.strftime("%Y-%m-%d"),
            "mata_uang": random.choice(["IDR"] * 19 + ["USD"]),
            "status": random.choice(["Aktif"] * 9 + ["Ditutup"]),
        })
    with open(os.path.join(OUTPUT_DIR, "fact_simpanan.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Created: fact_simpanan.csv ({len(rows)} rows)")


if __name__ == "__main__":
    cabang_ids = create_dim_cabang()
    nasabah_ids = create_dim_nasabah(cabang_ids)
    create_fact_transaksi(nasabah_ids)
    create_fact_kredit(nasabah_ids)
    create_fact_simpanan(nasabah_ids)
    print("\nAll CSVs created successfully!")
