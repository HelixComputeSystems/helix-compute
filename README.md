# Helix Compute — Selective Compute Engine

Stop recomputing everything.

Helix Compute processes only what changed — reducing compute cost, minimizing data transfer, and preserving exact, verifiable state reconstruction.

## What It Does

Traditional pipelines:

- Recompute entire datasets
- Transfer full state
- Waste compute on unchanged data

Helix Compute:

- Computes only deltas
- Applies selective updates
- Reconstructs full state deterministically

## Key Properties

- ~95% compute reduction on sparse updates
- 98–99.9% data reduction depending on dataset
- Bitwise exact reconstruction (SHA-256 verified)
- Works with:
  - JSON datasets
  - NDJSON / streaming logs
  - Telemetry pipelines

## Example Run

```bash
cd examples
python run.py

Dataset: 2015-01-01-15.json (NDJSON log)

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

Dataset: AEP_hourly.json (Structured JSON)

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

What This Means

Systems with sparse changes benefit massively

Streaming and telemetry pipelines see extreme reductions

Reconstruction is exact, not approximate


Helix Compute does not optimize compute.

It avoids unnecessary compute entirely.

Repository Structure

examples/
  run.py # Proof runner
  *.json # Test datasets (JSON + NDJSON)

How It Works

1. Load base dataset


2. Apply small mutation (simulated change)


3. Compute delta (insert/update/delete)


4. Apply selective compute (only changed records)


5. Rebuild full dataset


6. Verify with SHA-256



Validation

All outputs are verified via:

SHA-256(original) == SHA-256(rebuilt)

No approximation. No drift.

Status

Prototype / proof-of-concept.

Validated across:

Structured datasets

Log streams (NDJSON)

Multi-scale record counts


Built by

Evo Engineering

Structure-aware systems for infrastructure, computation, and control.