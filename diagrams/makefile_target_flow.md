# Makefile Target Flow Diagram

This diagram shows how your Makefile orchestrates environment setup, diagnostics, linting, testing, data resets, and pipeline execution.
It is the developer‑workflow counterpart to your pipeline + IR diagrams.

```mermaid
flowchart TD

    ENV[📄 env<br>- create venv<br>- install deps]:::setup
    RESET[📄 reset<br>- clean data<br>- remove artifacts]:::reset
    DIAG[📄 diagnostics<br>- schema checks<br>- file counts<br>- parquet validation]:::diag
    LINT[📄 lint<br>- ruff<br>- black<br>- isort]:::lint
    TEST[📄 test<br>- unit tests<br>- integration tests]:::test
    RUN[📄 run<br>- execute pipeline<br>- stage orchestration]:::run
    BUILD[📄 build<br>- compile artifacts<br>- prepare outputs]:::build

    ENV --> DIAG
    DIAG --> RUN
    RESET --> RUN
    LINT --> TEST
    TEST --> RUN
    RUN --> BUILD

    %% Functional color scheme (text always black)
    classDef setup fill:#A7C7E7,stroke:#336,color:#000,stroke-width:1px;      %% blue - setup/init
    classDef reset fill:#F28B82,stroke:#633,color:#000,stroke-width:1px;      %% red/pink - destructive
    classDef diag fill:#8FD18C,stroke:#363,color:#000,stroke-width:1px;       %% green - validation
    classDef lint fill:#F2C94C,stroke:#663,color:#000,stroke-width:1px;       %% yellow - lint/warnings
    classDef test fill:#C8A2C8,stroke:#636,color:#000,stroke-width:1px;       %% purple - correctness
    classDef run fill:#DEF,stroke:#336,color:#000,stroke-width:1px;           %% light blue - orchestration
    classDef build fill:#DFD,stroke:#363,color:#000,stroke-width:1px;         %% light green - outputs
```

---

## Responsibilities

### env

- Create virtual environment.
- Install pinned dependencies.
- Validate toolchain availability.

### reset

- Remove intermediate data.
- Clear artifacts and logs.
- Ensure reproducible pipeline runs.

### diagnostics

- Validate input schemas.
- Count rows, columns, timestamps.
- Check parquet integrity and metadata.

### lint

- Run ruff, black, and isort.
- Enforce formatting and style consistency.

### test

- Execute unit tests.
- Run integration tests.
- Validate pipeline correctness.

### run

- Execute pipeline stages.
- Orchestrate IR₀ → IR₈ transitions.
- Produce intermediate and final artifacts.

### build

- Compile final outputs.
- Prepare deployment artifacts.
- Ensure reproducibility and versioning.

---

## Outputs

### Build Artifacts

```code
build/
```

### Logs

```code
logs/
```

### Intermediate Data

```code
data/intermediate/
```

### Final Outputs

```code
data/final/
```

### IR Boundary

- Makefile orchestrates transitions across **IR₀ → IR₈**
