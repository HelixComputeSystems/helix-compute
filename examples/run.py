import json
import hashlib
import time
import copy
import os

# =========================
# CONFIG
# =========================
DELETE_SENTINEL = "__DEL__"

# =========================
# UTILS
# =========================
def normalize(data):
    sorted_records = sorted(data["records"], key=lambda r: str(r["id"]))
    return json.dumps({"records": sorted_records}, separators=(",", ":"), sort_keys=True).encode()

def sha256(b):
    return hashlib.sha256(b).hexdigest()

# =========================
# LOAD
# =========================
def load_data(path):
    with open(path, encoding="utf-8") as f:
        content = f.read().strip()

    try:
        raw = json.loads(content)
    except json.JSONDecodeError:
        # fallback → NDJSON
        raw = [json.loads(line) for line in content.splitlines() if line.strip()]

    if isinstance(raw, list):
        data = {"records": raw}
    else:
        data = raw

    # enforce IDs
    for i, r in enumerate(data["records"]):
        if "id" not in r:
            r["id"] = f"row_{i}"

    return data

# =========================
# DELTA
# =========================
def compute_delta(base, new):
    base_map = {r["id"]: r for r in base["records"]}
    new_map = {r["id"]: r for r in new["records"]}

    changes = {"update": [], "insert": [], "delete": []}

    for rid in new_map:
        if rid not in base_map:
            changes["insert"].append(new_map[rid])

    for rid in base_map:
        if rid not in new_map:
            changes["delete"].append(rid)

    for rid in new_map:
        if rid in base_map:
            old = base_map[rid]
            cur = new_map[rid]

            diff = {}

            for k, v in cur.items():
                if old.get(k) != v:
                    diff[k] = v

            for k in old:
                if k not in cur:
                    diff[k] = DELETE_SENTINEL

            if diff:
                changes["update"].append([rid, diff])

    return changes

def apply_delta(base, changes):
    base_map = {r["id"]: copy.deepcopy(r) for r in base["records"]}

    for rid in changes["delete"]:
        base_map.pop(rid, None)

    for rid, diff in changes["update"]:
        if rid in base_map:
            for k, v in diff.items():
                if v == DELETE_SENTINEL:
                    base_map[rid].pop(k, None)
                else:
                    base_map[rid][k] = v

    for rec in changes["insert"]:
        base_map[rec["id"]] = rec

    return {"records": list(base_map.values())}

# =========================
# FLUX
# =========================
def heavy_compute_record(record):
    out = {}

    for k, v in record.items():
        if k == "id":
            out[k] = v
            continue

        if isinstance(v, (int, float)):
            y = v / (abs(v) + 1e-6)
            for _ in range(10):
                y = (y * 1.3) - (y**2 * 0.001) + 0.5
            out[k] = y
        else:
            out[k] = v

    return out

def apply_flux(base, new):
    base_map = {r["id"]: r for r in base["records"]}
    out = copy.deepcopy(new)

    full_compute = len(out["records"])
    delta_compute = 0

    for i, r in enumerate(out["records"]):
        rid = r["id"]

        if rid not in base_map or base_map[rid] != r:
            out["records"][i] = heavy_compute_record(r)
            delta_compute += 1

    return out, full_compute, delta_compute

# =========================
# PROOF RUN
# =========================
def run_proof(file_path):
    print(f"\n📂 DATASET: {os.path.basename(file_path)}")
    print("=" * 60)

    start_time = time.time()

    base = load_data(file_path)
    modified = copy.deepcopy(base)

    # simulate change (5%)
    change_count = max(1, int(len(modified["records"]) * 0.05))

    for r in modified["records"][:change_count]:
        for k, v in r.items():
            if isinstance(v, (int, float)) and k != "id":
                r[k] = v + 1

    full_bytes = normalize(modified)

    changes = compute_delta(base, modified)
    delta_bytes = json.dumps(changes, separators=(",", ":")).encode()

    flux_result, full_compute, delta_compute = apply_flux(base, modified)

    rebuilt = apply_delta(base, changes)

    original_hash = sha256(full_bytes)
    rebuilt_hash = sha256(normalize(rebuilt))

    end_time = time.time()

    print("\n📊 RESULTS")
    print("-" * 60)

    print(f"Full Size : {len(full_bytes):>10} bytes")
    print(f"Delta Size : {len(delta_bytes):>10} bytes")

    reduction = 100 * (1 - len(delta_bytes) / len(full_bytes))
    print(f"Data Reduction : {reduction:>10.2f}%")

    print("\n⚡ COMPUTE")
    print(f"Full Ops : {full_compute:>10}")
    print(f"Delta Ops : {delta_compute:>10}")

    compute_reduction = 100 * (1 - delta_compute / full_compute)
    print(f"Compute Reduction: {compute_reduction:>9.2f}%")

    print("\n🔐 VALIDATION")
    print(f"Hash Match : {'YES ✅' if original_hash == rebuilt_hash else 'NO ❌'}")

    print("\n⏱️ TIME")
    print(f"Execution Time : {end_time - start_time:.4f}s")

    print("\n" + "=" * 60)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("\n🚀 HELIX COMPUTE — PROOF RUN\n")

    DATA_DIR = os.path.abspath(os.path.dirname(__file__))

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

    if not files:
        print("❌ No JSON files found in this directory.")
    else:
        for f in files:
            full_path = os.path.join(DATA_DIR, f)
            run_proof(full_path)