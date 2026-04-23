# Day 1 - Session 2: Data Protection Policies

## Workshop: Snowflake x Bank
### "Proteksi Data Nasabah Sesuai Regulasi OJK & UU PDP"

---

## Tujuan Session

Pada session ini, peserta akan belajar bagaimana melindungi data nasabah menggunakan fitur Data Protection di Snowflake:

1. **Role-Based Access Control (RBAC)** - Hierarki role perbankan
2. **Data Masking Policy** - Menyembunyikan data sensitif (NIK, nama, saldo) per role
3. **Row Access Policy** - Segregasi data per cabang/region
4. **Projection Policy** - Mencegah bulk extraction data PII
5. **Tag-Based Masking** - Otomatis masking berdasarkan tag PII

**AHA Moment:** *"Satu tabel, tapi setiap role melihat data yang berbeda!"*

---

## Daftar Isi

- [Part 1: Setup Roles & Privileges (Banking Hierarchy)](#part-1-setup-roles--privileges-banking-hierarchy)
- [Part 2: Data Masking Policies](#part-2-data-masking-policies)
- [Part 3: Row Access Policy (Branch Segregation)](#part-3-row-access-policy-branch-segregation)
- [Part 4: Projection Policy (Anti Bulk Extraction)](#part-4-projection-policy-anti-bulk-extraction)
- [Part 5: Tag-Based Masking (Automated PII Protection)](#part-5-tag-based-masking-automated-pii-protection)
- [Part 6: Testing - Switch Role & Verifikasi](#part-6-testing---switch-role--verifikasi)

---

## Pre-requisites

- Sudah menyelesaikan **Session 1** (database BANK_DB dan tabel-tabel sudah ada)
- Role: **ACCOUNTADMIN** (untuk setup awal)

---

## Part 1: Setup Roles & Privileges (Banking Hierarchy)

### Step 1.1: Buat Role Hierarchy

```sql
-- ============================================
-- STEP 1.1: Buat Banking Role Hierarchy
-- ============================================
USE ROLE ACCOUNTADMIN;

-- Role Level 1: Administrator
CREATE OR REPLACE ROLE BANK_ADMIN
    COMMENT = 'IT Security & Database Administrator';

-- Role Level 2: Compliance
CREATE OR REPLACE ROLE COMPLIANCE_OFFICER
    COMMENT = 'Audit & Kepatuhan - bisa lihat semua data termasuk PII';

-- Role Level 3: Branch Managers (per region)
CREATE OR REPLACE ROLE BRANCH_MANAGER_JKT
    COMMENT = 'Branch Manager Region Jakarta - hanya akses data Jakarta & Banten';

CREATE OR REPLACE ROLE BRANCH_MANAGER_SBY
    COMMENT = 'Branch Manager Region Jawa Timur - hanya akses data Jawa Timur';

CREATE OR REPLACE ROLE BRANCH_MANAGER_BDG
    COMMENT = 'Branch Manager Region Jawa Barat - hanya akses data Jawa Barat';

-- Role Level 4: Analysts
CREATE OR REPLACE ROLE DATA_ANALYST
    COMMENT = 'Tim Data/BI - bisa query tapi data PII di-mask';

CREATE OR REPLACE ROLE RISK_ANALYST
    COMMENT = 'Tim Risk Management - fokus pada data kredit & NPL';

-- Role Level 5: Frontliner
CREATE OR REPLACE ROLE TELLER_ROLE
    COMMENT = 'Frontliner/Teller - akses sangat terbatas';
```

### Step 1.2: Setup Role Hierarchy (Grant Roles)

```sql
-- ============================================
-- STEP 1.2: Role Hierarchy
-- ============================================
-- ACCOUNTADMIN
--   └── BANK_ADMIN
--         ├── COMPLIANCE_OFFICER
--         ├── BRANCH_MANAGER_JKT
--         ├── BRANCH_MANAGER_SBY
--         ├── BRANCH_MANAGER_BDG
--         ├── DATA_ANALYST
--         ├── RISK_ANALYST
--         └── TELLER_ROLE

GRANT ROLE BANK_ADMIN TO ROLE ACCOUNTADMIN;
GRANT ROLE COMPLIANCE_OFFICER TO ROLE BANK_ADMIN;
GRANT ROLE BRANCH_MANAGER_JKT TO ROLE BANK_ADMIN;
GRANT ROLE BRANCH_MANAGER_SBY TO ROLE BANK_ADMIN;
GRANT ROLE BRANCH_MANAGER_BDG TO ROLE BANK_ADMIN;
GRANT ROLE DATA_ANALYST TO ROLE BANK_ADMIN;
GRANT ROLE RISK_ANALYST TO ROLE BANK_ADMIN;
GRANT ROLE TELLER_ROLE TO ROLE BANK_ADMIN;
```

### Step 1.3: Grant Privileges ke Roles

```sql
-- ============================================
-- STEP 1.3: Grant Database & Schema Privileges
-- ============================================

-- Warehouse access untuk semua role
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE BANK_ADMIN;
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE COMPLIANCE_OFFICER;
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE BRANCH_MANAGER_JKT;
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE BRANCH_MANAGER_SBY;
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE BRANCH_MANAGER_BDG;
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE DATA_ANALYST;
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE RISK_ANALYST;
GRANT USAGE ON WAREHOUSE BANK_WH TO ROLE TELLER_ROLE;

-- Database access
GRANT USAGE ON DATABASE BANK_DB TO ROLE BANK_ADMIN;
GRANT USAGE ON DATABASE BANK_DB TO ROLE COMPLIANCE_OFFICER;
GRANT USAGE ON DATABASE BANK_DB TO ROLE BRANCH_MANAGER_JKT;
GRANT USAGE ON DATABASE BANK_DB TO ROLE BRANCH_MANAGER_SBY;
GRANT USAGE ON DATABASE BANK_DB TO ROLE BRANCH_MANAGER_BDG;
GRANT USAGE ON DATABASE BANK_DB TO ROLE DATA_ANALYST;
GRANT USAGE ON DATABASE BANK_DB TO ROLE RISK_ANALYST;
GRANT USAGE ON DATABASE BANK_DB TO ROLE TELLER_ROLE;

-- Schema access - RAW_DATA
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE BANK_ADMIN;
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE COMPLIANCE_OFFICER;
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE BRANCH_MANAGER_JKT;
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE BRANCH_MANAGER_SBY;
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE BRANCH_MANAGER_BDG;
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE DATA_ANALYST;
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE RISK_ANALYST;
GRANT USAGE ON SCHEMA BANK_DB.RAW_DATA TO ROLE TELLER_ROLE;

-- Schema access - ANALYTICS
GRANT USAGE ON SCHEMA BANK_DB.ANALYTICS TO ROLE BANK_ADMIN;
GRANT USAGE ON SCHEMA BANK_DB.ANALYTICS TO ROLE COMPLIANCE_OFFICER;
GRANT USAGE ON SCHEMA BANK_DB.ANALYTICS TO ROLE DATA_ANALYST;
GRANT USAGE ON SCHEMA BANK_DB.ANALYTICS TO ROLE RISK_ANALYST;

-- Table-level SELECT privileges
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE BANK_ADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE COMPLIANCE_OFFICER;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE BRANCH_MANAGER_JKT;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE BRANCH_MANAGER_SBY;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE BRANCH_MANAGER_BDG;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE DATA_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE RISK_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.RAW_DATA TO ROLE TELLER_ROLE;

GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.ANALYTICS TO ROLE BANK_ADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.ANALYTICS TO ROLE COMPLIANCE_OFFICER;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.ANALYTICS TO ROLE DATA_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA BANK_DB.ANALYTICS TO ROLE RISK_ANALYST;
```

### Step 1.4: Buat Mapping Table untuk Row Access Policy

```sql
-- ============================================
-- STEP 1.4: Mapping Table - Role <-> Region
-- ============================================
USE SCHEMA BANK_DB.RAW_DATA;

CREATE OR REPLACE TABLE ROLE_REGION_MAPPING (
    role_name VARCHAR(50),
    region VARCHAR(100)
);

INSERT INTO ROLE_REGION_MAPPING VALUES
    ('BRANCH_MANAGER_JKT', 'Region Jakarta'),
    ('BRANCH_MANAGER_SBY', 'Region Jawa Timur'),
    ('BRANCH_MANAGER_BDG', 'Region Jawa Barat');

-- Verifikasi
SELECT * FROM ROLE_REGION_MAPPING;

-- Grant SELECT ke semua role yang membutuhkan
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE BANK_ADMIN;
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE COMPLIANCE_OFFICER;
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE BRANCH_MANAGER_JKT;
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE BRANCH_MANAGER_SBY;
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE BRANCH_MANAGER_BDG;
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE DATA_ANALYST;
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE RISK_ANALYST;
GRANT SELECT ON TABLE ROLE_REGION_MAPPING TO ROLE TELLER_ROLE;
```

### Step 1.5: Verifikasi Setup

```sql
-- Verifikasi role hierarchy
SHOW ROLES LIKE 'BANK%';
SHOW ROLES LIKE 'BRANCH%';
SHOW ROLES LIKE 'DATA%';
SHOW ROLES LIKE 'RISK%';
SHOW ROLES LIKE 'TELLER%';
SHOW ROLES LIKE 'COMPLIANCE%';

-- Verifikasi grants
SHOW GRANTS TO ROLE DATA_ANALYST;
```

---

## Part 2: Data Masking Policies

### Step 2.1: Masking Policy - NIK (Partial Mask)

> **Skenario:** Kolom NIK/KTP harus di-mask untuk analyst dan teller.
> - COMPLIANCE_OFFICER & BANK_ADMIN: lihat full NIK → `3275012345670001`
> - BRANCH_MANAGER: partial mask → `3275XXXXXXXX0001`
> - DATA_ANALYST & RISK_ANALYST: heavy mask → `XXXXXXXXXXXXXXXX`
> - TELLER: heavy mask → `XXXXXXXXXXXXXXXX`

```sql
-- ============================================
-- STEP 2.1: Masking Policy - NIK
-- ============================================
USE ROLE ACCOUNTADMIN;
USE SCHEMA BANK_DB.RAW_DATA;

CREATE OR REPLACE MASKING POLICY mask_nik AS (val STRING) RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER')
            THEN val
        WHEN CURRENT_ROLE() IN ('BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN LEFT(val, 4) || 'XXXXXXXX' || RIGHT(val, 4)
        ELSE 'XXXXXXXXXXXXXXXX'
    END;

-- Apply ke kolom NIK pada tabel DIM_NASABAH
ALTER TABLE DIM_NASABAH MODIFY COLUMN nik SET MASKING POLICY mask_nik;
```

### Step 2.2: Masking Policy - Nama Nasabah (Conditional)

> **Skenario:** Nama nasabah sensitif sesuai UU PDP.
> - COMPLIANCE_OFFICER & BANK_ADMIN: full name → `Ahmad Pratama`
> - BRANCH_MANAGER: full name → `Ahmad Pratama`
> - DATA_ANALYST & RISK_ANALYST: initial only → `A******* P******`
> - TELLER: full mask → `*** CONFIDENTIAL ***`

```sql
-- ============================================
-- STEP 2.2: Masking Policy - Nama Nasabah
-- ============================================
CREATE OR REPLACE MASKING POLICY mask_nama AS (val STRING) RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER',
                                 'BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN val
        WHEN CURRENT_ROLE() IN ('DATA_ANALYST', 'RISK_ANALYST')
            THEN REGEXP_REPLACE(val, '([A-Za-z])([A-Za-z]+)', '\\1*****')
        ELSE '*** CONFIDENTIAL ***'
    END;

ALTER TABLE DIM_NASABAH MODIFY COLUMN nama_lengkap SET MASKING POLICY mask_nama;
```

### Step 2.3: Masking Policy - No HP

> **Skenario:** Nomor HP adalah data PII yang dilindungi UU PDP.
> - COMPLIANCE_OFFICER & BANK_ADMIN: full → `081234567890`
> - BRANCH_MANAGER: partial → `0812****7890`
> - Lainnya: full mask → `xxxxxxxxxxxx`

```sql
-- ============================================
-- STEP 2.3: Masking Policy - No HP
-- ============================================
CREATE OR REPLACE MASKING POLICY mask_phone AS (val STRING) RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER')
            THEN val
        WHEN CURRENT_ROLE() IN ('BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN LEFT(val, 4) || '****' || RIGHT(val, 4)
        ELSE 'xxxxxxxxxxxx'
    END;

ALTER TABLE DIM_NASABAH MODIFY COLUMN no_hp SET MASKING POLICY mask_phone;
```

### Step 2.4: Masking Policy - Email

```sql
-- ============================================
-- STEP 2.4: Masking Policy - Email
-- ============================================
CREATE OR REPLACE MASKING POLICY mask_email AS (val STRING) RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER')
            THEN val
        WHEN CURRENT_ROLE() IN ('BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN REGEXP_REPLACE(val, '^(.{2})(.*)(@.*)', '\\1****\\3')
        ELSE '****@****.***'
    END;

ALTER TABLE DIM_NASABAH MODIFY COLUMN email SET MASKING POLICY mask_email;
```

### Step 2.5: Masking Policy - Saldo (Range Masking)

> **Skenario:** Saldo nasabah sangat sensitif. Analyst hanya boleh lihat range.
> - COMPLIANCE_OFFICER, BANK_ADMIN, BRANCH_MANAGER: exact amount
> - DATA_ANALYST, RISK_ANALYST: range bucket (contoh: `Rp 10jt - 50jt`)
> - TELLER: `0` (tidak boleh lihat saldo)

```sql
-- ============================================
-- STEP 2.5: Masking Policy - Saldo (Range)
-- ============================================
CREATE OR REPLACE MASKING POLICY mask_saldo AS (val NUMBER) RETURNS NUMBER ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER',
                                 'BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN val
        WHEN CURRENT_ROLE() IN ('DATA_ANALYST', 'RISK_ANALYST')
            THEN CASE
                WHEN val < 1000000 THEN 500000
                WHEN val < 10000000 THEN 5000000
                WHEN val < 50000000 THEN 25000000
                WHEN val < 100000000 THEN 75000000
                WHEN val < 500000000 THEN 250000000
                WHEN val < 1000000000 THEN 750000000
                ELSE 1000000000
            END
        ELSE 0
    END;

ALTER TABLE FACT_SIMPANAN MODIFY COLUMN saldo SET MASKING POLICY mask_saldo;
```

### Step 2.6: Masking Policy - Penghasilan

```sql
-- ============================================
-- STEP 2.6: Masking Policy - Penghasilan
-- ============================================
CREATE OR REPLACE MASKING POLICY mask_penghasilan AS (val NUMBER) RETURNS NUMBER ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER',
                                 'BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN val
        WHEN CURRENT_ROLE() IN ('DATA_ANALYST', 'RISK_ANALYST')
            THEN ROUND(val, -6)
        ELSE 0
    END;

ALTER TABLE DIM_NASABAH MODIFY COLUMN penghasilan_bulanan SET MASKING POLICY mask_penghasilan;
```

### Step 2.7: Verifikasi Masking Policies

```sql
-- Lihat semua masking policies
SHOW MASKING POLICIES IN SCHEMA BANK_DB.RAW_DATA;

-- Lihat policy references (kolom mana yang pakai policy apa)
SELECT *
FROM TABLE(INFORMATION_SCHEMA.POLICY_REFERENCES(
    POLICY_NAME => 'BANK_DB.RAW_DATA.MASK_NIK'
));
```

---

## Part 3: Row Access Policy (Branch Segregation)

### Step 3.1: Buat Row Access Policy

> **Skenario:** Setiap Branch Manager hanya bisa melihat nasabah di region-nya.
> - BRANCH_MANAGER_JKT → hanya lihat nasabah dari cabang di Region Jakarta
> - BRANCH_MANAGER_SBY → hanya lihat nasabah dari cabang di Region Jawa Timur
> - BRANCH_MANAGER_BDG → hanya lihat nasabah dari cabang di Region Jawa Barat
> - COMPLIANCE_OFFICER, BANK_ADMIN → lihat semua
> - DATA_ANALYST, RISK_ANALYST → lihat semua (tapi data PII sudah di-mask)
> - TELLER → tidak bisa lihat sama sekali

```sql
-- ============================================
-- STEP 3.1: Row Access Policy pada DIM_NASABAH
-- ============================================
USE ROLE ACCOUNTADMIN;
USE SCHEMA BANK_DB.RAW_DATA;

CREATE OR REPLACE ROW ACCESS POLICY rap_branch_segregation
    AS (cabang_id_val VARCHAR) RETURNS BOOLEAN ->
    CASE
        -- Admin & Compliance bisa lihat semua
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER')
            THEN TRUE
        -- Analyst bisa lihat semua (data PII sudah di-mask)
        WHEN CURRENT_ROLE() IN ('DATA_ANALYST', 'RISK_ANALYST')
            THEN TRUE
        -- Branch Manager hanya lihat region-nya
        WHEN CURRENT_ROLE() IN ('BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN EXISTS (
                SELECT 1
                FROM ROLE_REGION_MAPPING rrm
                JOIN DIM_CABANG dc ON dc.region = rrm.region
                WHERE rrm.role_name = CURRENT_ROLE()
                  AND dc.cabang_id = cabang_id_val
            )
        -- Teller tidak bisa lihat data nasabah
        ELSE FALSE
    END;

-- Apply ke DIM_NASABAH
ALTER TABLE DIM_NASABAH ADD ROW ACCESS POLICY rap_branch_segregation ON (cabang_id);
```

### Step 3.2: Row Access Policy pada FACT Tables

```sql
-- ============================================
-- STEP 3.2: Row Access Policy pada FACT_TRANSAKSI
-- ============================================

-- Untuk FACT_TRANSAKSI: filter berdasarkan nasabah_id yang terhubung ke cabang
CREATE OR REPLACE ROW ACCESS POLICY rap_transaksi_by_branch
    AS (nasabah_id_val VARCHAR) RETURNS BOOLEAN ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER',
                                 'DATA_ANALYST', 'RISK_ANALYST')
            THEN TRUE
        WHEN CURRENT_ROLE() IN ('BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN EXISTS (
                SELECT 1
                FROM DIM_NASABAH dn
                JOIN DIM_CABANG dc ON dn.cabang_id = dc.cabang_id
                JOIN ROLE_REGION_MAPPING rrm ON dc.region = rrm.region
                WHERE rrm.role_name = CURRENT_ROLE()
                  AND dn.nasabah_id = nasabah_id_val
            )
        ELSE FALSE
    END;

ALTER TABLE FACT_TRANSAKSI ADD ROW ACCESS POLICY rap_transaksi_by_branch ON (nasabah_id);

-- Apply policy yang sama ke FACT_KREDIT dan FACT_SIMPANAN
ALTER TABLE FACT_KREDIT ADD ROW ACCESS POLICY rap_transaksi_by_branch ON (nasabah_id);
ALTER TABLE FACT_SIMPANAN ADD ROW ACCESS POLICY rap_transaksi_by_branch ON (nasabah_id);
```

### Step 3.3: Verifikasi Row Access Policy

```sql
-- Lihat semua row access policies
SHOW ROW ACCESS POLICIES IN SCHEMA BANK_DB.RAW_DATA;
```

---

## Part 4: Projection Policy (Anti Bulk Extraction)

### Step 4.1: Buat Projection Policy

> **Skenario:** Sesuai UU PDP, data PII tidak boleh di-extract dalam bulk.
> Kolom NIK tidak bisa di-SELECT kecuali ada filter WHERE clause yang spesifik.
> Hanya COMPLIANCE_OFFICER dan BANK_ADMIN yang bisa bulk select.

```sql
-- ============================================
-- STEP 4.1: Projection Policy - Anti Bulk Extraction
-- ============================================
USE ROLE ACCOUNTADMIN;
USE SCHEMA BANK_DB.RAW_DATA;

CREATE OR REPLACE PROJECTION POLICY pp_restrict_pii_columns
    AS () RETURNS PROJECTION_CONSTRAINT ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER')
            THEN PROJECTION_CONSTRAINT(ALLOW => TRUE)
        ELSE PROJECTION_CONSTRAINT(ALLOW => FALSE)
    END;

-- Apply ke kolom NIK (data PII paling sensitif)
ALTER TABLE DIM_NASABAH MODIFY COLUMN nik
    SET PROJECTION POLICY pp_restrict_pii_columns;

-- Apply ke kolom email
ALTER TABLE DIM_NASABAH MODIFY COLUMN email
    SET PROJECTION POLICY pp_restrict_pii_columns;
```

### Step 4.2: Verifikasi Projection Policy

```sql
SHOW PROJECTION POLICIES IN SCHEMA BANK_DB.RAW_DATA;
```

---

## Part 5: Tag-Based Masking (Automated PII Protection)

### Step 5.1: Buat Tags

> **Skenario:** Buat tag `PII_TYPE` untuk mengklasifikasikan kolom.
> Ketika kolom ditandai dengan tag PII, masking policy otomatis ter-apply.

```sql
-- ============================================
-- STEP 5.1: Buat Tags untuk Klasifikasi Data
-- ============================================
USE ROLE ACCOUNTADMIN;
USE SCHEMA BANK_DB.RAW_DATA;

CREATE OR REPLACE TAG PII_TYPE
    ALLOWED_VALUES 'IDENTIFIER', 'PHONE', 'EMAIL', 'FINANCIAL', 'NAME'
    COMMENT = 'Tag untuk mengklasifikasikan jenis data PII sesuai UU PDP';

CREATE OR REPLACE TAG DATA_SENSITIVITY
    ALLOWED_VALUES 'HIGH', 'MEDIUM', 'LOW', 'PUBLIC'
    COMMENT = 'Tingkat sensitivitas data';
```

### Step 5.2: Apply Tags ke Kolom

```sql
-- ============================================
-- STEP 5.2: Tag Kolom-kolom PII
-- ============================================

-- DIM_NASABAH
ALTER TABLE DIM_NASABAH MODIFY COLUMN nik SET TAG PII_TYPE = 'IDENTIFIER';
ALTER TABLE DIM_NASABAH MODIFY COLUMN nik SET TAG DATA_SENSITIVITY = 'HIGH';

ALTER TABLE DIM_NASABAH MODIFY COLUMN nama_lengkap SET TAG PII_TYPE = 'NAME';
ALTER TABLE DIM_NASABAH MODIFY COLUMN nama_lengkap SET TAG DATA_SENSITIVITY = 'HIGH';

ALTER TABLE DIM_NASABAH MODIFY COLUMN no_hp SET TAG PII_TYPE = 'PHONE';
ALTER TABLE DIM_NASABAH MODIFY COLUMN no_hp SET TAG DATA_SENSITIVITY = 'HIGH';

ALTER TABLE DIM_NASABAH MODIFY COLUMN email SET TAG PII_TYPE = 'EMAIL';
ALTER TABLE DIM_NASABAH MODIFY COLUMN email SET TAG DATA_SENSITIVITY = 'MEDIUM';

ALTER TABLE DIM_NASABAH MODIFY COLUMN penghasilan_bulanan SET TAG PII_TYPE = 'FINANCIAL';
ALTER TABLE DIM_NASABAH MODIFY COLUMN penghasilan_bulanan SET TAG DATA_SENSITIVITY = 'HIGH';

-- FACT_SIMPANAN
ALTER TABLE FACT_SIMPANAN MODIFY COLUMN saldo SET TAG PII_TYPE = 'FINANCIAL';
ALTER TABLE FACT_SIMPANAN MODIFY COLUMN saldo SET TAG DATA_SENSITIVITY = 'HIGH';
```

### Step 5.3: Buat Tag-Based Masking Policy

```sql
-- ============================================
-- STEP 5.3: Tag-Based Masking Policy
-- ============================================

-- Masking policy otomatis untuk tag PII_TYPE = 'IDENTIFIER'
CREATE OR REPLACE MASKING POLICY mask_tag_identifier AS (val STRING) RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'BANK_ADMIN', 'COMPLIANCE_OFFICER')
            THEN val
        WHEN CURRENT_ROLE() IN ('BRANCH_MANAGER_JKT', 'BRANCH_MANAGER_SBY', 'BRANCH_MANAGER_BDG')
            THEN LEFT(val, 4) || 'XXXXXXXX' || RIGHT(val, 4)
        ELSE 'XXXXXXXXXXXXXXXX'
    END;

-- Assign masking policy ke tag (bukan ke kolom individu)
-- Semua kolom dengan tag PII_TYPE = 'IDENTIFIER' otomatis ter-mask
ALTER TAG PII_TYPE SET MASKING POLICY mask_tag_identifier;
```

> **Catatan:** Tag-based masking hanya bisa digunakan jika kolom belum memiliki
> masking policy yang di-assign langsung. Karena kita sudah apply masking policy
> langsung di Part 2, tag-based masking ini berfungsi sebagai demonstrasi konsep.
> Dalam production, pilih salah satu: direct assignment ATAU tag-based.

### Step 5.4: Verifikasi Tags

```sql
-- Lihat semua tags
SHOW TAGS IN SCHEMA BANK_DB.RAW_DATA;

-- Lihat tag references pada tabel tertentu
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES(
    'BANK_DB.RAW_DATA.DIM_NASABAH',
    'TABLE'
));

-- Lihat kolom mana saja yang punya tag PII_TYPE
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
    'BANK_DB.RAW_DATA.DIM_NASABAH',
    'TABLE'
));
```

---

## Part 6: Testing - Switch Role & Verifikasi

> **Ini adalah bagian AHA MOMENT!**
> Jalankan query yang sama dengan role yang berbeda, perhatikan hasilnya berbeda.

### Test 6.1: COMPLIANCE_OFFICER (Lihat Semua)

```sql
-- ============================================
-- TEST 6.1: COMPLIANCE_OFFICER - Full Access
-- ============================================
USE ROLE COMPLIANCE_OFFICER;
USE WAREHOUSE BANK_WH;
USE SCHEMA BANK_DB.RAW_DATA;

-- Query 1: Lihat data nasabah
-- Expected: SEMUA data terlihat, SEMUA kolom tanpa mask
SELECT
    nasabah_id,
    nama_lengkap,
    nik,
    no_hp,
    email,
    segmen_nasabah,
    penghasilan_bulanan
FROM DIM_NASABAH
LIMIT 10;

-- Query 2: Count semua nasabah (harusnya 10,000)
SELECT COUNT(*) AS total_nasabah FROM DIM_NASABAH;

-- Query 3: Lihat saldo simpanan (harusnya exact amount)
SELECT
    s.simpanan_id,
    n.nama_lengkap,
    s.jenis_simpanan,
    s.saldo
FROM FACT_SIMPANAN s
JOIN DIM_NASABAH n ON s.nasabah_id = n.nasabah_id
LIMIT 10;
```

### Test 6.2: BRANCH_MANAGER_JKT (Hanya Jakarta)

```sql
-- ============================================
-- TEST 6.2: BRANCH_MANAGER_JKT - Region Jakarta Only
-- ============================================
USE ROLE BRANCH_MANAGER_JKT;
USE WAREHOUSE BANK_WH;
USE SCHEMA BANK_DB.RAW_DATA;

-- Query 1: Lihat data nasabah
-- Expected:
--   - Hanya nasabah dari cabang di Region Jakarta yang muncul
--   - NIK: partial mask (3275XXXXXXXX0001)
--   - Nama: full (terlihat)
--   - No HP: partial mask (0812****7890)
--   - Email: partial mask (ah****@email.com)
SELECT
    nasabah_id,
    nama_lengkap,
    nik,
    no_hp,
    email,
    segmen_nasabah,
    penghasilan_bulanan
FROM DIM_NASABAH
LIMIT 10;

-- Query 2: Count nasabah (harusnya KURANG dari 10,000)
SELECT COUNT(*) AS total_nasabah_jakarta FROM DIM_NASABAH;

-- Query 3: Verifikasi hanya cabang Jakarta yang muncul
SELECT DISTINCT dc.region, dc.kota
FROM DIM_NASABAH dn
JOIN DIM_CABANG dc ON dn.cabang_id = dc.cabang_id
ORDER BY dc.region, dc.kota;

-- Query 4: Lihat transaksi (hanya transaksi nasabah Jakarta)
SELECT COUNT(*) AS total_transaksi_jakarta FROM FACT_TRANSAKSI;

-- Query 5: Lihat kredit (hanya kredit nasabah Jakarta)
SELECT
    jenis_kredit,
    COUNT(*) AS jumlah,
    SUM(outstanding) AS total_outstanding
FROM FACT_KREDIT
GROUP BY jenis_kredit
ORDER BY total_outstanding DESC;
```

### Test 6.3: BRANCH_MANAGER_SBY (Hanya Jawa Timur)

```sql
-- ============================================
-- TEST 6.3: BRANCH_MANAGER_SBY - Region Jawa Timur Only
-- ============================================
USE ROLE BRANCH_MANAGER_SBY;
USE WAREHOUSE BANK_WH;
USE SCHEMA BANK_DB.RAW_DATA;

-- Query 1: Count nasabah (harusnya berbeda dari Jakarta)
SELECT COUNT(*) AS total_nasabah_jatim FROM DIM_NASABAH;

-- Query 2: Verifikasi hanya Jawa Timur
SELECT DISTINCT dc.region, dc.kota
FROM DIM_NASABAH dn
JOIN DIM_CABANG dc ON dn.cabang_id = dc.cabang_id
ORDER BY dc.region, dc.kota;

-- Query 3: Lihat data nasabah (perhatikan masking level-nya)
SELECT
    nasabah_id,
    nama_lengkap,
    nik,
    no_hp,
    email,
    penghasilan_bulanan
FROM DIM_NASABAH
LIMIT 10;
```

### Test 6.4: DATA_ANALYST (Semua Row, Data Ter-mask)

```sql
-- ============================================
-- TEST 6.4: DATA_ANALYST - All Rows, Masked PII
-- ============================================
USE ROLE DATA_ANALYST;
USE WAREHOUSE BANK_WH;
USE SCHEMA BANK_DB.RAW_DATA;

-- Query 1: Lihat data nasabah
-- Expected:
--   - SEMUA nasabah muncul (10,000)
--   - NIK: full mask (XXXXXXXXXXXXXXXX)
--   - Nama: initial mask (A***** P*****)
--   - No HP: full mask (xxxxxxxxxxxx)
--   - Email: full mask (****@****.***) 
--   - Penghasilan: rounded to nearest million
SELECT
    nasabah_id,
    nama_lengkap,
    nik,
    no_hp,
    email,
    segmen_nasabah,
    penghasilan_bulanan
FROM DIM_NASABAH
LIMIT 10;

-- Query 2: Count (harusnya 10,000 - analyst lihat semua row)
SELECT COUNT(*) AS total_nasabah FROM DIM_NASABAH;

-- Query 3: Analyst bisa aggregate data tanpa lihat PII
SELECT
    segmen_nasabah,
    COUNT(*) AS jumlah_nasabah,
    AVG(penghasilan_bulanan) AS avg_penghasilan
FROM DIM_NASABAH
GROUP BY segmen_nasabah
ORDER BY jumlah_nasabah DESC;

-- Query 4: Saldo di-mask jadi range bucket
SELECT
    jenis_simpanan,
    COUNT(*) AS jumlah,
    SUM(saldo) AS total_saldo
FROM FACT_SIMPANAN
GROUP BY jenis_simpanan;

-- Query 5: NPL Analysis (data kredit tetap bisa dianalisis)
SELECT
    status_kolektibilitas,
    COUNT(*) AS jumlah,
    SUM(outstanding) AS total_outstanding
FROM FACT_KREDIT
GROUP BY status_kolektibilitas
ORDER BY status_kolektibilitas;
```

### Test 6.5: TELLER_ROLE (Akses Sangat Terbatas)

```sql
-- ============================================
-- TEST 6.5: TELLER_ROLE - Very Limited Access
-- ============================================
USE ROLE TELLER_ROLE;
USE WAREHOUSE BANK_WH;
USE SCHEMA BANK_DB.RAW_DATA;

-- Query 1: Lihat data nasabah
-- Expected:
--   - TIDAK ADA row yang muncul (row access policy return FALSE)
--   - Atau jika ada row, semua PII fully masked
SELECT
    nasabah_id,
    nama_lengkap,
    nik,
    no_hp,
    email,
    penghasilan_bulanan
FROM DIM_NASABAH
LIMIT 10;

-- Query 2: Count (harusnya 0)
SELECT COUNT(*) AS total_nasabah FROM DIM_NASABAH;

-- Query 3: Transaksi juga 0
SELECT COUNT(*) AS total_transaksi FROM FACT_TRANSAKSI;
```

### Test 6.6: Projection Policy Test

```sql
-- ============================================
-- TEST 6.6: Projection Policy - Anti Bulk Extract
-- ============================================

-- Test sebagai DATA_ANALYST
USE ROLE DATA_ANALYST;
USE WAREHOUSE BANK_WH;
USE SCHEMA BANK_DB.RAW_DATA;

-- Query 1: Coba SELECT kolom NIK
-- Expected: ERROR karena projection policy melarang DATA_ANALYST select NIK
SELECT nasabah_id, nik FROM DIM_NASABAH LIMIT 5;

-- Query 2: SELECT tanpa kolom NIK -> BERHASIL
SELECT nasabah_id, segmen_nasabah, pekerjaan FROM DIM_NASABAH LIMIT 5;

-- Query 3: SELECT kolom email -> ERROR (juga dilindungi projection policy)
SELECT nasabah_id, email FROM DIM_NASABAH LIMIT 5;

-- Sekarang test sebagai COMPLIANCE_OFFICER
USE ROLE COMPLIANCE_OFFICER;

-- Query 4: COMPLIANCE bisa SELECT NIK -> BERHASIL
SELECT nasabah_id, nik, email FROM DIM_NASABAH LIMIT 5;
```

### Test 6.7: Comparison Table (Ringkasan)

> Jalankan query berikut dengan setiap role untuk melihat perbedaan:

```sql
-- ============================================
-- TEST 6.7: Side-by-Side Comparison
-- ============================================

-- Ganti USE ROLE sesuai role yang ingin ditest
-- USE ROLE COMPLIANCE_OFFICER;
-- USE ROLE BRANCH_MANAGER_JKT;
-- USE ROLE DATA_ANALYST;
-- USE ROLE TELLER_ROLE;

USE WAREHOUSE BANK_WH;
USE SCHEMA BANK_DB.RAW_DATA;

SELECT
    CURRENT_ROLE() AS current_role,
    COUNT(*) AS visible_rows
FROM DIM_NASABAH;
```

**Expected Results:**

| Role | Visible Rows | NIK | Nama | No HP | Email | Saldo | Penghasilan |
|------|-------------|-----|------|-------|-------|-------|-------------|
| COMPLIANCE_OFFICER | 10,000 | Full | Full | Full | Full | Exact | Exact |
| BANK_ADMIN | 10,000 | Full | Full | Full | Full | Exact | Exact |
| BRANCH_MANAGER_JKT | ~2,500* | Partial | Full | Partial | Partial | Exact | Exact |
| BRANCH_MANAGER_SBY | ~1,200* | Partial | Full | Partial | Partial | Exact | Exact |
| BRANCH_MANAGER_BDG | ~1,500* | Partial | Full | Partial | Partial | Exact | Exact |
| DATA_ANALYST | 10,000 | Full Mask | Initial | Full Mask | Full Mask | Range | Rounded |
| RISK_ANALYST | 10,000 | Full Mask | Initial | Full Mask | Full Mask | Range | Rounded |
| TELLER_ROLE | 0 | - | - | - | - | - | - |

*\*Jumlah bervariasi tergantung distribusi data ke cabang/region*

---

## Ringkasan: Mapping ke Regulasi

| Fitur Snowflake | Kebutuhan Regulasi | Penjelasan |
|----------------|-------------------|------------|
| **Masking Policy** | UU PDP Pasal 16 - Pemrosesan Data Pribadi | Data PII hanya bisa dilihat oleh pihak berwenang |
| **Row Access Policy** | POJK Tata Kelola TI - Segregation of Duties | Branch Manager hanya akses data region-nya |
| **Projection Policy** | UU PDP Pasal 25 - Pembatasan Pemrosesan | Mencegah bulk extraction data nasabah |
| **Tag-Based Masking** | UU PDP Pasal 21 - Klasifikasi Data | Otomatis proteksi berdasarkan klasifikasi PII |
| **Role Hierarchy** | POJK - Least Privilege Principle | Setiap role hanya mendapat akses minimum yang diperlukan |

---

## Cleanup (Opsional - Setelah Workshop)

```sql
-- Hapus policies
USE ROLE ACCOUNTADMIN;
USE SCHEMA BANK_DB.RAW_DATA;

ALTER TABLE DIM_NASABAH MODIFY COLUMN nik UNSET MASKING POLICY;
ALTER TABLE DIM_NASABAH MODIFY COLUMN nama_lengkap UNSET MASKING POLICY;
ALTER TABLE DIM_NASABAH MODIFY COLUMN no_hp UNSET MASKING POLICY;
ALTER TABLE DIM_NASABAH MODIFY COLUMN email UNSET MASKING POLICY;
ALTER TABLE DIM_NASABAH MODIFY COLUMN penghasilan_bulanan UNSET MASKING POLICY;
ALTER TABLE FACT_SIMPANAN MODIFY COLUMN saldo UNSET MASKING POLICY;

ALTER TABLE DIM_NASABAH DROP ROW ACCESS POLICY rap_branch_segregation;
ALTER TABLE FACT_TRANSAKSI DROP ROW ACCESS POLICY rap_transaksi_by_branch;
ALTER TABLE FACT_KREDIT DROP ROW ACCESS POLICY rap_transaksi_by_branch;
ALTER TABLE FACT_SIMPANAN DROP ROW ACCESS POLICY rap_transaksi_by_branch;

ALTER TABLE DIM_NASABAH MODIFY COLUMN nik UNSET PROJECTION POLICY;
ALTER TABLE DIM_NASABAH MODIFY COLUMN email UNSET PROJECTION POLICY;

DROP MASKING POLICY IF EXISTS mask_nik;
DROP MASKING POLICY IF EXISTS mask_nama;
DROP MASKING POLICY IF EXISTS mask_phone;
DROP MASKING POLICY IF EXISTS mask_email;
DROP MASKING POLICY IF EXISTS mask_saldo;
DROP MASKING POLICY IF EXISTS mask_penghasilan;
DROP MASKING POLICY IF EXISTS mask_tag_identifier;
DROP ROW ACCESS POLICY IF EXISTS rap_branch_segregation;
DROP ROW ACCESS POLICY IF EXISTS rap_transaksi_by_branch;
DROP PROJECTION POLICY IF EXISTS pp_restrict_pii_columns;
DROP TAG IF EXISTS PII_TYPE;
DROP TAG IF EXISTS DATA_SENSITIVITY;

DROP ROLE IF EXISTS BANK_ADMIN;
DROP ROLE IF EXISTS COMPLIANCE_OFFICER;
DROP ROLE IF EXISTS BRANCH_MANAGER_JKT;
DROP ROLE IF EXISTS BRANCH_MANAGER_SBY;
DROP ROLE IF EXISTS BRANCH_MANAGER_BDG;
DROP ROLE IF EXISTS DATA_ANALYST;
DROP ROLE IF EXISTS RISK_ANALYST;
DROP ROLE IF EXISTS TELLER_ROLE;
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Masking policy conflict | Satu kolom hanya bisa punya 1 masking policy (direct) ATAU tag-based, tidak keduanya |
| Row access policy lambat | Pastikan mapping table tidak terlalu besar, gunakan index/cluster jika perlu |
| Projection policy error | Projection policy hanya mencegah SELECT kolom tersebut, bukan filter |
| "Insufficient privileges" | Pastikan GRANT USAGE pada warehouse, database, dan schema sudah benar |
| Role tidak muncul | Pastikan role sudah di-create dan di-grant ke user yang sedang login |

---

**Selamat! Anda telah berhasil mengimplementasikan Data Protection Policies untuk melindungi data nasabah sesuai regulasi OJK & UU PDP.**
