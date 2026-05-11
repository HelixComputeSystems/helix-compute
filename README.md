# Helix Compute — Selective Compute Engine

**Stop recomputing everything.**

Helix Compute processes only what changed — reducing compute cost, minimizing data transfer, and preserving exact, verifiable state reconstruction.

Helix operates as an execution-layer optimization for incremental systems.

Instead of recomputing entire pipelines after small mutations, Helix performs:

* sparse dependency-aware execution
* reverse dependency indexing
* localized replay propagation
* deterministic reconstruction validation

---

## 📄 Whitepaper

See:

* `docs/HELIX_WHITEPAPER_V4.pdf`

Topics covered:

* sparse replay propagation
* reverse dependency indexing
* bounded dependency locality
* topology benchmark methodology
* deterministic replay validation
* incremental execution benchmarks

---

## 🚀 What It Does

### Traditional pipelines

Most systems:

* recompute entire datasets
* transfer full state
* repeatedly traverse unchanged dependencies
* waste compute on stable data

### Helix Compute

Helix instead:

* computes only deltas
* executes only affected dependency neighborhoods
* applies selective replay propagation
* reconstructs full state deterministically

---

## ⚡ Key Properties

* ~95% compute reduction on sparse updates
* 98–99.9% data reduction depending on workload
* Bitwise exact reconstruction (SHA-256 verified)
* Reverse-indexed propagation acceleration
* Bounded replay locality under mutation stress

Works with:

* JSON datasets
* NDJSON / streaming logs
* Telemetry pipelines
* Time-series infrastructure
* Incremental ETL systems

---

## 🔬 Example Run

```bash
cd examples
python run.py
```

### Dataset: `2015-01-01-15.json` (NDJSON log)

```text
RESULTS
------------------------------------------------------------
Full Size : 26206459 bytes
Delta Size : 15912 bytes
Data Reduction : 99.94%

COMPUTE
Full Ops : 11351
Delta Ops : 567
Compute Reduction: 95.00%

VALIDATION
Hash Match : YES

TIME
Execution Time : 2.006s
```

---

### Dataset: `AEP_hourly.json` (Structured JSON)

```text
RESULTS
------------------------------------------------------------
Full Size : 7528951 bytes
Delta Size : 144438 bytes
Data Reduction : 98.08%

COMPUTE
Full Ops : 121273
Delta Ops : 6063
Compute Reduction: 95.00%

VALIDATION
Hash Match : YES

TIME
Execution Time : 1.297s
```

---

## 🧠 Why It Matters

Systems with sparse mutation benefit massively from locality-aware replay.

Helix is designed for workloads where:

* recomputation dominates runtime cost
* append-heavy mutation is common
* deterministic replay matters
* dependency propagation remains localized

These conditions commonly appear in:

* telemetry systems
* historian pipelines
* CDC workflows
* streaming ETL
* structured event processing

> Helix Compute does not optimize compute.
> **It avoids unnecessary compute entirely.**

---

## 🏗️ How It Works

```text
append mutation
        ↓
reverse dependency lookup
        ↓
localized replay window
        ↓
deterministic reconstruction
```

Execution flow:

1. Load base dataset
2. Apply mutation (change)
3. Compute delta (insert/update/delete)
4. Execute only affected dependencies
5. Rebuild full dataset deterministically
6. Verify reconstruction via SHA-256

---

## 🔐 Validation

All outputs are verified via:

```text
SHA-256(original) == SHA-256(rebuilt)
```

No approximation.
No drift.
No probabilistic reconstruction.

---

## 📊 Benchmark Highlights

From the benchmark suite:

* Indexed expansion speedup: **11,940.78x**
* Best execution compression: **13,333x**
* Replay validation: **MATCH: True**
* Dependency locality remained bounded (~1.2–1.4 radius)

The benchmark suite includes:

* tree / mesh / clustered topologies
* random / hotspot / migration-wave mutation
* replay-storm propagation conditions
* datasets ranging from 10K → 100K records

---

## 📁 Repo Structure

```text
docs/
  HELIX_WHITEPAPER_V4.pdf

examples/
  run.py
  run_api.py
  *.json
```

---

## 📌 Status

Prototype / proof-of-concept.

Validated across:

* structured datasets
* NDJSON log streams
* sparse mutation workloads
* replay locality benchmarks
* multi-scale record counts

---

## 🏢 Built By

**Evo Engineering**

Structure-aware systems for infrastructure, computation, and control.
