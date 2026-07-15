# core_03 — Stage 3 Chunked Core Processing (Branch 2)

<!-- markdownlint-disable MD033 -->

Stage 3 implements the **deterministic, parallel‑safe chunk‑processing engine** that transforms Stage 2 preprocessed ERA5 data into stable, schema‑validated intermediate artifacts. These artifacts form the foundation for all downstream spatiotemporal structuring (Stage 4) and feature engineering (Stage 5).

Stage 3 is the first **fully operational** transformation stage in the pipeline, producing both chunk‑level Parquet artifacts and a final merged dataset.

---

## Stage 3 Scope (Branch 2)

Stage 3 builds a clean, metadata‑driven processing layer:

- **ChunkSpec** — atomic unit of work
- **ChunkPlanner** — builds deterministic chunk lists
- **ChunkWorker** — processes a single chunk
- **ChunkSchema** — enforces column order + dtypes
- **ChunkOrchestrator** — parallel execution engine
- **ChunkMerge** — merges all chunk outputs into `merged.nc`

Branch 2 uses Python multiprocessing for parallel execution.
Distributed execution arrives in Branch 3.

---

## Config‑Driven Temporal Windowing

Stage 3 chunking is controlled entirely by `config.yml`:

```yaml
  chunk:
    size:
      time: 12     # window size (hours)
    stride:
      time: 12     # window stride (hours)
```

This enables:

- 12‑hour pollution‑risk windows
- 24‑hour climate/finance windows
- 6‑hour meteorology/energy windows

without changing any code.

Each window produces **one ChunkSpec per variable**, using the **representative timestamp** (the first timestamp in the window).

---

## Choosing the Right Time‑Window Size

Temporal windowing is a critical design choice. Different window sizes produce different statistical, physical, and operational behaviors. The correct choice depends on your application domain.

### 1‑Hour Windows — High‑Frequency Dynamics

Used in:

- aviation meteorology
- severe weather nowcasting
- energy grid balancing
- high‑frequency pollution spikes

### 3‑Hour Windows — Synoptic Meteorology

Used in:

- storm evolution
- hydrology
- short‑term climate diagnostics

### 6‑Hour Windows — Operational Meteorology & Energy

Used in:

- renewable energy forecasting
- storm lifecycle segmentation
- regional climate diagnostics

### 12‑Hour Windows — Pollution‑Risk, Climate Finance, Insurance

Used in:

- PM2.5 / ozone modeling
- climate‑linked financial risk
- insurance exposure windows
- environmental compliance

### 24‑Hour Windows — Daily Climate & Environmental Modeling

Used in:

- daily climate indicators
- agriculture
- water resource management

### 48‑Hour Windows — Slow‑Moving Systems

Used in:

- atmospheric rivers
- heat domes
- catastrophe modeling

### Weekly Windows — Climate & Environmental Trends

Used in:

- climate trend analysis
- environmental policy reporting

### Biweekly / Monthly Windows — Long‑Term Climate Signals

Used in:

- seasonal forecasting
- climatology
- anomaly detection

### Summary Table

<table>
  <thead>
    <tr>
      <th>Window Size</th>
      <th>Best For</th>
      <th>Why</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 hr</td>
      <td>aviation, severe weather</td>
      <td>highest temporal fidelity</td>
    </tr>
    <tr>
      <td>3 hr</td>
      <td>synoptic meteorology</td>
      <td>matches ERA5 synoptic cycle</td>
    </tr>
    <tr>
      <td>6 hr</td>
      <td>energy forecasting</td>
      <td>smooth but responsive</td>
    </tr>
    <tr>
      <td>12 hr</td>
      <td>pollution‑risk, finance</td>
      <td>captures diurnal regimes</td>
    </tr>
    <tr>
      <td>24 hr</td>
      <td>daily climate</td>
      <td>full diurnal cycle</td>
    </tr>
    <tr>
      <td>48 hr</td>
      <td>large‑scale systems</td>
      <td>multi‑day patterns</td>
    </tr>
    <tr>
      <td>Weekly</td>
      <td>climate trends</td>
      <td>persistent anomalies</td>
    </tr>
    <tr>
      <td>Biweekly/Monthly</td>
      <td>climate research</td>
      <td>long‑term variability</td>
    </tr>
  </tbody>
</table>

---

## File Structure

```markdown
core_03/
├── __init__.py              # Package initializer + documentation
├── chunk_spec.py            # Atomic unit of work (representative timestamp)
├── chunk_planner.py         # Builds deterministic ChunkSpec lists (windowing)
├── chunk_worker.py          # Processes a single chunk
├── chunk_schema.py          # Deterministic column order + dtype enforcement
├── chunk_merge.py           # Merges chunk outputs → merged.nc + metadata + QC
└── chunk_orchestrator.py    # Parallel execution engine with retry + logging
```

These six modules form the complete Stage 3 engine.

---

## How Stage 3 Works

Stage 3 is a **two‑phase pipeline**.

### Phase 1 — Chunk Execution

1. Load Stage 2 `metadata.json`
2. Build chunk specifications using config‑driven windowing
3. Process each chunk independently:

   - load parquet
   - normalize coordinates
   - drop GRIB metadata
   - enforce schema
   - write chunk parquet + metadata JSON

4. Execute chunks in parallel
5. Produce deterministic chunk‑level Parquet outputs

### Phase 2 — Chunk Merging

1. Load all chunk Parquet outputs
2. Concatenate along the time dimension
3. Sort by time
4. Validate variable consistency
5. Write final Stage 3 artifacts:

   - `merged.nc`
   - `merged_metadata.json`
   - `merged_qc.json`

This merged dataset is the required input for Stage 4.

---

## Branch 3 Preview

Branch 3 expands Stage 3 with:

- distributed execution backends (Ray, Dask)
- spatial tiling strategies for large‑domain parallelism
- advanced retry + failure isolation
- chunk lineage + provenance tracking
- performance instrumentation + metrics
- multi‑file chunk stitching + partitioning

These enhancements build on the foundation established in Branch 2.

---

## Usage

Run Stage 3 via the Makefile:

```bash
make core
```

Or directly:

```bash
python -m src.core_03 --config configs/config.yml
```

After completion, Stage 3 produces:

```markdown
data/intermediate/
    merged.nc
    merged_metadata.json
    merged_qc.json
```

These are consumed by Stage 4.

---

## Notes

Stage 3 is where the pipeline becomes **parallel**, **deterministic**, and **schema‑driven**.
It establishes the structure that Stage 4 (spatiotemporal alignment) and Stage 5 (feature engineering) depend on.

A clean, modular Stage 3 ensures the entire pipeline remains maintainable and scalable as complexity increases.
