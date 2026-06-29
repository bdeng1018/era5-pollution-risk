# ERA5 Pollution‑Risk Pipeline (Branch 1 MVP)

Branch 1 delivers a **minimal**, **production‑aligned**, and **intentionally 
scoped** foundation for ERA5 ingestion, preprocessing, and exploratory 
pollution‑risk analytics. It focuses on building the **core engineering 
architecture** that Branch 2 will scale into a multi‑year, feature‑rich 
pipeline.

This MVP emphasizes **clarity**, **modularity**, and **reproducibility**. It 
includes only the essential components required to validate ingestion, 
preprocessing, feature building, baseline modeling, and evaluation for a *single 
month* of ERA5 data and a **single key variable**. Advanced systems—such as 
metadata tracking, schema validation, multi‑year ingestion, feature dependency 
graphs, MLflow experiment tracking, Docker containerization, and CI/CD—are 
**deliberately deferred** to Branch 2.

Branch 1 proves that the pipeline structure, config‑driven design, Makefile 
orchestration, and preprocessing logic are **correct**, **stable**, and **ready 
for expansion**. It mirrors modern engineering patterns used across climate 
analytics, utilities, finance, healthcare, aerospace, and other data‑intensive 
domains.

---

## 🧱 Design principles (Branch 1)

- **Modularity:** Each stage is isolated, testable, and import‑safe.  
- **Config‑driven behavior:** End‑users modify YAML files, not Python code.  
- **Reproducibility:** Makefile orchestrates deterministic execution.  
- **Minimalism:** Only essential components included; no premature complexity.  
- **Scalability:** Architecture designed for Branch 2 expansion.  
- **Clarity:** Pipeline stages mirror real MLOps patterns used in industry.

---

## 📦 Project structure

```markdown
era5-pollution-risk/
├── configs/               # YAML configs (paths, variables, years, months, region)
├── data/
│   ├── raw/era5/          # ERA5 ZIP + GRIB files (ignored by Git)
│   ├── intermediate/      # Parquet files (ignored by Git)
│   ├── features/          # Engineered features
│   └── predictions/       # Model predictions
├── diagrams/              # Pipeline diagrams (Branch 1)
├── models/                # Baseline model artifacts
├── notebooks/             # EDA notebooks (Branch 1: branch1_eda.ipynb)
├── scripts/diagnostics/   # Developer utilities (e.g., test_cds.py)
├── src/
│   ├── utils/             # Logging, config loading, path resolution
│   ├── download_01/       # ERA5 download scripts (monthly + single-variable)
│   ├── preprocessing_02/  # GRIB → Parquet conversion
│   ├── features_03/       # Feature engineering (Branch 1: minimal)
│   ├── modeling_04/       # Baseline modeling (Branch 1: simple)
│   └── evaluation_05/     # Evaluation (Branch 1: basic metrics)
└── tests/                 # Smoke tests for Branch 1
```

---

## 🚀 Pipeline Overview (Branch 1)

Branch 1 implements a minimal but production‑aligned pipeline for a **single 
month** and a **single key variable** (e.g., 2m temperature):

1. **Download ERA5 (single variable)**  
   - Single‑level variable (e.g., `2m_temperature`)
   - One year (2023)  
   - One month (September)  
   - Outputs a **single-variable GRIB file** in `data/raw/era5/`
   - This file is required for Stages 2–5

2. **Preprocessing**  
   - Unzip GRIB archives (if needed)
   - Inspect GRIB metadata
   - Convert the single-variable GRIB → Parquet
   - Write `data/intermediate/2m_temperature_2023_09.parquet`
   - Perform lightweight schema checks

3. **Feature engineering**  
   - Build a small set of derived features from the single‑variable Parquet
   - Store features in `data/features/features.parquet`
   - Designed to be extended in Branch 2

4. **Modeling**  
   - Train a simple baseline model using engineered features
   - Store model artifacts in `models/model.pkl`
   - Serves as a foundation for more advanced models in Branch 2

5. **Evaluation**
   - Generate predictions and basic metrics
   - Store predictions in `data/predictions/predictions.parquet`
   - Establishes the evaluation pattern for future models

The pipeline is Makefile‑orchestrated, modular, and reproducible, enabling 
seamless scaling to multi‑year ingestion and advanced modeling in later 
branches.

---

## 📊 Diagrams

Branch 1 includes lightweight pipeline diagrams that illustrate the end‑to‑end 
flow without over‑engineering:

- `diagrams/pipeline.md` — Mermaid diagram rendered on GitHub  
- `diagrams/pipeline.txt` — ASCII diagram for quick terminal viewing  

These diagrams provide a clear visual summary of the Branch 1 architecture, 
showing how the single‑variable GRIB file moves through preprocessing, feature 
engineering, modeling, and evaluation.

---

## 🔥 Why September 2023?

Branch 1 uses **September 2023** as the initial month for ingestion and testing. 
This choice is intentional:

