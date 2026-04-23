# Day 2 - Session 4: Accelerating with Cortex Code

## Workshop: Snowflake x Bank
### "From Zero to ML Model & Data Pipeline dengan Natural Language"

---

## Tujuan Session

Pada session ini, peserta akan menggunakan **Cortex Code di Snowsight** untuk mempercepat pekerjaan sehari-hari:

1. **Membangun ML Model** - Dari nol sampai model ter-register, hanya menggunakan natural language
2. **Membangun Data Pipeline** - Buat ETL pipeline lengkap dengan Dynamic Tables dan Tasks
3. **Advanced Use Cases** - Governance, debugging, documentation
4. **Hands-on Challenge** - Peserta membangun fraud detection model sendiri

**AHA Moment:** *"Barrier to entry untuk data engineering & ML di Snowflake jadi sangat rendah. Bahkan orang yang bukan engineer bisa mulai explore data dan build model."*

---

## Daftar Isi

- [Cara Mengakses Cortex Code di Snowsight](#cara-mengakses-cortex-code-di-snowsight)
- [Part 1: Warm-up - SQL Generation & Code Explanation](#part-1-warm-up---sql-generation--code-explanation)
- [Part 2: Membangun ML Model dengan Cortex Code](#part-2-membangun-ml-model-dengan-cortex-code)
- [Part 3: Membangun Data Pipeline dengan Cortex Code](#part-3-membangun-data-pipeline-dengan-cortex-code)
- [Part 4: Advanced Use Cases](#part-4-advanced-use-cases)
- [Part 5: Hands-on Challenge - Fraud Detection Model](#part-5-hands-on-challenge---fraud-detection-model)

---

## Pre-requisites

- Sudah menyelesaikan **Session 1-3** (database `BANK_NUSANTARA_DB` dan semua tabel sudah ada)
- Snowflake Trial Account (**Enterprise Edition** atau lebih tinggi)
- Cortex Code sudah aktif di Snowsight (biasanya sudah enabled by default)

---

## Cara Mengakses Cortex Code di Snowsight

### Di SQL Worksheet:
1. Buka **Snowsight** → **Projects** → **Worksheets**
2. Buat worksheet baru
3. Klik ikon **Cortex Code** (ikon AI/sparkle ✨) di toolbar, atau tekan `Cmd+Shift+Space` (Mac) / `Ctrl+Shift+Space` (Windows)
4. Ketik prompt dalam bahasa natural → Cortex Code akan generate SQL

### Di Notebook:
1. Buka **Snowsight** → **Projects** → **Notebooks**
2. Buat notebook baru
3. Di setiap cell, klik ikon Cortex Code atau gunakan shortcut
4. Cortex Code bisa generate SQL cell maupun Python cell

> **Tips:** Cortex Code memahami konteks database, schema, dan tabel yang sedang aktif. Pastikan sudah `USE DATABASE` dan `USE SCHEMA` yang benar.

---

## Part 1: Warm-up - SQL Generation & Code Explanation

> **Durasi:** ~15 menit
> **Tujuan:** Peserta familiar dengan Cortex Code interface dan kemampuan dasarnya

### Step 1.1: Setup Context

Buka SQL Worksheet baru dan jalankan:

```sql
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE BANK_WH;
USE DATABASE BANK_NUSANTARA_DB;
USE SCHEMA RAW_DATA;
```

---

### Step 1.2: Generate SQL dari Natural Language

Buka Cortex Code dan coba prompt-prompt berikut satu per satu. Perhatikan SQL yang dihasilkan.

#### Prompt 1 - Query Sederhana

```
Tampilkan 10 nasabah dengan penghasilan tertinggi beserta nama cabang mereka
```

> **Expected:** Cortex Code akan generate JOIN antara DIM_NASABAH dan DIM_CABANG, ORDER BY penghasilan_bulanan DESC, LIMIT 10

#### Prompt 2 - Agregasi

```
Hitung total saldo simpanan per jenis simpanan, urutkan dari yang terbesar
```

> **Expected:** GROUP BY jenis_simpanan dengan SUM(saldo)

#### Prompt 3 - Query Analitik Perbankan

```
Hitung NPL ratio per region cabang. NPL adalah kredit dengan status kolektibilitas 3, 4, atau 5. 
Tampilkan region, total kredit, kredit NPL, dan NPL ratio dalam persen.
```

> **Expected:** JOIN fact_kredit dengan dim_nasabah dan dim_cabang, CASE WHEN untuk NPL, GROUP BY region

#### Prompt 4 - Window Function

```
Untuk setiap nasabah, tampilkan transaksi terakhir mereka beserta ranking transaksi berdasarkan jumlah terbesar. 
Gunakan window function ROW_NUMBER.
```

> **Expected:** ROW_NUMBER() OVER (PARTITION BY nasabah_id ORDER BY tanggal_transaksi DESC)

---

### Step 1.3: Code Explanation

Copy-paste query kompleks ini ke worksheet, select semua, lalu minta Cortex Code jelaskan:

```sql
WITH kredit_summary AS (
    SELECT 
        dc.region,
        dc.kota,
        COUNT(DISTINCT fk.kredit_id) AS total_kredit,
        SUM(CASE WHEN fk.status_kolektibilitas LIKE '3%' 
                  OR fk.status_kolektibilitas LIKE '4%' 
                  OR fk.status_kolektibilitas LIKE '5%' 
             THEN 1 ELSE 0 END) AS kredit_npl,
        SUM(fk.outstanding) AS total_outstanding,
        SUM(CASE WHEN fk.status_kolektibilitas LIKE '3%' 
                  OR fk.status_kolektibilitas LIKE '4%' 
                  OR fk.status_kolektibilitas LIKE '5%' 
             THEN fk.outstanding ELSE 0 END) AS outstanding_npl
    FROM FACT_KREDIT fk
    JOIN DIM_NASABAH dn ON fk.nasabah_id = dn.nasabah_id
    JOIN DIM_CABANG dc ON dn.cabang_id = dc.cabang_id
    GROUP BY dc.region, dc.kota
)
SELECT 
    region,
    kota,
    total_kredit,
    kredit_npl,
    ROUND(kredit_npl * 100.0 / NULLIF(total_kredit, 0), 2) AS npl_ratio_persen,
    total_outstanding,
    outstanding_npl,
    ROUND(outstanding_npl * 100.0 / NULLIF(total_outstanding, 0), 2) AS npl_outstanding_ratio
FROM kredit_summary
ORDER BY npl_ratio_persen DESC;
```

#### Prompt untuk Explanation:

```
Jelaskan query ini step by step. Apa tujuannya dan bagaimana cara kerjanya?
```

---

### Step 1.4: Quick Fix - Debug Error

Sengaja buat query dengan error, lalu minta Cortex Code perbaiki:

```sql
-- Query ini punya beberapa error, paste dan minta CoCo fix
SELCT nama_lengkap, penghaslan_bulanan
FROM DIM_NSABAH
WERE status_aktif = 'Aktif'
ORDRE BY penghasilan_bulanan DES
LIMT 10;
```

#### Prompt:

```
Fix semua error di query SQL ini
```

> **Expected:** Cortex Code akan fix typo: SELECT, penghasilan_bulanan, DIM_NASABAH, WHERE, ORDER BY, DESC, LIMIT

---

## Part 2: Membangun ML Model dengan Cortex Code

> **Durasi:** ~30 menit
> **Tujuan:** Bangun customer churn prediction model dari nol menggunakan Cortex Code

### Overview

Kita akan membangun **Customer Churn Prediction Model** step by step, setiap langkah menggunakan Cortex Code. Use case ini berbeda dari Session 3 (credit scoring) agar peserta mendapat pengalaman baru.

---

### Step 2.1: Buat Notebook Baru

1. Buka **Snowsight** → **Projects** → **Notebooks**
2. Klik **+ Notebook**
3. Nama: `Churn_Prediction_CortexCode`
4. Database: `BANK_NUSANTARA_DB`
5. Schema: `RAW_DATA`
6. Warehouse: `BANK_WH`

---

### Step 2.2: Generate Synthetic Churn Data

Buka Cortex Code di notebook cell dan gunakan prompt berikut:

#### Prompt:

```
Buatkan SQL untuk membuat tabel CUSTOMER_CHURN_DATA di schema BANK_NUSANTARA_DB.RAW_DATA 
yang berisi data churn nasabah bank dengan kolom berikut:
- CUSTOMER_ID (VARCHAR) 
- TENURE_MONTHS (INT) - berapa lama jadi nasabah
- NUM_PRODUCTS (INT) - jumlah produk yang dimiliki (1-4)
- BALANCE (FLOAT) - saldo rata-rata
- NUM_TRANSACTIONS_LAST_3M (INT) - jumlah transaksi 3 bulan terakhir
- IS_ACTIVE_MEMBER (INT) - 0 atau 1
- CREDIT_SCORE (INT) - range 300-850
- ESTIMATED_SALARY (FLOAT) - estimasi gaji
- AGE (INT) - usia 18-70
- HAS_CREDIT_CARD (INT) - 0 atau 1
- HAS_MOBILE_BANKING (INT) - 0 atau 1
- NUM_COMPLAINTS (INT) - jumlah komplain 0-5
- CHURNED (INT) - target variable, 0 atau 1

Generate 5000 rows data sintetis menggunakan GENERATOR dan UNIFORM/NORMAL distribution. 
Buat churn rate sekitar 20%. 
Pastikan data realistis: nasabah dengan saldo rendah, banyak komplain, dan tidak aktif 
cenderung lebih sering churn.
```

> **Perhatikan:** Cortex Code akan generate SQL INSERT atau CREATE TABLE AS SELECT dengan GENERATOR()

---

### Step 2.3: Exploratory Data Analysis

#### Prompt:

```
Buatkan Python code untuk EDA pada tabel CUSTOMER_CHURN_DATA:
1. Tampilkan jumlah total rows dan distribusi churn (0 vs 1)
2. Hitung statistik deskriptif semua kolom numerik
3. Buat correlation matrix antara semua fitur numerik dan target CHURNED
4. Identifikasi top 5 fitur yang paling berkorelasi dengan CHURNED

Gunakan Snowpark session yang sudah ada (get_active_session), pandas, dan matplotlib.
```

---

### Step 2.4: Feature Engineering

#### Prompt:

```
Buatkan Python code untuk feature engineering pada data CUSTOMER_CHURN_DATA:

1. Buat fitur baru:
   - BALANCE_SALARY_RATIO = BALANCE / ESTIMATED_SALARY
   - PRODUCTS_PER_TENURE = NUM_PRODUCTS / TENURE_MONTHS
   - TRANSACTION_FREQUENCY = NUM_TRANSACTIONS_LAST_3M / 3
   - ENGAGEMENT_SCORE = (IS_ACTIVE_MEMBER * 2 + HAS_MOBILE_BANKING + HAS_CREDIT_CARD) / 4
   - COMPLAINT_RATE = NUM_COMPLAINTS / TENURE_MONTHS
   - IS_HIGH_VALUE = 1 jika BALANCE > 50000 dan NUM_PRODUCTS >= 2, else 0

2. Simpan hasilnya sebagai tabel CHURN_FEATURES di schema RAW_DATA

Gunakan Snowpark DataFrame operations, bukan pandas.
```

---

### Step 2.5: Train Model

#### Prompt:

```
Buatkan Python code untuk train XGBoost classifier untuk churn prediction:

1. Load data dari tabel CHURN_FEATURES menggunakan Snowpark
2. Pisahkan features dan target (CHURNED)
3. Split data 80% train, 20% test dengan stratify
4. Handle imbalanced data menggunakan scale_pos_weight
5. Train XGBoost dengan parameter:
   - n_estimators=200
   - max_depth=5
   - learning_rate=0.05
6. Evaluasi model: tampilkan AUC-ROC, classification report, dan confusion matrix
7. Plot ROC curve dan feature importance (top 10)

Gunakan get_active_session() untuk koneksi Snowpark.
```

---

### Step 2.6: Register ke Model Registry

#### Prompt:

```
Buatkan Python code untuk register model XGBoost churn prediction ke Snowflake Model Registry:

1. Buat schema ML_MODELS jika belum ada
2. Register model dengan nama CHURN_PREDICTION_MODEL versi V1
3. Gunakan sample_input_data dari training data (head 10 rows)
4. Set target_platforms ke WAREHOUSE agar bisa inference via SQL
5. Tambahkan metrics: auc_roc dan classification report
6. Tambahkan conda_dependencies: xgboost, scikit-learn
7. Setelah register, verifikasi dengan SHOW MODELS dan SHOW FUNCTIONS

Gunakan snowflake.ml.registry.Registry
```

---

### Step 2.7: Batch Inference via SQL

#### Prompt:

```
Buatkan SQL query untuk melakukan batch inference menggunakan model CHURN_PREDICTION_MODEL V1 
yang sudah di-register di BANK_NUSANTARA_DB.ML_MODELS.

1. Scoring semua customer dari tabel CHURN_FEATURES
2. Tampilkan CUSTOMER_ID, actual CHURNED, predicted churn, dan churn probability
3. Hanya tampilkan top 20 customer dengan probabilitas churn tertinggi
4. Gunakan syntax MODEL()!PREDICT() dan MODEL()!PREDICT_PROBA()
```

---

### Step 2.8: Model Explainability (SHAP)

#### Prompt:

```
Buatkan SQL query untuk mendapatkan SHAP explanation dari model CHURN_PREDICTION_MODEL V1.

Gunakan syntax:
WITH MV_ALIAS AS MODEL ... VERSION ...
SELECT ... FROM table, TABLE(MV_ALIAS!EXPLAIN(...))

Tampilkan 5 customer dengan churn probability tertinggi beserta SHAP values mereka.
Ini penting untuk regulatory compliance - kita harus bisa menjelaskan kenapa model 
memprediksi nasabah akan churn.
```

---

## Part 3: Membangun Data Pipeline dengan Cortex Code

> **Durasi:** ~20 menit
> **Tujuan:** Bangun ETL pipeline lengkap menggunakan Dynamic Tables dan Tasks

---

### Step 3.1: Buat Worksheet Baru

Buka SQL Worksheet baru, set context:

```sql
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE BANK_WH;
USE DATABASE BANK_NUSANTARA_DB;
USE SCHEMA ANALYTICS;
```

---

### Step 3.2: Staging Layer - Dynamic Tables

#### Prompt:

```
Buatkan Dynamic Table untuk staging layer yang membersihkan data dari RAW_DATA:

1. STG_NASABAH: 
   - Ambil dari RAW_DATA.DIM_NASABAH
   - Filter hanya nasabah dengan status_aktif = 'Aktif'
   - Tambahkan kolom USIA_TAHUN (datediff dari tanggal_lahir ke current_date)
   - Tambahkan kolom SEGMEN_GROUP: mapping segmen ke 3 kategori 
     (Retail/Priority → CONSUMER, Private Banking → HIGH_NET_WORTH, SME/Corporate → BUSINESS)
   - Target lag: 1 hour

2. STG_TRANSAKSI:
   - Ambil dari RAW_DATA.FACT_TRANSAKSI
   - Filter hanya transaksi dengan status = 'Berhasil'
   - Tambahkan kolom IS_DIGITAL (1 jika channel = Mobile Banking/Internet Banking/QRIS, 0 lainnya)
   - Tambahkan kolom TANGGAL_DATE (cast tanggal_transaksi ke DATE)
   - Target lag: 1 hour
```

> **Expected:** Cortex Code generate `CREATE OR REPLACE DYNAMIC TABLE ... TARGET_LAG = '1 hour' AS SELECT ...`

---

### Step 3.3: Business Layer - Aggregated Metrics

#### Prompt:

```
Buatkan Dynamic Table untuk business metrics layer di schema ANALYTICS:

1. BIZ_NASABAH_360:
   - Gabungkan data dari STG_NASABAH, RAW_DATA.FACT_SIMPANAN, RAW_DATA.FACT_KREDIT, STG_TRANSAKSI
   - Per nasabah, hitung:
     * total_simpanan (SUM saldo dari simpanan aktif)
     * total_outstanding_kredit (SUM outstanding dari kredit)
     * jumlah_produk_simpanan (COUNT simpanan aktif)
     * jumlah_produk_kredit (COUNT kredit)
     * total_transaksi_30d (COUNT transaksi 30 hari terakhir)
     * avg_transaksi_30d (AVG jumlah transaksi 30 hari terakhir)
     * digital_ratio (rasio transaksi digital vs total)
     * is_npl (1 jika ada kredit kolektibilitas 3/4/5)
   - Target lag: downstream (mengikuti tabel sumber)

2. BIZ_CABANG_PERFORMANCE:
   - Per cabang, hitung:
     * total_nasabah_aktif
     * total_dpk (Dana Pihak Ketiga = SUM semua simpanan)
     * total_kredit_outstanding
     * npl_ratio
     * avg_transaksi_per_nasabah
   - Target lag: downstream
```

---

### Step 3.4: Automated Alert dengan Task

#### Prompt:

```
Buatkan Snowflake Task untuk alerting otomatis:

1. TASK_NPL_ALERT:
   - Jadwal: setiap hari jam 8 pagi (CRON: 0 8 * * *)
   - Warehouse: BANK_WH
   - Logika: Cek jika ada cabang dengan NPL ratio > 5%
   - Jika ada, INSERT ke tabel ALERT_LOG (alert_id, alert_type, cabang_id, region, 
     npl_ratio, message, created_at)
   - Buat juga tabel ALERT_LOG nya

2. TASK_DAILY_SUMMARY:
   - Jadwal: setiap hari jam 7 pagi
   - Logika: Hitung summary harian dan INSERT ke tabel DAILY_METRICS_LOG
   - Metrics: total_transaksi_hari_ini, total_volume, total_nasabah_baru, 
     top_channel, avg_transaksi_amount
   - Buat juga tabel DAILY_METRICS_LOG nya
```

---

### Step 3.5: Monitoring Pipeline

#### Prompt:

```
Buatkan query SQL untuk monitoring health dari data pipeline yang sudah kita buat:

1. Cek status semua Dynamic Tables - apakah semuanya ACTIVE dan kapan terakhir refresh
2. Cek status semua Tasks - apakah STARTED dan kapan terakhir jalan
3. Tampilkan jumlah rows di setiap tabel pipeline (staging dan business layer)
4. Cek apakah ada data freshness issue (data terakhir > 24 jam)

Format hasilnya sebagai dashboard monitoring yang mudah dibaca.
```

---

### Step 3.6: Visualisasi Pipeline dengan Streamlit

#### Prompt:

```
Buatkan Streamlit app sederhana di Snowflake untuk monitoring data pipeline:

1. Header: "Bank - Pipeline Monitor"
2. Metrics row: Tampilkan 4 KPI cards:
   - Total Nasabah Aktif
   - Total DPK (formatted Rp)
   - NPL Ratio (%)
   - Transaksi Hari Ini
3. Chart: Bar chart NPL ratio per region dari BIZ_CABANG_PERFORMANCE
4. Table: Alert log terbaru dari ALERT_LOG (jika ada)
5. Table: Daily metrics trend dari DAILY_METRICS_LOG

Gunakan st.metric, st.bar_chart, st.dataframe.
Koneksi pakai get_active_session().
```

---

## Part 4: Advanced Use Cases

> **Durasi:** ~10 menit
> **Tujuan:** Tunjukkan versatility Cortex Code untuk berbagai skenario

---

### 4.1: Data Governance

#### Prompt:

```
Buatkan masking policy untuk melindungi kolom ESTIMATED_SALARY di tabel CUSTOMER_CHURN_DATA:
- ACCOUNTADMIN dan COMPLIANCE_OFFICER bisa lihat nilai asli
- Role lain hanya lihat range (< 5jt, 5-10jt, 10-20jt, > 20jt)

Buat policy-nya dan apply ke kolom yang sesuai.
```

---

### 4.2: Query Debugging

#### Prompt:

```
Query berikut berjalan sangat lambat. Analisis kenapa dan berikan rekomendasi optimasi:

SELECT dn.*, ft.*, fs.*, fk.*
FROM DIM_NASABAH dn
CROSS JOIN FACT_TRANSAKSI ft
LEFT JOIN FACT_SIMPANAN fs ON dn.nasabah_id = fs.nasabah_id
LEFT JOIN FACT_KREDIT fk ON dn.nasabah_id = fk.nasabah_id
WHERE ft.jumlah > 1000000
ORDER BY ft.tanggal_transaksi DESC;

Jelaskan masalahnya dan buatkan versi yang dioptimasi.
```

---

### 4.3: Auto-Generate Documentation

#### Prompt:

```
Buatkan dokumentasi lengkap untuk semua tabel di schema BANK_NUSANTARA_DB.RAW_DATA:

1. Untuk setiap tabel, tampilkan:
   - Nama tabel dan deskripsi singkat
   - Jumlah rows
   - Daftar kolom dengan tipe data dan penjelasan bisnis
   - Sample data (3 rows)
   - Relasi ke tabel lain (foreign key relationship)

Format sebagai markdown documentation yang bisa langsung dipakai tim data.
```

---

### 4.4: Generate Test Cases

#### Prompt:

```
Buatkan SQL test cases untuk memvalidasi data quality di tabel FACT_KREDIT:

1. Null check: tidak boleh ada NULL di kolom kredit_id, nasabah_id, jumlah_pinjaman
2. Range check: jumlah_pinjaman harus > 0, outstanding harus <= jumlah_pinjaman
3. Referential integrity: semua nasabah_id di FACT_KREDIT harus ada di DIM_NASABAH
4. Business rule: status_kolektibilitas harus diawali angka 1-5
5. Duplicate check: tidak boleh ada duplikat kredit_id
6. Freshness check: tanggal_pencairan tidak boleh di masa depan

Untuk setiap test, tampilkan jumlah pelanggaran dan contoh data yang bermasalah.
```

---

## Part 5: Hands-on Challenge - Fraud Detection Model

> **Durasi:** 15-20 menit
> **Format:** Peserta bekerja sendiri/berpasangan, menggunakan Cortex Code untuk menyelesaikan challenge

---

### Instruksi Challenge

**Tantangan:** Bangun Fraud Detection Model sederhana menggunakan Cortex Code.

Peserta bebas bertanya ke Cortex Code untuk menyelesaikan setiap langkah. Berikut adalah **hint prompts** yang bisa digunakan jika stuck:

---

### Challenge Step 1: Generate Data

**Hint prompt:**

```
Buatkan tabel TRANSACTION_FRAUD_DATA di BANK_NUSANTARA_DB.RAW_DATA dengan 10,000 rows:

Kolom:
- TRX_ID, NASABAH_ID, TRX_DATE, TRX_AMOUNT, MERCHANT_CATEGORY
- TRX_CHANNEL (ATM/Mobile/Internet/EDC/Teller)
- TRX_HOUR (0-23), TRX_DAY_OF_WEEK (1-7)
- IS_INTERNATIONAL (0/1), IS_WEEKEND (0/1)
- AVG_TRX_AMOUNT_30D, NUM_TRX_LAST_24H, NUM_DISTINCT_MERCHANTS_7D
- DISTANCE_FROM_HOME_KM
- IS_FRAUD (target: 0 atau 1, fraud rate ~3%)

Buat data realistis: transaksi fraud cenderung:
- Jumlah besar (> 5x rata-rata normal)
- Di luar jam kerja (malam hari)
- International transactions
- Jarak jauh dari rumah
- Frekuensi tinggi dalam 24 jam terakhir
```

---

### Challenge Step 2: Quick EDA

**Hint prompt:**

```
Lakukan EDA cepat pada tabel TRANSACTION_FRAUD_DATA:
- Distribusi fraud vs non-fraud
- Rata-rata amount untuk fraud vs non-fraud
- Channel mana yang paling banyak fraud
- Jam berapa paling banyak fraud
- Visualisasikan dalam chart
```

---

### Challenge Step 3: Train Model

**Hint prompt:**

```
Train Random Forest classifier untuk fraud detection pada TRANSACTION_FRAUD_DATA:
- Features: TRX_AMOUNT, TRX_HOUR, TRX_DAY_OF_WEEK, IS_INTERNATIONAL, IS_WEEKEND,
  AVG_TRX_AMOUNT_30D, NUM_TRX_LAST_24H, NUM_DISTINCT_MERCHANTS_7D, DISTANCE_FROM_HOME_KM
- Target: IS_FRAUD
- Handle imbalanced data (fraud hanya 3%)
- Evaluasi: AUC-ROC, Precision-Recall, F1-score
- Tampilkan feature importance
```

---

### Challenge Step 4: Register & Score

**Hint prompt:**

```
Register model fraud detection ke Snowflake Model Registry dengan nama FRAUD_DETECTION_MODEL V1.
Lalu buat SQL query untuk scoring semua transaksi dan flag yang fraud probability > 0.5.
```

---

### Challenge Scoring (untuk presentasi)

| Kriteria | Poin |
|----------|------|
| Data berhasil di-generate | 20 |
| EDA lengkap dengan visualisasi | 20 |
| Model berhasil di-train dan evaluasi | 25 |
| Model ter-register di Registry | 20 |
| Batch inference berhasil | 15 |
| **Total** | **100** |

---

## Tips untuk Peserta

### Cara Prompting yang Efektif

| Tip | Contoh |
|-----|--------|
| **Spesifik** | "Buatkan XGBoost classifier" bukan "buatkan model ML" |
| **Berikan konteks** | "Gunakan tabel DIM_NASABAH di schema RAW_DATA" |
| **Tentukan output** | "Tampilkan AUC-ROC, precision, recall" |
| **Iteratif** | Mulai sederhana, lalu tambahkan kompleksitas |
| **Minta penjelasan** | "Jelaskan kenapa kamu memilih parameter ini" |

### Jika Cortex Code Salah

1. **Berikan koreksi spesifik:** "Kolom namanya `JUMLAH_PINJAMAN` bukan `LOAN_AMOUNT`"
2. **Tambah konteks:** "Tabel ini di schema RAW_DATA, bukan PUBLIC"
3. **Minta revisi:** "Revisi query di atas, tambahkan filter WHERE status = 'Aktif'"

### Keyboard Shortcuts

| Shortcut | Fungsi |
|----------|--------|
| `Cmd/Ctrl + Shift + Space` | Buka Cortex Code |
| `Cmd/Ctrl + Enter` | Jalankan cell/query |
| `Tab` | Accept suggestion |
| `Esc` | Dismiss suggestion |

---

## Cleanup

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE BANK_NUSANTARA_DB;

-- Tabel dari ML Model exercise
DROP TABLE IF EXISTS RAW_DATA.CUSTOMER_CHURN_DATA;
DROP TABLE IF EXISTS RAW_DATA.CHURN_FEATURES;
DROP MODEL IF EXISTS ML_MODELS.CHURN_PREDICTION_MODEL;

-- Tabel dari Pipeline exercise
DROP DYNAMIC TABLE IF EXISTS ANALYTICS.STG_NASABAH;
DROP DYNAMIC TABLE IF EXISTS ANALYTICS.STG_TRANSAKSI;
DROP DYNAMIC TABLE IF EXISTS ANALYTICS.BIZ_NASABAH_360;
DROP DYNAMIC TABLE IF EXISTS ANALYTICS.BIZ_CABANG_PERFORMANCE;
DROP TABLE IF EXISTS ANALYTICS.ALERT_LOG;
DROP TABLE IF EXISTS ANALYTICS.DAILY_METRICS_LOG;
ALTER TASK IF EXISTS ANALYTICS.TASK_NPL_ALERT SUSPEND;
ALTER TASK IF EXISTS ANALYTICS.TASK_DAILY_SUMMARY SUSPEND;
DROP TASK IF EXISTS ANALYTICS.TASK_NPL_ALERT;
DROP TASK IF EXISTS ANALYTICS.TASK_DAILY_SUMMARY;

-- Tabel dari Challenge exercise
DROP TABLE IF EXISTS RAW_DATA.TRANSACTION_FRAUD_DATA;
DROP MODEL IF EXISTS ML_MODELS.FRAUD_DETECTION_MODEL;
```

---

## Ringkasan Session

| Aktivitas | Apa yang Dipelajari |
|-----------|-------------------|
| **SQL Generation** | Cortex Code bisa generate complex SQL dari bahasa natural |
| **Code Explanation** | Cortex Code bisa menjelaskan query kompleks step by step |
| **ML Model** | Build churn prediction dari nol: data → EDA → train → register → inference |
| **Data Pipeline** | Build ETL: staging → business layer → alerting → monitoring |
| **Governance** | Generate masking policies, data quality tests |
| **Debugging** | Identifikasi dan fix query performance issues |
| **Documentation** | Auto-generate data documentation |

### Key Takeaways

1. **Cortex Code menurunkan barrier to entry** - Tim non-engineer bisa mulai explore data
2. **Produktivitas meningkat** - Task yang biasa butuh jam-an bisa selesai dalam menit
3. **Best Practice Built-in** - Cortex Code aware dengan Snowflake ecosystem dan best practices
4. **Iteratif** - Mulai dari prompt sederhana, iterasi sampai hasilnya sesuai
5. **Tetap harus di-review** - AI-generated code tetap harus di-review oleh manusia

---

**Selamat! Anda telah menyelesaikan seluruh 4 session workshop Snowflake x Bank!**

---

## Penutup Workshop

Dalam 2 hari ini, peserta telah membangun:

| Session | Apa yang Dibangun |
|---------|------------------|
| **Session 1** | AI Banking Assistant (RAG + Cortex Search + Cortex Agent + Snowflake Intelligence) |
| **Session 2** | Data Protection Framework (Masking, Row Access, Projection Policy, Tag-Based) |
| **Session 3** | Credit Scoring Model (Feature Store + XGBoost + Model Registry + SHAP) |
| **Session 4** | Churn Model + Data Pipeline + Fraud Detection (semua via Cortex Code) |

**Semua ini berjalan di satu platform: Snowflake. Tanpa perlu memindahkan data, tanpa infra terpisah.**
