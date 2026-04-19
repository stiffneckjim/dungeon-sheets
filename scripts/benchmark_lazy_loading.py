#!/usr/bin/env python3
"""Benchmark lazy-loading behavior for dungeonsheets content modules.

This script measures:
1) Package import time
2) First attribute access time (triggers lazy loading)
3) Second attribute access time (steady-state)

It can benchmark one checkout, or compare two checkouts side-by-side.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TARGETS: tuple[tuple[str, str], ...] = (
    ("dungeonsheets.spells", "MagicMissile"),
    ("dungeonsheets.armor", "LeatherArmor"),
    ("dungeonsheets.weapons", "Shortsword"),
    ("dungeonsheets.monsters", "Goblin"),
    ("dungeonsheets.background", "Acolyte"),
)


@dataclass
class BenchStats:
    mean_ms: float
    stdev_ms: float
    min_ms: float
    max_ms: float


def _resolve_python(checkout: Path, python_override: str | None) -> str:
    if python_override:
        return python_override
    venv_python = checkout / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _summarize(samples: Iterable[float]) -> BenchStats:
    data = list(samples)
    if not data:
        raise ValueError("No samples to summarize")
    if len(data) == 1:
        return BenchStats(mean_ms=data[0], stdev_ms=0.0, min_ms=data[0], max_ms=data[0])
    return BenchStats(
        mean_ms=statistics.mean(data),
        stdev_ms=statistics.stdev(data),
        min_ms=min(data),
        max_ms=max(data),
    )


def _run_probe(checkout: Path, python_cmd: str, module: str, attr: str | None) -> dict:
    payload = {"module": module, "attr": attr}
    code = "\n".join(
        [
            "import importlib",
            "import json",
            "import time",
            f"cfg = {payload!r}",
            "mod_start = time.perf_counter()",
            "mod = importlib.import_module(cfg['module'])",
            "mod_end = time.perf_counter()",
            "out = {'import_ms': (mod_end - mod_start) * 1000.0}",
            "if cfg['attr'] is not None:",
            "    a0 = time.perf_counter()",
            "    getattr(mod, cfg['attr'])",
            "    a1 = time.perf_counter()",
            "    a2 = time.perf_counter()",
            "    getattr(mod, cfg['attr'])",
            "    a3 = time.perf_counter()",
            "    out['first_access_ms'] = (a1 - a0) * 1000.0",
            "    out['second_access_ms'] = (a3 - a2) * 1000.0",
            "print(json.dumps(out))",
        ]
    )
    proc = subprocess.run(
        [python_cmd, "-c", code],
        cwd=str(checkout),
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout.strip())


def _benchmark_checkout(checkout: Path, repeats: int, python_override: str | None) -> dict:
    python_cmd = _resolve_python(checkout, python_override)
    rows: dict[str, dict[str, list[float]]] = {"dungeonsheets (import only)": {"import_ms": []}}
    for module, attr in TARGETS:
        rows[f"{module}.{attr}"] = {
            "import_ms": [],
            "first_access_ms": [],
            "second_access_ms": [],
        }

    for _ in range(repeats):
        rows["dungeonsheets (import only)"]["import_ms"].append(
            _run_probe(checkout, python_cmd, "dungeonsheets", None)["import_ms"]
        )
        for module, attr in TARGETS:
            result = _run_probe(checkout, python_cmd, module, attr)
            key = f"{module}.{attr}"
            rows[key]["import_ms"].append(result["import_ms"])
            rows[key]["first_access_ms"].append(result["first_access_ms"])
            rows[key]["second_access_ms"].append(result["second_access_ms"])

    summarized: dict[str, dict[str, BenchStats]] = {}
    for row_name, metrics in rows.items():
        summarized[row_name] = {metric: _summarize(samples) for metric, samples in metrics.items()}

    return {
        "checkout": str(checkout),
        "python": python_cmd,
        "repeats": repeats,
        "results": summarized,
    }


def _print_single_report(report: dict) -> None:
    print(f"Checkout: {report['checkout']}")
    print(f"Python:   {report['python']}")
    print(f"Repeats:  {report['repeats']}")
    print()
    print("Metric means in milliseconds (ms):")
    print("- import_ms: module import time")
    print("- first_access_ms: first getattr(module, symbol)")
    print("- second_access_ms: immediate repeated getattr")
    print()

    for row_name, metrics in report["results"].items():
        print(f"{row_name}")
        for metric, stats in metrics.items():
            print(
                f"  {metric:<16} mean={stats.mean_ms:8.3f}  "
                f"stdev={stats.stdev_ms:7.3f}  min={stats.min_ms:7.3f}  max={stats.max_ms:7.3f}"
            )
        print()


def _print_comparison(base: dict, cand: dict) -> None:
    print(f"Baseline:  {base['checkout']}")
    print(f"Candidate: {cand['checkout']}")
    print()
    print("Delta shown as candidate - baseline (negative is faster):")
    print()

    header = f"{'Target':44} {'Metric':16} {'Base Mean':>10} {'Cand Mean':>10} {'Delta':>10} {'Delta %':>9}"
    print(header)
    print("-" * len(header))

    for row_name, base_metrics in base["results"].items():
        cand_metrics = cand["results"][row_name]
        for metric, base_stats in base_metrics.items():
            cand_stats = cand_metrics[metric]
            delta = cand_stats.mean_ms - base_stats.mean_ms
            delta_pct = (delta / base_stats.mean_ms * 100.0) if base_stats.mean_ms else 0.0
            print(
                f"{row_name:44} {metric:16} "
                f"{base_stats.mean_ms:10.3f} {cand_stats.mean_ms:10.3f} {delta:10.3f} {delta_pct:8.1f}%"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkout",
        type=Path,
        default=Path.cwd(),
        help="Single checkout to benchmark (default: current directory).",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Baseline checkout path for side-by-side comparison.",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        help="Candidate checkout path for side-by-side comparison.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=8,
        help="Number of isolated process samples per probe (default: 8).",
    )
    parser.add_argument(
        "--python",
        help="Override Python executable used for probes (default: each checkout's .venv/bin/python if present).",
    )
    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats must be >= 1")

    if bool(args.baseline) ^ bool(args.candidate):
        parser.error("Provide both --baseline and --candidate for comparison mode")

    if args.baseline and args.candidate:
        base_report = _benchmark_checkout(args.baseline.resolve(), args.repeats, args.python)
        cand_report = _benchmark_checkout(args.candidate.resolve(), args.repeats, args.python)
        _print_comparison(base_report, cand_report)
        return 0

    report = _benchmark_checkout(args.checkout.resolve(), args.repeats, args.python)
    _print_single_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