- Strong pollution‑risk signals in the LA Basin  
- Wildfire smoke → elevated **PM2.5**  
- Late‑summer **ozone peaks**
- Meteorological variability (heat, stagnation, wind events)  
- Realistic pipeline validation without requiring full 6‑year ingestion

This month provides a **representative, domain‑relevant slice** of ERA5 data 
ideal for validating ingestion, preprocessing, and baseline analytics.

---

## ⚙️ Configuration

All pipeline settings live in `configs/`:

- **[paths.yml](ca://s?q=Update_paths_yml)** — raw, intermediate, features, predictions directories 
- **[variables.yml](ca://s?q=Update_variables_yml)** — ERA5 variable list (Branch 1 focuses on a single key variable) 
- **[years.yml](ca://s?q=Update_years_yml)** — Branch 1 uses a single year 
- **[months.yml](ca://s?q=Update_months_yml)** — Branch 1 uses a single month 
- **[region.yml](ca://s?q=Add_region_yml)** — LA Basin bounding box 

### Do end‑users need to edit configs in Branch 1?

**Not to get started.**
Branch 1 ships with fully working defaults: 

 - year = 2023
 - month = 09
 - variables = minimal set (including the single key variable)
 - region = LA Basin

End‑users *may* edit configs if they want to: 

 - change the month or year
 - change the region
 - add/remove variables

But editing configs is **optional** for Branch 1; the pipeline runs 
out‑of‑the‑box with the provided settings. 

---

## 📁 Data Expectations (Branch 1)

Branch 1 operates on a **single ERA5 variable** for a **single month**.  
To run Stages 2–5 successfully, the following files **must exist** in `data/raw/era5/` before running the pipeline.

### Required files (Branch 1)

The pipeline requires **one single‑variable GRIB file** and its associated cfgrib index:

```markdown
data/raw/era5/2m_temperature_2023_09.grib
data/raw/era5/2m_temperature_2023_09.grib.<hash>.idx
```

Where:

- `<hash>` is an automatically generated alphanumeric identifier  
- Example:  
  `2m_temperature_2023_09.grib.5b7b6.idx`  
- The exact hash will differ on every machine and every download

These files are produced by:

```bash
python -m src.download_01.download_era5_single
```

This **single-variable GRIB** is the file used by: 

- Stage 02 — Preprocessing
- Stage 03 — Feature Engineering
- Stage 04 — Modeling
- Stage 05 — Evaluation
- Smoke Tests (`make test`)

Without this file, the pipeline **cannot** proceed past Stage 01.

### Optional files (not required for Branch 1)

The monthly ZIP + GRIB files downloaded via: 

```bash
make download
```

may appear in: 

```markdown
data/raw/era5/era5_2023_09.zip
data/raw/era5/era5_2023_09.grib
```

These are included for: 

- debugging
- exploratory analysis
- future Branch 2 multi‑variable ingestion

Branch 1 does **not** use these files in Stages 2–5. 

---

## 🧰 Developer diagnostics (`scripts/diagnostics/test_cds.py`)

Before running the pipeline, developers can optionally validate their 
environment using: 

```markdown
python scripts/diagnostics/test_cds.py
```

This script checks: 
 - `.cdsapirc` exists and is readable 
 - CDS API credentials are valid 
 - network connectivity to ECMWF 
 - `cdsapi` is installed correctly 
 - basic skip logic for downloads behaves as expected 

This script is **not** part of the numbered pipeline stages and is **not** 
included in the Makefile. 
It is a **developer‑only diagnostic tool** to ensure ERA5 downloads will succeed 
before running the download scripts or the full pipeline. 

---

## 🛠️ Download scripts (Stage 1 details)

Branch 1 includes two download scripts under `src/download_01/`:

 - `download_era5_monthly.py` — downloads a full monthly ZIP + GRIB for multiple variables 
 - `download_era5_single.py` — downloads a **single‑variable GRIB** for the key 
 variable used in Branch 1 

For the Branch 1 pipeline:

 - The **single‑variable GRIB** (e.g., `2m_temperature_2023_09.grib`) is the file used by Stages 2–5. 
 - The monthly ZIP/GRIB are present for future expansion and debugging but are 
 **not required** for the Branch 1 feature/model/evaluation flow. 

End‑users must ensure the single‑variable GRIB exists in `data/raw/era5/` before 
running the full pipeline. 

---

## 🛠️ Makefile Commands

The Makefile provides a simple interface: 

```markdown
make env         # Validate environment (packages, directories, configs)
make download    # Download ERA5 monthly data (ZIP + GRIB) via download_era5_monthly.py
make preprocess  # Unzip + inspect + convert GRIB → Parquet
make features    # Build minimal features from ERA5 data
make train       # Train a baseline model on features
make evaluate    # Evaluate the model and write predictions
make test        # Run smoke tests
make all         # Run the full pipeline (download → evaluate)
```

### Important note for Branch 1

Because Branch 1’s feature/model/evaluation stages are built around the 
**single‑variable GRIB**, end‑users should: 

1. Run environment validation (optional but recommended): 

```markdown
make env
```

2. Run the **single‑variable download** explicitly: 

```markdown
python -m src.download_01.download_era5_single
```

This writes the single‑variable GRIB (e.g., `2m_temperature_2023_09.grib`) into 
`data/raw/era5/`.

3. Then run the pipeline stages via Makefile: 

```markdown
make preprocess
make features
make train
make evaluate
```

Alternatively, after the single‑variable GRIB is present, end‑users can simply 
run:

```markdown
make all
```

to execute Stages 1-5 in sequence. 

The monthly download (`make download`) is useful for future Branch 2 expansion 
and debugging but is **not strictly required** for the Branch 1 single‑variable 
pipeline to function.

---

## 🧪 Testing (Branch 1)

After running the pipeline, end‑users can run: 

```markdown
make test
```

Branch 1 includes **smoke tests only**:

- modules import without errors 
- key functions run without crashing (especially Stage 1) 
- basic folder structure is present 

Tests do **not** perform heavy file validation or schema checks in Branch 1. 
A deeper pytest suite arrives in Branch 2. 

---

## 📓 Notebooks

After running the pipeline and tests, end‑users open:

```markdown
notebooks/branch1_eda.ipynb
```

Inside the notebook, users can: 

- inspect Parquet files in `data/intermediate/` and `data/features/`
- validate variable distributions
- check time‑series behavior
- examine spatial coverage
- inspect metadata
- detect anomalies
- confirm pipeline correctness end‑to‑end

This notebook is the **primary interactive interface** for Branch 1 and is 
designed for exploratory analysis and sanity checks.

---

## 🔧 Environment

The environment is defined in `environment.yml`:

- Python 3.10  
- xarray + cfgrib  
- eccodes  
- cdsapi  
- pyarrow  
- cartopy  
- rich (logging)  
- jupyterlab  

This is the minimal set required for ERA5 ingestion, preprocessing, and baseline 
analytics. 

---

## 🔒 Git Hygiene

`.gitignore` ensures no large binary data enters the repo:

- ERA5 ZIP + GRIB  
- Parquet files  
- logs  
- notebook checkpoints  
- environment files  

Folder structure is preserved via `.gitkeep` where needed.

---

## ⚠️ Limitations (Branch 1)

Branch 1 intentionally avoids:

- multi‑year ingestion
- metadata registry
- schema registry
- feature dependency graphs
- MLflow experiment tracking
- Docker containerization
- CI/CD
- hyperparameter tuning
- model comparison
- residual analysis
- dashboards

These are planned for Branch 2 and beyond.

---

## 📈 Branch 2 Roadmap

Branch 2 will introduce:

- Full 6‑year ERA5 ingestion
- Advanced feature engineering (pollution-risk, exposure, meteorological drivers)
- Train/validation/test splits
- Real ML models (regression, gradient boosting, deep learning)
- Hyperparameter tuning
- Residual analysis and error diagnostics
- Model comparison and selection
- Evaluation dashboards
- MLflow experiment tracking
- Docker containerization
- CI/CD + artifact versioning
- Canary model deployment patterns 

Branch 1 intentionally avoids these to keep the MVP clean and focused on core 
architecture. 

---

## 🧭 End‑User Workflow (Branch 1)

For most users, the workflow is:

1. *(Optional)* Run diagnostics: 

```markdown
python scripts/diagnostics/test_cds.py
```

2. *(Optional)* Edit YAML configs in `configs/` (years, months, region, variables). 

3. Download the single‑variable GRIB required for Branch 1: 

```markdown
python -m src.download_01.download_era5_single
```

4. Run the full pipeline:

```markdown
make all
```

5. Run smoke tests: 

```markdown
make test
```

6. Open the notebook: 

```markdown
notebooks/branch1_eda.ipynb
```

7. Explore outputs, validate ingestion, inspect features and predictions.

This pattern matches modern enterprise ML systems: **config‑driven pipelines, 
Makefile orchestration, and notebooks for exploratory analysis**. 

---

## ✅ Status (Branch 1)

- Branch 1 is **complete** as a minimal, single‑variable ERA5 ingestion and modeling pipeline.
- The pipeline is fully operational for **September 2023** and **one key ERA5 variable**.
- Multi‑variable and multi‑year ingestion will be introduced in Branch 2. 
- Branch 1 establishes the architecture, Makefile orchestration, config system, 
preprocessing logic, and baseline modeling workflow that Branch 2 will scale. 

---

## 📬 Maintainer

**Brian Deng**  
Los Angeles, CA  

**Focus:** 
- Climate analytics 
- Hazard‑risk modeling 
- ERA5‑based pipelines and geospatial workflows 
- Scalable ML/data engineering for environmental systems 
- Pollution‑risk analytics for environmental and health exposure 