# Day 2 - Session 3: End-to-End Machine Learning

## Workshop: Snowflake x Bank Nusantara
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

- Sudah menyelesaikan **Session 1** (database `BANK_NUSANTARA_DB` dan tabel-tabel sudah ada)
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
4. Pilih database/schema: `BANK_NUSANTARA_DB.RAW_DATA`
5. Tambahkan packages di tab **Packages**:
   - `snowflake-ml-python`
   - `xgboost`
   - `scikit-learn`
   - `matplotlib`
   - `scipy`

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

> **Catatan:** Pastikan koneksi Snowflake sudah dikonfigurasi di `~/.snowflake/connections.toml`

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

| # | Feature | Sumber | Deskripsi |
|---|---------|--------|-----------|
| 1 | `AVG_TRX_AMOUNT` | FACT_TRANSAKSI | Rata-rata jumlah transaksi |
| 2 | `TOTAL_TRX_COUNT` | FACT_TRANSAKSI | Total jumlah transaksi |
| 3 | `DIGITAL_CHANNEL_RATIO` | FACT_TRANSAKSI | Rasio transaksi via channel digital (Mobile Banking, Internet Banking, QRIS) |
| 4 | `FAILED_TRX_RATIO` | FACT_TRANSAKSI | Rasio transaksi gagal |
| 5 | `TOTAL_TRX_VOLUME` | FACT_TRANSAKSI | Total volume transaksi (Rp) |
| 6 | `TOTAL_SIMPANAN` | FACT_SIMPANAN | Total saldo simpanan aktif |
| 7 | `JUMLAH_PRODUK_SIMPANAN` | FACT_SIMPANAN | Jumlah produk simpanan |
| 8 | `MAX_SALDO_SIMPANAN` | FACT_SIMPANAN | Saldo simpanan terbesar |
| 9 | `PENGHASILAN_BULANAN` | DIM_NASABAH | Penghasilan bulanan nasabah |
| 10 | `LAMA_JADI_NASABAH_TAHUN` | DIM_NASABAH | Lama menjadi nasabah (tahun) |
| 11 | `USIA` | DIM_NASABAH | Usia nasabah |
| 12 | `CREDIT_UTILIZATION_RATIO` | FACT_KREDIT | Outstanding / Jumlah Pinjaman |
| 13 | `SAVING_RATIO` | FACT_SIMPANAN + KREDIT | Total Simpanan / Jumlah Pinjaman |

### Snowflake Feature Store

```python
from snowflake.ml.feature_store import FeatureStore, FeatureView, Entity, CreationMode

# Buat Feature Store
fs = FeatureStore(
    session=session,
    database="BANK_NUSANTARA_DB",
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

### Register ke Snowflake Model Registry

```python
from snowflake.ml.registry import Registry

reg = Registry(session=session, database_name="BANK_NUSANTARA_DB", schema_name="ML_MODELS")

mv = reg.log_model(
    model_v2,
    model_name="CREDIT_SCORING_UMKM",
    version_name="V2",
    sample_input_data=X_train.head(10),
    conda_dependencies=["xgboost", "scikit-learn"],
    target_platforms=["WAREHOUSE"],
    metrics={"auc_roc": auc_v2, "average_precision": ap_v2},
    comment="Tuned XGBoost Credit Scoring Model"
)
```

### Verifikasi

```sql
-- Lihat models
SHOW MODELS IN SCHEMA BANK_NUSANTARA_DB.ML_MODELS;

-- Lihat functions
SHOW FUNCTIONS IN MODEL BANK_NUSANTARA_DB.ML_MODELS.CREDIT_SCORING_UMKM VERSION V2;
```

### Snowflake Objects yang Dibuat

| Schema | Object | Type | Deskripsi |
|--------|--------|------|-----------|
| `ML_FEATURES` | `NASABAH_TRANSACTION_FEATURES` | Feature View | Transaction features |
| `ML_FEATURES` | `NASABAH_SIMPANAN_FEATURES` | Feature View | Simpanan features |
| `ML_MODELS` | `CREDIT_SCORING_UMKM` | Model (V1, V2) | XGBoost credit scoring |
| `RAW_DATA` | `CREDIT_SCORING_FEATURES` | Table | Master feature table |

---

## Part 5: Batch Inference & Explainability (SHAP)

### Batch Inference via SQL

```sql
-- Scoring seluruh aplikasi kredit
SELECT
    KREDIT_ID,
    NASABAH_ID,
    IS_DEFAULT AS ACTUAL,
    MODEL(BANK_NUSANTARA_DB.ML_MODELS.CREDIT_SCORING_UMKM, V2)!PREDICT(
        JUMLAH_PINJAMAN, OUTSTANDING, TENOR_BULAN, ...
    ):output_feature_0::INT AS PREDICTED_DEFAULT,
    MODEL(BANK_NUSANTARA_DB.ML_MODELS.CREDIT_SCORING_UMKM, V2)!PREDICT_PROBA(
        JUMLAH_PINJAMAN, OUTSTANDING, TENOR_BULAN, ...
    ):output_feature_1::FLOAT AS DEFAULT_PROBABILITY
