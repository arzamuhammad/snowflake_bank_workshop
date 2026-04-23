-- =============================================================================
-- Snowflake Notebook Service Setup for Bank Workshop
-- =============================================================================
-- Purpose: Provision GPU compute pool + PyPI access integration to power the
--          BANK_SERVICE_1 notebook service used by credit_scoring_ml.ipynb.
--
-- After running this script, complete the setup in Snowsight:
--   1. Open Snowsight -> Notebooks
--   2. Upload snowflake_bank_workshop/day2-session3-ml/credit_scoring_ml.ipynb
--   3. When prompted to "Connect to a service", select:
--        - Runtime                     : Run on container (GPU)
--        - Compute Pool                : GPU_POOL_S
--        - External Access Integration : BANK_PYPI_ACCESS_INTEGRATION
--        - Service Name                : BANK_SERVICE_1
--   4. (Optional) First notebook cell to refresh ML libs:
--        !pip install --upgrade snowflake-ml-python
-- =============================================================================

USE ROLE ACCOUNTADMIN;

-- -----------------------------------------------------------------------------
-- Step 1: Create GPU compute pool (GPU_NV_S)
-- -----------------------------------------------------------------------------
CREATE COMPUTE POOL IF NOT EXISTS GPU_POOL_S
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = GPU_NV_S
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 3600
    COMMENT = 'GPU compute pool (GPU_NV_S) for Bank ML notebook service';

-- -----------------------------------------------------------------------------
-- Step 2: Create PyPI network rule + external access integration
-- -----------------------------------------------------------------------------
USE DATABASE BANK_DB;
USE SCHEMA PUBLIC;

CREATE OR REPLACE NETWORK RULE BANK_DB.PUBLIC.PYPI_NETWORK_RULE
    TYPE = HOST_PORT
    MODE = EGRESS
    VALUE_LIST = ('pypi.org', 'pypi.python.org', 'pythonhosted.org', 'files.pythonhosted.org')
    COMMENT = 'Allow egress to PyPI for Bank ML notebooks';

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION BANK_PYPI_ACCESS_INTEGRATION
    ALLOWED_NETWORK_RULES = (BANK_DB.PUBLIC.PYPI_NETWORK_RULE)
    ENABLED = TRUE
    COMMENT = 'PyPI access for BANK_SERVICE_1 notebook service';

-- -----------------------------------------------------------------------------
-- Step 3: Grant usage
-- -----------------------------------------------------------------------------
GRANT USAGE ON COMPUTE POOL GPU_POOL_S TO ROLE ACCOUNTADMIN;
GRANT USAGE ON INTEGRATION BANK_PYPI_ACCESS_INTEGRATION TO ROLE ACCOUNTADMIN;

-- -----------------------------------------------------------------------------
-- Step 4: Resume compute pool so it is ready for the notebook service
-- -----------------------------------------------------------------------------
ALTER COMPUTE POOL GPU_POOL_S RESUME;

-- -----------------------------------------------------------------------------
-- Verification
-- -----------------------------------------------------------------------------
SHOW COMPUTE POOLS LIKE 'GPU_POOL_S';
SHOW EXTERNAL ACCESS INTEGRATIONS LIKE 'BANK_PYPI_ACCESS_INTEGRATION';
