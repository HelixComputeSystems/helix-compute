import json
import hashlib
import time
import copy
import os

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
        raw = [json.loads(line) for line in content.splitlines() if line.strip()]

    if isinstance(raw, list):
        data = {"records": raw}
    else:
        data = raw

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

    full_ops = len(out["records"])
    delta_ops = 0

    for i, r in enumerate(out["records"]):
        rid = r["id"]

        if rid not in base_map or base_map[rid] != r:
            out["records"][i] = heavy_compute_record(r)
            delta_ops += 1

    return out, full_ops, delta_ops

# =========================
# CLEAN DEMO FUNCTION
# =========================
def run_demo(file_path):
    start_time = time.time()

    base = load_data(file_path)
    modified = copy.deepcopy(base)

    change_count = max(1, int(len(modified["records"]) * 0.05))

    for r in modified["records"][:change_count]:
        for k, v in r.items():
            if isinstance(v, (int, float)) and k != "id":
                r[k] = v + 1

    full_bytes = normalize(modified)

    changes = compute_delta(base, modified)
    delta_bytes = json.dumps(changes, separators=(",", ":")).encode()

    flux_result, full_ops, delta_ops = apply_flux(base, modified)

    rebuilt = apply_delta(base, changes)

    original_hash = sha256(full_bytes)
    rebuilt_hash = sha256(normalize(rebuilt))

    end_time = time.time()

    return {
        "dataset": os.path.basename(file_path),
        "data_reduction_pct": round(100 * (1 - len(delta_bytes) / len(full_bytes)), 2),
        "compute_reduction_pct": round(100 * (1 - delta_ops / full_ops), 2),
        "full_ops": full_ops,
        "delta_ops": delta_ops,
        "full_size_bytes": len(full_bytes),
        "delta_size_bytes": len(delta_bytes),
        "hash_match": original_hash == rebuilt_hash,
        "execution_time_sec": round(end_time - start_time, 4)
    }