FROM BANK_NUSANTARA_DB.RAW_DATA.CREDIT_SCORING_FEATURES;
```

### SHAP Explainability

> **WAJIB untuk regulasi OJK:** Model harus bisa menjelaskan kenapa approve/reject.

```sql
-- SHAP values untuk setiap prediksi
WITH MV_ALIAS AS MODEL BANK_NUSANTARA_DB.ML_MODELS.CREDIT_SCORING_UMKM VERSION V2
SELECT
    t.KREDIT_ID,
    t.NASABAH_ID,
    e.*
FROM BANK_NUSANTARA_DB.RAW_DATA.CREDIT_SCORING_FEATURES t,
    TABLE(MV_ALIAS!EXPLAIN(t.JUMLAH_PINJAMAN, t.OUTSTANDING, ...)) e;
```

**Output:** Setiap kolom `*_EXPLANATION` menunjukkan kontribusi (positif/negatif) feature terhadap prediksi default.

---

## Part 6: ML Observability & Monitoring

### Setup Model Monitor

```python
from snowflake.ml.monitoring import ModelMonitor, ModelMonitorConfig

monitor = ModelMonitor(
    session=session,
    name="CREDIT_SCORING_MONITOR",
    config=ModelMonitorConfig(
        model_version=mv_v2,
        model_function_name="predict_proba",
        background_compute_warehouse_name="BANK_WH"
    )
)
```

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

-- Hapus model
DROP MODEL IF EXISTS BANK_NUSANTARA_DB.ML_MODELS.CREDIT_SCORING_UMKM;

-- Hapus schemas
DROP SCHEMA IF EXISTS BANK_NUSANTARA_DB.ML_FEATURES CASCADE;
DROP SCHEMA IF EXISTS BANK_NUSANTARA_DB.ML_MODELS CASCADE;

-- Hapus feature table
DROP TABLE IF EXISTS BANK_NUSANTARA_DB.RAW_DATA.CREDIT_SCORING_FEATURES;
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: snowflake.ml` | Install: `pip install snowflake-ml-python` |
| `xgboost not found` | Install: `pip install xgboost` (atau tambahkan di Snowsight Packages) |
| Model registration gagal | Pastikan schema `ML_MODELS` sudah exist, cek privileges |
| `MODEL()!PREDICT()` error | Cek jumlah dan urutan kolom harus sama persis dengan saat training |
| Feature Store error | Pastikan schema `ML_FEATURES` bisa dibuat, cek warehouse aktif |
| SHAP `EXPLAIN()` tidak tersedia | Model harus di-register dengan `sample_input_data` dan `target_platforms=["WAREHOUSE"]` |
| GridSearchCV sangat lambat | Kurangi `param_grid` atau gunakan `RandomizedSearchCV` |
| Imbalanced dataset | Gunakan `scale_pos_weight` di XGBoost (sudah dihandle di notebook) |

---

## Referensi

- [Snowflake Feature Store Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview)
- [Snowflake Model Registry Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview)
- [Snowflake ML Observability](https://docs.snowflake.com/en/developer-guide/snowflake-ml/monitoring/overview)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)

---

## Koneksi ke Bank Mandiri

| Aspek | Relevansi |
|-------|-----------|
| **Livin' Merchant** | Data transaksi UMKM real-time → perfect untuk cash-flow based lending |
| **AI Fraud Detection** | Bank Mandiri sudah pakai AI (85% reduction) - credit scoring adalah next step |
| **Regulasi OJK** | SHAP explainability → transparansi model wajib untuk persetujuan kredit |
| **ML Lineage** | Audit trail data → akuntabilitas sesuai regulasi |

---

**Selamat! Anda telah berhasil membangun Credit Scoring Model end-to-end di Snowflake!**
