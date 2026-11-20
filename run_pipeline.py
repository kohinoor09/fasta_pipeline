#!/usr/bin/env python3
"""End-to-end FASTA pipeline: stats -> filter -> report.
Run with:  python run_pipeline.py
"""
import csv
import sys
from pathlib import Path

# ====================== PARAMETERS (edit here only) ======================
INPUT_FASTA = "data/example.fasta"   # input file
OUT_DIR = "results"                  # all intermediate + final files go here
MIN_LENGTH = 50                      # keep sequences at least this long (bp)
MIN_GC = 40.0                        # keep sequences with GC% >= this
MAX_GC = 60.0                        # keep sequences with GC% <= this
# ==========================================================================

OUT = Path(OUT_DIR)
STATS_CSV = OUT / "01_stats.csv"
FILTERED_CSV = OUT / "02_filtered.csv"
SUMMARY_TXT = OUT / "03_summary.txt"
PARAMS_TXT = OUT / "params_used.txt"


def read_fasta(path):
    name, seq = None, []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    yield name, "".join(seq)
                name, seq = line[1:].split()[0], []
            else:
                seq.append(line.upper())
    if name is not None:
        yield name, "".join(seq)


def step1_stats():
    """FASTA -> 01_stats.csv (length, GC%, base counts per sequence)."""
    rows = []
    for name, seq in read_fasta(INPUT_FASTA):
        n = len(seq)
        counts = {b: seq.count(b) for b in "ACGTN"}
        gc = (counts["G"] + counts["C"]) / n * 100 if n else 0.0
        rows.append({"id": name, "length": n, "gc_percent": round(gc, 2), **counts})
    with open(STATS_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[step 1] {len(rows)} sequences -> {STATS_CSV}")


def step2_filter():
    """01_stats.csv -> 02_filtered.csv (apply length + GC thresholds)."""
    with open(STATS_CSV) as f:
        rows = list(csv.DictReader(f))
    kept = [r for r in rows
            if int(r["length"]) >= MIN_LENGTH
            and MIN_GC <= float(r["gc_percent"]) <= MAX_GC]
    with open(FILTERED_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(kept)
    print(f"[step 2] kept {len(kept)} of {len(rows)} -> {FILTERED_CSV}")


def step3_report():
    """02_filtered.csv -> 03_summary.txt (final summary)."""
    with open(STATS_CSV) as f:
        total = len(list(csv.DictReader(f)))
    with open(FILTERED_CSV) as f:
        kept = list(csv.DictReader(f))
    lines = [
        "FASTA PIPELINE SUMMARY",
        f"Input file: {INPUT_FASTA}",
        f"Total sequences: {total}",
        f"Passed filters: {len(kept)}",
    ]
    if kept:
        avg_len = sum(int(r["length"]) for r in kept) / len(kept)
        avg_gc = sum(float(r["gc_percent"]) for r in kept) / len(kept)
        lines += [f"Average length (passed): {avg_len:.1f} bp",
                  f"Average GC% (passed): {avg_gc:.2f}",
                  "Passed IDs: " + ", ".join(r["id"] for r in kept)]
    SUMMARY_TXT.write_text("\n".join(lines) + "\n")
    print(f"[step 3] report -> {SUMMARY_TXT}")


def main():
    if not Path(INPUT_FASTA).exists():
        sys.exit(f"Input file not found: {INPUT_FASTA}")
    OUT.mkdir(exist_ok=True)
    PARAMS_TXT.write_text(
        f"INPUT_FASTA={INPUT_FASTA}\nMIN_LENGTH={MIN_LENGTH}\n"
        f"MIN_GC={MIN_GC}\nMAX_GC={MAX_GC}\n")
    step1_stats()
    step2_filter()
    step3_report()
    print("Pipeline finished.")


if __name__ == "__main__":
    main()
