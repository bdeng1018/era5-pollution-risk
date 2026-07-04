# core_03 — Stage 3 Chunked Core Processing

Stage 3 introduces the **deterministic, parallel‑safe chunk‑processing engine** that transforms the preprocessed ERA5 data from `preprocessing_02` into stable, schema‑validated intermediate artifacts. This stage is the foundation for all downstream spatiotemporal structuring (Stage 4) and feature engineering (Stage 5).

Stage 3 is the first **fully operational** transformation stage in the pipeline.

---

## 📌 Stage 3 Scope (Branch 2)

Stage 3 builds a clean, metadata‑driven processing layer:

- Define **ChunkSpec**, the atomic unit of work
- Build deterministic chunk lists via **ChunkPlanner**
- Process each chunk independently using **ChunkWorker**
- Enforce column order and dtypes via **ChunkSchema**
- Execute chunks in parallel using **ChunkOrchestrator**
- Produce reproducible Parquet artifacts for Stage 4

Branch 2 implements the full architecture using Python multiprocessing.
Distributed execution arrives in Branch 3.

---

## 📁 Files

```markdown
core_03/
├── __init__.py              # Package initializer
├── chunk_spec.py            # Defines the atomic unit of work
├── chunk_planner.py         # Builds deterministic ChunkSpec lists
├── chunk_worker.py          # Processes a single chunk
├── chunk_orchestrator.py    # Parallel execution engine
└── chunk_schema.py          # Deterministic column order + dtype enforcement
```

These five modules form the complete Stage 3 engine.
Additional modules (e.g., `chunk_metrics.py`, `chunk_provenance.py`) may appear in Branch 3.

---

## ⚙️ How It Works

The Stage 3 pipeline:

1. Load Stage 2 `metadata.json`
2. Build chunk specifications (hourly/daily windows; spatial tiling optional in Branch 3)
3. Process each chunk independently:
   - load → normalize → clean → enforce schema → write
4. Execute chunks in parallel with multiprocessing
5. Write deterministic Parquet outputs for Stage 4

This design ensures reproducibility, parallel safety, and clean separation of concerns.

---

## 🔜 Branch 3 Preview

Branch 3 expands Stage 3 with:

- Distributed execution backends (Ray, Dask)
- Spatial tiling strategies for large‑domain parallelism
- Advanced retry and failure isolation
- Chunk lineage and provenance tracking
- Performance instrumentation and metrics
- Multi‑file chunk stitching and partitioning

These enhancements build on the foundation established in Branch 2.

---

## 📦 Usage

Run Stage 3 via the Makefile:

```markdown
make core
```

Or directly:

```markdown
python -m src.core_03.chunk_orchestrator
```

---

## 📬 Notes

Stage 3 is the first stage where the pipeline becomes **parallel**, **deterministic**, and **schema‑driven**.
It establishes the structure that Stage 4 (spatiotemporal alignment) and Stage 5 (feature engineering) depend on.
A clean, modular Stage 3 ensures the entire pipeline remains maintainable and scalable as complexity increases.
