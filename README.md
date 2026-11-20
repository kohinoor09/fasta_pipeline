## FASTA Analysis Pipeline

A 3-step pipeline that runs from one command:

1. **Stats**: reads a FASTA file, writes length, GC% and base counts per sequence (`results/01_stats.csv`)
2. **Filter**: keeps sequences meeting length and GC% thresholds (`results/02_filtered.csv`)
3. **Report**: writes a summary (`results/03_summary.txt`)

## Run
Requires Python 3.8+ only (no extra packages).

    git clone <this-repo-url>
    cd fasta-pipeline
    python run_pipeline.py

## Parameters
All settings are in the block at the top of `run_pipeline.py`
(input file, output folder, MIN_LENGTH, MIN_GC, MAX_GC). The values used in each
run are saved to `results/params_used.txt`.

## Outputs
Intermediate files are kept in `results/` so every step can be inspected.

## Decisions
- Used only the Python standard library so it runs on a clean checkout with no installs.
- A small example FASTA is included in `data/` so the pipeline works immediately.
- Sequences that fail the filters are dropped in step 2 but remain visible in step 1's file.fasta_pipeline
