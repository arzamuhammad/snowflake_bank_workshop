CREATE OR REPLACE SEMANTIC VIEW BANK_DB.RAW_DATA.BANK_ANALYTICS_SV

  TABLES (
    NASABAH AS BANK_DB.RAW_DATA.DIM_NASABAH
      PRIMARY KEY (nasabah_id)
      WITH SYNONYMS = ('customer', 'nasabah')
      COMMENT = 'Data master nasabah bank termasuk informasi demografis dan segmentasi',

    CABANG AS BANK_DB.RAW_DATA.DIM_CABANG
      PRIMARY KEY (cabang_id)
      WITH SYNONYMS = ('branch', 'cabang')
      COMMENT = 'Data master cabang bank termasuk lokasi dan tipe cabang',

    TRANSAKSI AS BANK_DB.RAW_DATA.FACT_TRANSAKSI
      PRIMARY KEY (transaksi_id)
      WITH SYNONYMS = ('transaction', 'transaksi')
      COMMENT = 'Data transaksi harian nasabah',

    KREDIT AS BANK_DB.RAW_DATA.FACT_KREDIT
      PRIMARY KEY (kredit_id)
      WITH SYNONYMS = ('loan', 'kredit', 'pinjaman')
      COMMENT = 'Data portofolio kredit/pinjaman',

    SIMPANAN AS BANK_DB.RAW_DATA.FACT_SIMPANAN
      PRIMARY KEY (simpanan_id)
      WITH SYNONYMS = ('deposit', 'simpanan', 'DPK')
      COMMENT = 'Data simpanan nasabah (Dana Pihak Ketiga / DPK)'
  )

  RELATIONSHIPS (
    NASABAH_TO_CABANG AS
      NASABAH (cabang_id) REFERENCES CABANG (cabang_id),
    TRANSAKSI_TO_NASABAH AS
      TRANSAKSI (nasabah_id) REFERENCES NASABAH (nasabah_id),
    KREDIT_TO_NASABAH AS
      KREDIT (nasabah_id) REFERENCES NASABAH (nasabah_id),
    SIMPANAN_TO_NASABAH AS
      SIMPANAN (nasabah_id) REFERENCES NASABAH (nasabah_id)
  )

  FACTS (
    NASABAH.penghasilan_bulanan AS penghasilan_bulanan
      WITH SYNONYMS = ('gaji', 'income', 'pendapatan', 'salary')
      COMMENT = 'Penghasilan bulanan nasabah dalam Rupiah',

    TRANSAKSI.jumlah AS jumlah
      WITH SYNONYMS = ('amount', 'nominal', 'nilai transaksi')
      COMMENT = 'Nominal transaksi dalam Rupiah',

    KREDIT.jumlah_pinjaman AS jumlah_pinjaman
      WITH SYNONYMS = ('loan amount', 'plafon', 'principal')
      COMMENT = 'Total plafon kredit dalam Rupiah',

    KREDIT.outstanding AS outstanding
      WITH SYNONYMS = ('sisa pinjaman', 'remaining balance', 'baki debet')
      COMMENT = 'Sisa pokok pinjaman yang belum dibayar',

    KREDIT.tenor_bulan AS tenor_bulan
      WITH SYNONYMS = ('tenor', 'loan term', 'jangka waktu')
      COMMENT = 'Jangka waktu kredit dalam bulan',

    KREDIT.suku_bunga_persen AS suku_bunga_persen
      WITH SYNONYMS = ('interest rate', 'bunga', 'rate')
      COMMENT = 'Suku bunga kredit per tahun dalam persen',

    SIMPANAN.saldo AS saldo
      WITH SYNONYMS = ('balance', 'jumlah simpanan')
      COMMENT = 'Saldo simpanan saat ini dalam Rupiah',

    SIMPANAN.suku_bunga_persen AS suku_bunga_persen
      WITH SYNONYMS = ('interest rate', 'bunga simpanan')
      COMMENT = 'Suku bunga simpanan per tahun dalam persen',

    CABANG.jumlah_karyawan AS jumlah_karyawan
      COMMENT = 'Jumlah karyawan cabang'
  )

  DIMENSIONS (
    NASABAH.nasabah_id AS nasabah_id
      WITH SYNONYMS = ('customer id', 'id nasabah')
      COMMENT = 'ID unik nasabah',
    NASABAH.nama_lengkap AS nama_lengkap
      WITH SYNONYMS = ('nama', 'customer name')
      COMMENT = 'Nama lengkap nasabah',
    NASABAH.nik AS nik
      WITH SYNONYMS = ('KTP', 'nomor KTP', 'identitas')
      COMMENT = 'Nomor Induk Kependudukan',
    NASABAH.segmen_nasabah AS segmen_nasabah
      WITH SYNONYMS = ('segmen', 'segment', 'kategori nasabah')
      COMMENT = 'Segmen nasabah: Retail, Priority, SME, Corporate, Private Banking',
    NASABAH.cabang_id AS cabang_id
      COMMENT = 'ID cabang tempat nasabah terdaftar',
    NASABAH.tanggal_buka_rekening AS tanggal_buka_rekening
      WITH SYNONYMS = ('registration date', 'tanggal daftar')
      COMMENT = 'Tanggal pertama kali nasabah membuka rekening',
    NASABAH.status_aktif AS status_aktif
      WITH SYNONYMS = ('status', 'active status')
      COMMENT = 'Status nasabah: Aktif atau Tidak Aktif',
    NASABAH.pekerjaan AS pekerjaan
      WITH SYNONYMS = ('occupation', 'profesi', 'job')
      COMMENT = 'Pekerjaan nasabah',
    NASABAH.jenis_kelamin AS jenis_kelamin
      WITH SYNONYMS = ('gender', 'kelamin')
      COMMENT = 'Jenis kelamin',

    CABANG.cabang_id AS cabang_id
      WITH SYNONYMS = ('branch id', 'kode cabang')
      COMMENT = 'ID unik cabang',
    CABANG.nama_cabang AS nama_cabang
      WITH SYNONYMS = ('branch name')
      COMMENT = 'Nama lengkap cabang',
    CABANG.kota AS kota
      WITH SYNONYMS = ('city')
      COMMENT = 'Kota lokasi cabang',
    CABANG.provinsi AS provinsi
      WITH SYNONYMS = ('province', 'propinsi')
      COMMENT = 'Provinsi lokasi cabang',
    CABANG.region AS region
      WITH SYNONYMS = ('wilayah', 'area', 'regional')
      COMMENT = 'Region operasional cabang',
    CABANG.tipe_cabang AS tipe_cabang
      WITH SYNONYMS = ('branch type', 'jenis cabang')
      COMMENT = 'Tipe cabang: KC, KCP, KK',

    TRANSAKSI.transaksi_id AS transaksi_id
      WITH SYNONYMS = ('transaction id')
      COMMENT = 'ID unik transaksi',
    TRANSAKSI.nasabah_id AS nasabah_id
      COMMENT = 'ID nasabah yang melakukan transaksi',
    TRANSAKSI.tanggal_transaksi AS tanggal_transaksi
      WITH SYNONYMS = ('transaction date', 'waktu transaksi')
      COMMENT = 'Tanggal dan waktu transaksi',
    TRANSAKSI.jenis_transaksi AS jenis_transaksi
      WITH SYNONYMS = ('transaction type', 'tipe transaksi')
      COMMENT = 'Jenis transaksi: Transfer, Tarik Tunai, Setor Tunai, dll',
    TRANSAKSI.channel AS channel
      WITH SYNONYMS = ('kanal', 'media transaksi')
      COMMENT = 'Channel: Mobile Banking, ATM, Teller, Internet Banking, EDC, QRIS',
    TRANSAKSI.status AS status
      WITH SYNONYMS = ('transaction status')
      COMMENT = 'Status transaksi: Berhasil atau Gagal',

    KREDIT.kredit_id AS kredit_id
      WITH SYNONYMS = ('loan id')
      COMMENT = 'ID unik kredit',
    KREDIT.nasabah_id AS nasabah_id
      COMMENT = 'ID nasabah peminjam',
    KREDIT.jenis_kredit AS jenis_kredit
      WITH SYNONYMS = ('loan type', 'tipe kredit', 'produk kredit')
      COMMENT = 'Jenis produk kredit: KPR, KKB, KUR, dll',
    KREDIT.tanggal_pencairan AS tanggal_pencairan
      WITH SYNONYMS = ('disbursement date', 'tanggal cair')
      COMMENT = 'Tanggal kredit dicairkan',
    KREDIT.status_kolektibilitas AS status_kolektibilitas
      WITH SYNONYMS = ('collectibility', 'kualitas kredit', 'NPL status')
      COMMENT = 'Status kolektibilitas OJK: 1-Lancar, 2-DPK, 3-Kurang Lancar, 4-Diragukan, 5-Macet. NPL = kolektibilitas 3, 4, 5',
    KREDIT.agunan AS agunan
      WITH SYNONYMS = ('collateral', 'jaminan')
      COMMENT = 'Jenis agunan/jaminan kredit',
    KREDIT.sektor_ekonomi AS sektor_ekonomi
      WITH SYNONYMS = ('economic sector', 'sektor usaha')
      COMMENT = 'Sektor ekonomi usaha debitur',

    SIMPANAN.simpanan_id AS simpanan_id
      WITH SYNONYMS = ('deposit id')
      COMMENT = 'ID unik simpanan',
    SIMPANAN.nasabah_id AS nasabah_id
      COMMENT = 'ID nasabah pemilik simpanan',
    SIMPANAN.jenis_simpanan AS jenis_simpanan
      WITH SYNONYMS = ('deposit type', 'tipe simpanan')
      COMMENT = 'Jenis simpanan: Tabungan, Deposito, Giro (DPK)',
    SIMPANAN.tanggal_buka AS tanggal_buka
      WITH SYNONYMS = ('opening date')
      COMMENT = 'Tanggal pembukaan rekening simpanan',
    SIMPANAN.mata_uang AS mata_uang
      WITH SYNONYMS = ('currency', 'valas')
      COMMENT = 'Mata uang: IDR atau USD',
    SIMPANAN.status AS status
      WITH SYNONYMS = ('deposit status')
      COMMENT = 'Status simpanan: Aktif atau Ditutup'
  )

  METRICS (
    SIMPANAN.total_dpk AS SUM(CASE WHEN status = 'Aktif' THEN saldo ELSE 0 END)
      WITH SYNONYMS = ('total simpanan', 'total deposits', 'dana pihak ketiga', 'DPK')
      COMMENT = 'Total Dana Pihak Ketiga (DPK) - saldo simpanan aktif',

    KREDIT.total_outstanding_kredit AS SUM(outstanding)
      WITH SYNONYMS = ('total kredit', 'total loans', 'total pinjaman', 'baki debet')
      COMMENT = 'Total outstanding kredit - sisa pokok seluruh pinjaman',

    KREDIT.npl_amount AS SUM(CASE WHEN status_kolektibilitas IN ('3-Kurang Lancar', '4-Diragukan', '5-Macet') THEN outstanding ELSE 0 END)
      WITH SYNONYMS = ('kredit bermasalah', 'non performing loan', 'kredit macet')
      COMMENT = 'Total outstanding kredit bermasalah (NPL) - kolektibilitas 3, 4, 5',

    KREDIT.npl_ratio AS SUM(CASE WHEN status_kolektibilitas IN ('3-Kurang Lancar', '4-Diragukan', '5-Macet') THEN outstanding ELSE 0 END) * 100.0 / NULLIF(SUM(outstanding), 0)
      WITH SYNONYMS = ('rasio NPL', 'NPL rate', 'rasio kredit bermasalah')
      COMMENT = 'Rasio NPL (%) - sehat di bawah 5% sesuai OJK',

    NASABAH.jumlah_nasabah_aktif AS COUNT(CASE WHEN status_aktif = 'Aktif' THEN nasabah_id END)
      WITH SYNONYMS = ('total nasabah aktif', 'active customers')
      COMMENT = 'Jumlah nasabah dengan status aktif',

    TRANSAKSI.total_volume_transaksi AS SUM(CASE WHEN status = 'Berhasil' THEN jumlah ELSE 0 END)
      WITH SYNONYMS = ('volume transaksi', 'transaction volume')
      COMMENT = 'Total nilai/volume transaksi dalam Rupiah',

    TRANSAKSI.jumlah_transaksi AS COUNT(CASE WHEN status = 'Berhasil' THEN transaksi_id END)
      WITH SYNONYMS = ('count transaksi', 'transaction count', 'frekuensi transaksi')
      COMMENT = 'Total jumlah/count transaksi berhasil'
  )

  COMMENT = 'Semantic View untuk analisis data operasional Bank - mencakup nasabah, transaksi, kredit, dan simpanan';
