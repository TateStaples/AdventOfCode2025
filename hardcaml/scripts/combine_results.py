#!/usr/bin/env python3

import argparse
import csv
import glob
import json
import os
import re
from typing import Any, Dict, Optional


def parse_day_from_design_name(name: str) -> Optional[int]:
    m = re.match(r"day(\d+)", name)
    return int(m.group(1)) if m else None


def load_cycles_csv(path: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            key = row["variant"]
            out[key] = row
    return out


def load_yosys_stat_json(path: str) -> Dict[str, Any]:
    # Some Yosys versions (or invocations) can include banner/log text alongside
    # the JSON emitted by `stat -json`. We attempt strict JSON parsing first,
    # then fall back to extracting the first JSON object from the file.
    with open(path) as f:
        text = f.read()

    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        if start == -1:
            raise
        decoder = json.JSONDecoder()
        obj, _end = decoder.raw_decode(text[start:])
        return obj


def find_top_module(stat: Dict[str, Any]) -> Optional[str]:
    # `stat -json` format is stable-ish but varies with -hierarchy.
    # We use a best-effort approach to locate the top module bucket.
    for k in ("modules", "design", "top"):
        if k in stat:
            # Not always present.
            pass
    if "modules" in stat and isinstance(stat["modules"], dict):
        # choose the first module listed
        return next(iter(stat["modules"].keys()), None)
    if "module" in stat and isinstance(stat["module"], str):
        return stat["module"]
    return None


def extract_area_cells(stat: Dict[str, Any]) -> Dict[str, Any]:
    # Yosys `stat -json` has evolved over time. We attempt common fields.
    # If absent, we still emit whatever we can find.
    out: Dict[str, Any] = {
        "cmos_area": None,
        "cells_total": None,
        "cells_by_type": None,
    }

    modules = stat.get("modules")
    if isinstance(modules, dict) and modules:
        # If multiple modules exist, pick the first one (top) for totals.
        top_mod = next(iter(modules.values()))
        if isinstance(top_mod, dict):
            # Newer Yosys `stat -json` primarily reports `num_cells` and
            # `num_cells_by_type`. `area` is only present in some flows.
            if out["cells_total"] is None:
                num_cells = top_mod.get("num_cells")
                if isinstance(num_cells, (int, float, str)):
                    try:
                        out["cells_total"] = int(float(num_cells))
                    except Exception:
                        pass

            by_type = top_mod.get("num_cells_by_type")
            if isinstance(by_type, dict):
                out["cells_by_type"] = by_type

            # Prefer CMOS transistor estimate as a normalized area proxy.
            est = top_mod.get("estimated_num_transistors")
            if out["cmos_area"] is None and isinstance(est, str):
                # Strings often look like "48726+".
                m = re.match(r"(\d+)", est.strip())
                if m:
                    out["cmos_area"] = int(m.group(1))

            if out["cmos_area"] is None and "area" in top_mod:
                out["cmos_area"] = top_mod.get("area")

    # Some versions store aggregate at the top level.
    if out["cells_total"] is None and "num_cells" in stat:
        try:
            out["cells_total"] = int(float(stat.get("num_cells")))
        except Exception:
            pass

    if out["cmos_area"] is None and "area" in stat:
        out["cmos_area"] = stat.get("area")

    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", required=True)
    ap.add_argument("--yosys-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cycles = load_cycles_csv(args.cycles)

    stat_files = glob.glob(os.path.join(args.yosys_dir, "*_yosys_stat.json"))
    stats_by_variant: Dict[str, Dict[str, Any]] = {}
    for p in stat_files:
        variant = os.path.basename(p).replace("_yosys_stat.json", "")
        try:
            stat = load_yosys_stat_json(p)
        except Exception:
            continue
        extracted = extract_area_cells(stat)
        extracted["yosys_stat_path"] = os.path.relpath(p)
        stats_by_variant[variant] = extracted

    # Merge on variant names where possible.
    all_variants = sorted(set(cycles.keys()) | set(stats_by_variant.keys()))

    fieldnames = [
        "variant",
        "day",
        "design",
        "work_units",
        "cycles",
        "ok",
        "cells_total",
        "cmos_area",
        "yosys_stat_path",
    ]

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for v in all_variants:
            row: Dict[str, Any] = {"variant": v}

            c = cycles.get(v)
            if c:
                row.update(
                    {
                        "day": c.get("day"),
                        "design": c.get("design"),
                        "work_units": c.get("work_units"),
                        "cycles": c.get("cycles"),
                        "ok": c.get("ok"),
                    }
                )
            else:
                # fall back to best-effort day parsing
                d = parse_day_from_design_name(v)
                row.update({"day": d})

            s = stats_by_variant.get(v)
            if s:
                row.update(
                    {
                        "cells_total": s.get("cells_total"),
                        "cmos_area": s.get("cmos_area"),
                        "yosys_stat_path": s.get("yosys_stat_path"),
                    }
                )

            w.writerow(row)


if __name__ == "__main__":
    main()
