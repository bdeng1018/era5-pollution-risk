# 🔐 Security Policy — ERA5 Pollution‑Risk Pipeline (Branch 2)

This project implements a multi‑stage ERA5 ingestion, preprocessing, chunking, feature‑engineering, modeling, evaluation, and deployment pipeline.
Although it does not expose a public API, contributors and users may discover issues related to:

- GRIB ingestion correctness
- metadata extraction and validation
- preprocessing integrity (unzip → inspect → convert → metadata)
- chunk‑planning, chunk‑processing, and chunk‑merging logic
- spatiotemporal alignment, interpolation, QC, and tensor building
- feature engineering correctness (Stage 05)
- modeling reproducibility and deterministic training (Stage 06)
- evaluation metrics and inference behavior (Stage 07)
- deployment configuration and runtime safety (Stage 08)
- Makefile orchestration and workspace tooling

Branch 2 processes **public ERA5 climate datasets** only.
No PHI/PII is ingested, stored, or processed.

Branch 2 does **not** include AI/RAG/LLM/agentic inference.
Those components are reserved for Branch 3.

---

## 📣 Reporting a Vulnerability

Please report all security, data‑integrity, or reproducibility issues privately.

Maintainer: **Brian Deng**
Email: **<bdeng.data.pipelines@gmail.com>**

You may report:

- ingestion failures that corrupt GRIB or parquet outputs
- metadata extraction errors not caught by preprocessing
- chunk‑planning or chunk‑merging inconsistencies
- spatiotemporal alignment or interpolation errors
- QC logic that produces incorrect masks or tensors
- feature‑engineering logic that produces invalid features
- modeling code that leaks environment details or behaves nondeterministically
- evaluation metrics that expose sensitive paths or misrepresent results
- deployment misconfigurations that create unsafe runtime behavior
- Makefile targets that produce nondeterministic results
- any reproducibility issue affecting deterministic execution

Do **not** open a public GitHub Issue for security‑related findings.

---

## 🕒 Response Expectations

You will receive an initial response within **72 hours**.
A full assessment or fix may take longer depending on complexity.

---

## 🔄 Disclosure Process

If the issue is confirmed:

- a patch will be developed in a dedicated branch
- tests will be added to prevent regression
- documentation will be updated
- the fix will be included in the next semantic version release
- the changelog will record the resolution under `[Unreleased]`

---

## 🧪 Non‑Security Bugs

For non‑security issues (tests, formatting, diagnostics, Makefile targets, VS Code configs, etc.), please use:

- GitHub Issues
- GitHub Discussions (if enabled)
- Pull Requests

---

## 🧭 Branch Notes

### Branch 2 (ERA5)

Branch 2 introduces:

- multi‑year ERA5 ingestion
- GRIB preprocessing
- chunked core processing
- spatiotemporal tensor compilation
- feature engineering (Stage 05)
- modeling (Stage 06)
- evaluation (Stage 07)
- deployment scaffolding (Stage 08)
- deterministic Makefile orchestration
- VS Code workspace tooling (tasks, launch, settings, extensions)

No AI/RAG/LLM/agentic inference is used in Branch 2.

### Branch 3 (Future)

Branch 3 will introduce:

- advanced feature engineering
- full modeling pipelines
- evaluation dashboards
- deployment (FastAPI, Docker, MLflow)
- optional agentic inference modules
- security policies updated accordingly
