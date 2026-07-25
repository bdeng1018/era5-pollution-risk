# 🔐 Security Policy

This project implements a multi‑stage ERA5 ingestion, preprocessing, feature‑engineering, modeling, and evaluation pipeline.
Although it does not expose a public API, contributors and users may discover issues related to:

- data ingestion correctness
- GRIB decoding reliability
- preprocessing logic
- feature generation
- model artifact handling
- diagnostics scripts
- reproducibility and deterministic execution

### Branch 1 Scope

Branch 1 is **fully deterministic** and processes only **public ERA5 climate datasets**.
No sensitive, private, or regulated data (PHI/PII) is ingested, stored, or processed.

Branch 1 includes:

- single-variable ERA5 ingestion
- minimal preprocessing
- placeholder feature engineering
- baseline modeling
- trivial evaluation

Parallelization, multi-variable ingestion, metadata tracking, and advanced modeling arrive in **Branch 2** and should **not** be added to Branch 1.

If you believe you have found a security‑relevant issue, please follow the guidelines below.

---

## 📣 Reporting a Vulnerability

Please report all security or data‑integrity issues **privately**.

Maintainer: **Brian Deng** <br>
Email: **<bdeng.data.pipelines@gmail.com>**

You may report:

- ingestion failures that produce corrupted GRIB or Parquet files
- GRIB decoding issues that silently drop variables or coordinates
- preprocessing logic that produces incorrect or incomplete outputs
- feature engineering errors that affect downstream modeling
- model artifact issues (serialization, deserialization, reproducibility)
- diagnostics scripts that behave unexpectedly or expose environment details
- any reproducibility issue that affects deterministic execution

Do **not** open a public GitHub Issue for security‑related findings.

---

## 🕒 Response Expectations

You will receive an initial response within **72 hours**.
A full assessment or fix may take longer depending on complexity.

---

## 🔄 Disclosure Process

If the issue is confirmed:

- it will be patched in a dedicated branch
- tests will be added to prevent regression
- documentation will be updated
- the fix will be included in the next semantic version release
- the changelog will record the resolution under `[Unreleased]`

---

## 🧪 Non‑Security Bugs

For non‑security issues (tests, formatting, diagnostics, Makefile targets, etc.), please use:

- GitHub Issues
- GitHub Discussions (if enabled)
- Pull Requests
