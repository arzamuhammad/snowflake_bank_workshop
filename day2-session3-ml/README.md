# Day 2 - Session 3: End-to-End Machine Learning

## Workshop: Snowflake x Bank
### "Credit Scoring Model untuk Kredit UMKM"

---

## Tujuan Session

Pada session ini, peserta akan membangun **Credit Scoring Model** secara end-to-end di Snowflake:

1. **Data Preparation & EDA** - Eksplorasi data kredit dan buat binary target variable
2. **Feature Engineering & Feature Store** - Buat features dari transaksi, simpanan, dan demografis; register ke Snowflake Feature Store
3. **Model Training** - Train XGBoost Classifier (Baseline V1 + Tuned V2 dengan GridSearchCV)
4. **Model Registry & Deployment** - Register model ke Snowflake Model Registry, inference via SQL
5. **Batch Inference & Explainability** - Scoring batch via `MODEL()!PREDICT()`, SHAP values via `MODEL()!EXPLAIN()`
6. **ML Observability** - Monitor prediction drift, feature drift, dan performance degradation

**AHA Moment:** *"Build credit scoring model production-ready dalam satu session, lengkap dengan explainability (SHAP) dan lineage!"*

---

## Daftar Isi

- [Pre-requisites](#pre-requisites)
- [Arsitektur ML Pipeline](#arsitektur-ml-pipeline)
- [Setup Environment](#setup-environment)
- [Part 1: Data Preparation & EDA](#part-1-data-preparation--eda)
- [Part 2: Feature Engineering & Feature Store](#part-2-feature-engineering--feature-store)
- [Part 3: Model Training (XGBoost)](#part-3-model-training-xgboost)
- [Part 4: Model Registry & Deployment](#part-4-model-registry--deployment)
- [Part 5: Batch Inference & Explainability (SHAP)](#part-5-batch-inference--explainability-shap)
- [Part 6: ML Observability & Monitoring](#part-6-ml-observability--monitoring)
- [Cleanup](#cleanup)
- [Troubleshooting](#troubleshooting)

---

## Pre-requisites

- Sudah menyelesaikan **Session 1** (database `BANK_DB` dan tabel-tabel sudah ada)
- Snowflake Trial Account (**Enterprise Edition** atau lebih tinggi)
- Role: **ACCOUNTADMIN**
- Python environment dengan packages berikut:
  - `snowflake-ml-python` >= 1.5.0
  - `snowflake-snowpark-python`
  - `xgboost`
  - `scikit-learn`
  - `pandas`, `numpy`
  - `matplotlib`
  - `scipy`

---

## Arsitektur ML Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Snowflake ML Pipeline                                │
│                                                                             │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────────┐         │
│  │  RAW DATA    │    │  FEATURE STORE   │    │  MODEL REGISTRY   │         │
│  │              │    │                  │    │                   │         │
│  │ DIM_NASABAH  │───▶│ TRX_FEATURES     │───▶│ CREDIT_SCORING    │         │
│  │ DIM_CABANG   │    │ SIMPANAN_FEATURES│    │ _UMKM             │         │
│  │ FACT_KREDIT  │    │                  │    │   V1 (Baseline)   │         │
│  │ FACT_TRANSAKSI    │ Entity: NASABAH  │    │   V2 (Tuned)      │         │
│  │ FACT_SIMPANAN│    │                  │    │                   │         │
│  └──────────────┘    └──────────────────┘    └─────────┬─────────┘         │
│                                                         │                   │
│                                              ┌──────────▼──────────┐       │
│                                              │     INFERENCE       │       │
│                                              │                     │       │
│                                              │ SQL: MODEL()!       │       │
│                                              │   PREDICT()         │       │
│                                              │   PREDICT_PROBA()   │       │
│                                              │   EXPLAIN() (SHAP)  │       │
│                                              └──────────┬──────────┘       │
│                                                         │                   │
│                                              ┌──────────▼──────────┐       │
│                                              │   ML OBSERVABILITY  │       │
│                                              │                     │       │
│                                              │ - Prediction Drift  │       │
│                                              │ - Feature Drift     │       │
│                                              │ - Performance Track │       │
│                                              └─────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Setup Environment

### Opsi A: Snowflake Notebook (Snowsight)

1. Buka Snowsight → **Projects** → **Notebooks**
2. Klik **+ Notebook** → Upload file `credit_scoring_ml.ipynb`
3. Pilih warehouse: `BANK_WH`
4. Pilih database/schema: `BANK_DB.RAW_DATA`
5. Tambahkan packages di tab **Packages**:
   - `snowflake-ml-python`
   - `xgboost`
   - `scikit-learn`
   - `matplotlib`
   - `scipy`

> **Catatan Session:** Di dalam Snowsight Notebook, session di-inject otomatis via `get_active_session()` — tidak perlu `Session.builder`. Notebook ini sudah menggunakan pola tersebut:
> ```python
> from snowflake.snowpark.context import get_active_session
> session = get_active_session()
> ```

### Opsi B: Local (IDE / CLI)

```bash
# 1. Buat virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install snowflake-ml-python snowflake-snowpark-python xgboost scikit-learn pandas numpy matplotlib scipy

# 3. Jalankan notebook
jupyter notebook credit_scoring_ml.ipynb
```

> **Catatan:** Untuk run lokal, uncomment dua baris `connection_name` + `Session.builder` di cell setup notebook, dan pastikan koneksi Snowflake sudah dikonfigurasi di `~/.snowflake/connections.toml`.

---

## Part 1: Data Preparation & EDA

### Dataset yang Digunakan (dari Session 1)

| Tabel | Jumlah Rows | Deskripsi |
|-------|-------------|-----------|
| `DIM_NASABAH` | 10,000 | Data demografis nasabah |
| `DIM_CABANG` | 67 | Data cabang bank |
| `FACT_KREDIT` | 5,000 | Data kredit dengan status kolektibilitas |
| `FACT_TRANSAKSI` | 100,000 | Data transaksi |
| `FACT_SIMPANAN` | 15,000 | Data simpanan |

### Target Variable

Status kolektibilitas (1-5) di-convert ke binary classification:

| Kolektibilitas | Kategori OJK | Label |
|---------------|-------------|-------|
| 1 - Lancar | Performing | **NON-DEFAULT (0)** |
| 2 - Dalam Perhatian Khusus | Performing | **NON-DEFAULT (0)** |
| 3 - Kurang Lancar | Non-Performing (NPL) | **DEFAULT (1)** |
| 4 - Diragukan | Non-Performing (NPL) | **DEFAULT (1)** |
| 5 - Macet | Non-Performing (NPL) | **DEFAULT (1)** |

### Langkah-langkah:

1. Load semua tabel dari Snowflake via Snowpark
2. Buat binary target variable `IS_DEFAULT` dari `STATUS_KOLEKTIBILITAS`
3. Visualisasi distribusi: kolektibilitas, default rate per jenis kredit, distribusi pinjaman
4. Cek imbalanced ratio (penting untuk credit scoring)

---

## Part 2: Feature Engineering & Feature Store

### Features yang Dibuat

| # | Feature | Sumber | Deskripsi | Tipe |
|---|---------|--------|-----------|------|
| 1 | `AVG_TRX_AMOUNT` | FACT_TRANSAKSI | Rata-rata jumlah transaksi | Numeric |
| 2 | `TOTAL_TRX_COUNT` | FACT_TRANSAKSI | Total jumlah transaksi | Numeric |
| 3 | `DIGITAL_CHANNEL_RATIO` | FACT_TRANSAKSI | Rasio transaksi via channel digital (Mobile Banking, Internet Banking, QRIS) | Numeric |
| 4 | `FAILED_TRX_RATIO` | FACT_TRANSAKSI | Rasio transaksi gagal | Numeric |
| 5 | `TOTAL_TRX_VOLUME` | FACT_TRANSAKSI | Total volume transaksi (Rp) | Numeric |
| 6 | `TOTAL_SIMPANAN` | FACT_SIMPANAN | Total saldo simpanan aktif | Numeric |
| 7 | `JUMLAH_PRODUK_SIMPANAN` | FACT_SIMPANAN | Jumlah produk simpanan | Numeric |
| 8 | `MAX_SALDO_SIMPANAN` | FACT_SIMPANAN | Saldo simpanan terbesar | Numeric |
| 9 | `AVG_BUNGA_SIMPANAN` | FACT_SIMPANAN | Rata-rata suku bunga simpanan | Numeric |
| 10 | `PENGHASILAN_BULANAN` | DIM_NASABAH | Penghasilan bulanan nasabah | Numeric |
| 11 | `LAMA_JADI_NASABAH_TAHUN` | DIM_NASABAH | Lama menjadi nasabah (tahun) | Numeric |
| 12 | `USIA` | DIM_NASABAH | Usia nasabah | Numeric |
| 13 | `CREDIT_UTILIZATION_RATIO` | FACT_KREDIT | Outstanding / Jumlah Pinjaman | Numeric |
| 14 | `SAVING_RATIO` | FACT_SIMPANAN + KREDIT | Total Simpanan / Jumlah Pinjaman | Numeric |
| 15 | `JENIS_KREDIT` | FACT_KREDIT | Jenis produk kredit | Categorical (encoded) |
| 16 | `SEKTOR_EKONOMI` | FACT_KREDIT | Sektor ekonomi nasabah | Categorical (encoded) |
| 17 | `AGUNAN` | FACT_KREDIT | Jenis agunan kredit | Categorical (encoded) |
| 18 | `SEGMEN_NASABAH` | DIM_NASABAH | Segmen nasabah (e.g. UMKM, Retail) | Categorical (encoded) |
| 19 | `PEKERJAAN` | DIM_NASABAH | Pekerjaan nasabah | Categorical (encoded) |
| 20 | `JENIS_KELAMIN` | DIM_NASABAH | Jenis kelamin nasabah | Categorical (encoded) |

> **Catatan:** Fitur kategorikal di-encode dengan `sklearn.preprocessing.LabelEncoder` sebelum training. Saat V2 dilog ulang ke Model Registry, encoding yang sama direplikasi di Snowpark (`_encode_snowpark` helper) untuk memastikan sample input Snowpark cocok dengan schema training — ini yang memungkinkan ML Lineage tercatat.

### Snowflake Feature Store

```python
from snowflake.ml.feature_store import FeatureStore, FeatureView, Entity, CreationMode

# Buat Feature Store
fs = FeatureStore(
    session=session,
    database="BANK_DB",
    name="ML_FEATURES",
    default_warehouse="BANK_WH",
    creation_mode=CreationMode.CREATE_IF_NOT_EXIST
)

# Register Entity
nasabah_entity = Entity(name="NASABAH", join_keys=["NASABAH_ID"])
fs.register_entity(nasabah_entity)

# Register Feature Views
trx_feature_view = FeatureView(
    name="NASABAH_TRANSACTION_FEATURES",
    entities=[nasabah_entity],
    feature_df=trx_fv_df,
    desc="Transaction features per nasabah"
)
fs.register_feature_view(feature_view=trx_feature_view, version="V1")
```

**Keuntungan Feature Store:**
- **Reusability** - Features bisa dipakai oleh multiple models
- **Versioning** - Track perubahan feature logic
- **Discovery** - Tim lain bisa menemukan features yang sudah ada
- **Consistency** - Training dan inference menggunakan features yang sama

---

## Part 3: Model Training (XGBoost)

### 3.1 Baseline Model (V1)

```python
model_v1 = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,  # Handle imbalanced data
    eval_metric='auc'
)
```

### 3.2 Tuned Model (V2) - GridSearchCV

```python
param_grid = {
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [100, 200, 300],
    'min_child_weight': [1, 3, 5],
    'subsample': [0.8, 1.0],
}

grid_search = GridSearchCV(
    estimator=xgb_base,
    param_grid=param_grid,
    scoring='roc_auc',
    cv=3,
    n_jobs=-1
)
```

### Metrics Penting untuk Credit Scoring

| Metric | Kenapa Penting |
|--------|---------------|
| **AUC-ROC** | Overall discriminative power model |
| **Precision (Default)** | Berapa banyak prediksi default yang benar (false positive = reject nasabah baik) |
| **Recall (Default)** | Berapa banyak actual default yang berhasil dideteksi (false negative = loloskan nasabah berisiko) |
| **Average Precision** | Ringkasan precision-recall trade-off |

> **Untuk perbankan:** Cost of False Negative (meloloskan default) >> Cost of False Positive (menolak nasabah baik). Oleh karena itu **Recall** sangat penting.

---

## Part 4: Model Registry & Deployment

### Register Model V1 (Baseline) - pandas sample

```python
from snowflake.ml.registry import Registry

reg = Registry(session=session, database_name="BANK_DB", schema_name="ML_MODELS")

mv_v1 = reg.log_model(
    model_v1,
    model_name="CREDIT_SCORING_UMKM",
    version_name="V1",
    sample_input_data=X_train.head(10),              # pandas DataFrame
    conda_dependencies=["xgboost", "scikit-learn"],
    target_platforms=["WAREHOUSE"],
    metrics={"auc_roc": auc_v1, "average_precision": ap_v1},
    comment="Baseline XGBoost Credit Scoring Model - no tuning"
)
```

### Register Model V2 (Tuned) - Snowpark sample untuk Lineage

Agar Snowflake bisa mencatat **ML Lineage** (source tables → model), V2 di-log ulang dengan **Snowpark DataFrame** sebagai `sample_input_data`. Karena kolom kategorikal sudah di-`LabelEncoder` di pandas, encoding yang sama direplikasi di Snowpark via helper:

```python
def _encode_snowpark(col_name, le):
    classes = list(le.classes_)
    expr = F.when(F.col(col_name) == F.lit(classes[0]), F.lit(0))
    for i, cls in enumerate(classes[1:], start=1):
        expr = expr.when(F.col(col_name) == F.lit(cls), F.lit(i))
    return expr.otherwise(F.lit(-1)).cast(T.IntegerType()).alias(col_name)

sample_sp_df = master_features.select(*select_exprs).na.fill(0).limit(10)

# Drop existing V2 dulu lalu re-log
try:
    reg.get_model("CREDIT_SCORING_UMKM").delete_version("V2")
except Exception:
    pass

mv_v2 = reg.log_model(
    model_v2,
    model_name="CREDIT_SCORING_UMKM",
    version_name="V2",
    sample_input_data=sample_sp_df,                  # Snowpark DataFrame (untuk lineage)
    conda_dependencies=["xgboost", "scikit-learn"],
    target_platforms=["WAREHOUSE"],
    metrics={
        "auc_roc": auc_v2,
        "average_precision": ap_v2,
        "best_params": str(grid_search.best_params_),
    },
    comment="Tuned XGBoost Credit Scoring Model - re-logged with Snowpark sample_input for lineage"
)
```

> **Kenapa Snowpark sample_input?** Saat `sample_input_data` berupa Snowpark DataFrame, Snowflake mencatat tabel sumber → feature columns → model version, sehingga `mv.lineage(direction="upstream")` mengembalikan referensi object yang benar.

### Verifikasi

```sql
-- Lihat models
SHOW MODELS IN SCHEMA BANK_DB.ML_MODELS;

-- Lihat functions
SHOW FUNCTIONS IN MODEL BANK_DB.ML_MODELS.CREDIT_SCORING_UMKM VERSION V2;
```

### Snowflake Objects yang Dibuat

| Schema | Object | Type | Deskripsi |
|--------|--------|------|-----------|
| `ML_FEATURES` | `NASABAH_TRANSACTION_FEATURES` | Feature View | Transaction features |
| `ML_FEATURES` | `NASABAH_SIMPANAN_FEATURES` | Feature View | Simpanan features |
| `ML_MODELS` | `CREDIT_SCORING_UMKM` | Model (V1, V2) | XGBoost credit scoring |
| `ML_MODELS` | `CREDIT_SCORING_MONITOR` | Model Monitor | Monitor drift + performance V2 |
| `RAW_DATA` | `CREDIT_SCORING_FEATURES` | Table | Master feature table (encoded) |
| `RAW_DATA` | `CREDIT_SCORING_PREDICTIONS` | Table | Inference log (source utk Model Monitor) |

---

## Part 5: Batch Inference & Explainability (SHAP)

### Batch Inference via SQL

```sql
-- Scoring seluruh aplikasi kredit
SELECT
    KREDIT_ID,
    NASABAH_ID,
    IS_DEFAULT AS ACTUAL,
    MODEL(BANK_DB.ML_MODELS.CREDIT_SCORING_UMKM, V2)!PREDICT(
        JUMLAH_PINJAMAN, OUTSTANDING, TENOR_BULAN, ...
    ):output_feature_0::INT AS PREDICTED_DEFAULT,
    MODEL(BANK_DB.ML_MODELS.CREDIT_SCORING_UMKM, V2)!PREDICT_PROBA(
        JUMLAH_PINJAMAN, OUTSTANDING, TENOR_BULAN, ...
    ):output_feature_1::FLOAT AS DEFAULT_PROBABILITY
FROM BANK_DB.RAW_DATA.CREDIT_SCORING_FEATURES;
```

### SHAP Explainability

> **WAJIB untuk regulasi OJK:** Model harus bisa menjelaskan kenapa approve/reject.

```sql
-- SHAP values untuk setiap prediksi
WITH MV_ALIAS AS MODEL BANK_DB.ML_MODELS.CREDIT_SCORING_UMKM VERSION V2
SELECT
    t.KREDIT_ID,
    t.NASABAH_ID,
    e.*
FROM BANK_DB.RAW_DATA.CREDIT_SCORING_FEATURES t,
    TABLE(MV_ALIAS!EXPLAIN(t.JUMLAH_PINJAMAN, t.OUTSTANDING, ...)) e;
```

**Output:** Setiap kolom `*_EXPLANATION` menunjukkan kontribusi (positif/negatif) feature terhadap prediksi default.

---

## Part 6: ML Observability & Monitoring

### 6.1 Buat Inference Log Table

Model Monitor butuh source table yang berisi **features + prediction score + actual label + timestamp**. Notebook membuatnya via SQL:

```sql
CREATE OR REPLACE TABLE BANK_DB.RAW_DATA.CREDIT_SCORING_PREDICTIONS AS
SELECT
    KREDIT_ID,
    NASABAH_ID,
    IS_DEFAULT AS ACTUAL_DEFAULT,
    <feature_cols>,
    MODEL(BANK_DB.ML_MODELS.CREDIT_SCORING_UMKM, V2)!PREDICT_PROBA(
        <feature_cols>
    ):output_feature_1::FLOAT AS DEFAULT_PROBABILITY,
    CURRENT_TIMESTAMP()::TIMESTAMP_NTZ AS PREDICTION_TS
FROM BANK_DB.RAW_DATA.CREDIT_SCORING_FEATURES;
```

### 6.2 Setup Model Monitor (SQL)

Notebook menggunakan **SQL `CREATE MODEL MONITOR`** (bukan Python API) — ini approach yang direkomendasikan Snowflake saat ini:

```sql
CREATE OR REPLACE MODEL MONITOR BANK_DB.ML_MODELS.CREDIT_SCORING_MONITOR
WITH
    MODEL = BANK_DB.ML_MODELS.CREDIT_SCORING_UMKM
    VERSION = V2
    FUNCTION = 'predict_proba'
    WAREHOUSE = BANK_WH
    SOURCE = BANK_DB.RAW_DATA.CREDIT_SCORING_PREDICTIONS
    TIMESTAMP_COLUMN = PREDICTION_TS
    PREDICTION_SCORE_COLUMNS = (DEFAULT_PROBABILITY)
    ACTUAL_CLASS_COLUMNS = (ACTUAL_DEFAULT)
    ID_COLUMNS = (KREDIT_ID)
    REFRESH_INTERVAL = '1 day'
    AGGREGATION_WINDOW = '1 day';

SHOW MODEL MONITORS IN SCHEMA BANK_DB.ML_MODELS;
```

### 6.3 ML Lineage - Audit Trail

```python
upstream   = mv_v2.lineage(direction="upstream")     # tabel / feature views sumber
downstream = mv_v2.lineage(direction="downstream")   # objects turunan dari model
```

> Lineage hanya populated bila model di-log dengan **Snowpark DataFrame** sebagai `sample_input_data` (lihat Part 4.2).

### 6.4 Simulasi Drift Detection (Scipy KS-Test)

Untuk demo, notebook menyuntikkan shift kecil pada prediksi baseline dan menguji dengan Kolmogorov-Smirnov:

```python
from scipy import stats
shifted_probs = np.clip(y_prob_v2 + np.random.normal(0.05, 0.02, len(y_prob_v2)), 0, 1)
ks_stat, ks_pvalue = stats.ks_2samp(y_prob_v2, shifted_probs)
# p-value < 0.05 → significant drift → retrain
```

Plot yang dihasilkan (`drift_detection.png`):
- Histogram distribusi probabilitas Week 1 (baseline) vs Week 4 (drifted)
- Time series AUC-ROC mingguan dengan threshold alert (0.75)

### Jenis Monitoring

| Jenis | Deskripsi | Alert Threshold |
|-------|-----------|----------------|
| **Prediction Drift** | Distribusi prediksi berubah dari baseline | KS-test p-value < 0.05 |
| **Feature Drift** | Distribusi input features berubah | PSI > 0.2 |
| **Performance Degradation** | AUC-ROC turun di bawah threshold | AUC < 0.75 |

### Kenapa Monitoring Penting?

- **Regulatory Compliance:** OJK mengharuskan model divalidasi secara berkala
- **Business Risk:** Model yang degrade bisa menyebabkan kerugian kredit
- **Data Quality:** Perubahan data source bisa mempengaruhi model performance

---

## Cleanup

Jalankan setelah workshop selesai:

```sql
USE ROLE ACCOUNTADMIN;

-- Hapus model monitor dan model
DROP MODEL MONITOR IF EXISTS BANK_DB.ML_MODELS.CREDIT_SCORING_MONITOR;
DROP MODEL IF EXISTS BANK_DB.ML_MODELS.CREDIT_SCORING_UMKM;

-- Hapus schemas
DROP SCHEMA IF EXISTS BANK_DB.ML_FEATURES CASCADE;
DROP SCHEMA IF EXISTS BANK_DB.ML_MODELS CASCADE;

-- Hapus feature & prediction tables
DROP TABLE IF EXISTS BANK_DB.RAW_DATA.CREDIT_SCORING_FEATURES;
DROP TABLE IF EXISTS BANK_DB.RAW_DATA.CREDIT_SCORING_PREDICTIONS;
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: snowflake.ml` | Install: `pip install snowflake-ml-python` |
| `xgboost not found` | Install: `pip install xgboost` (atau tambahkan di Snowsight Packages) |
| Model registration gagal | Pastikan schema `ML_MODELS` sudah exist, cek privileges |
| `MODEL()!PREDICT()` error | Cek jumlah dan urutan kolom harus sama persis dengan saat training (lihat `feature_cols`) |
| Feature Store error | Pastikan schema `ML_FEATURES` bisa dibuat, cek warehouse aktif |
| SHAP `EXPLAIN()` tidak tersedia | Model harus di-register dengan `sample_input_data` dan `target_platforms=["WAREHOUSE"]` |
| `mv_v2.lineage()` return kosong | Model V2 harus di-log ulang dengan **Snowpark DataFrame** sebagai `sample_input_data` (lihat Part 4.2, helper `_encode_snowpark`) |
| `CREATE MODEL MONITOR` gagal | Source table (`CREDIT_SCORING_PREDICTIONS`) harus ada dengan kolom: `PREDICTION_TS` (TIMESTAMP_NTZ), `DEFAULT_PROBABILITY`, `ACTUAL_DEFAULT`, `KREDIT_ID` |
| GridSearchCV sangat lambat | Kurangi `param_grid` atau gunakan `RandomizedSearchCV` |
| Imbalanced dataset | Gunakan `scale_pos_weight` di XGBoost (sudah dihandle di notebook) |
| `get_active_session()` error di lokal | Jalankan di Snowsight Notebook, atau uncomment baris `Session.builder` di cell setup untuk local run |

---

## Referensi

- [Snowflake Feature Store Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview)
- [Snowflake Model Registry Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview)
- [Snowflake ML Observability](https://docs.snowflake.com/en/developer-guide/snowflake-ml/monitoring/overview)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)

---

## Koneksi ke Bank

| Aspek | Relevansi |
|-------|-----------|
| **Livin' Merchant** | Data transaksi UMKM real-time → perfect untuk cash-flow based lending |
| **AI Fraud Detection** | Bank sudah pakai AI (85% reduction) - credit scoring adalah next step |
| **Regulasi OJK** | SHAP explainability → transparansi model wajib untuk persetujuan kredit |
| **ML Lineage** | Audit trail data → akuntabilitas sesuai regulasi |

---

**Selamat! Anda telah berhasil membangun Credit Scoring Model end-to-end di Snowflake!**
