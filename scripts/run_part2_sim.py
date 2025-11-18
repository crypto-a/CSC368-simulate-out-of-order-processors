"""
run_part2_sim.py
Runs all Part 2 simulations for CSC368H1 Assignment 3
"""

import subprocess
import os
from pathlib import Path

# Define project paths
PROJECT_ROOT = Path(__file__).parent
GEM5_SCRIPT = PROJECT_ROOT / "gem5scripts" / "a3_part2.py"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "part2"

# Workloads to simulate (large inputs only, as per assignment)
WORKLOADS = [
    "basicmath",
    "bitcounts",
    "qsort",
    "susan_edges",
    "susan_corners",
    "susan_smoothing",
    "jpeg_encode",
    "jpeg_decode",
    "dijkstra"
]

# gem5 executable path (adjust if needed)
GEM5_EXECUTABLE = "gem5"  # Assumes gem5 is in PATH, or update to full path


def run_simulation(workload_name):
    """Run a single simulation for the given workload."""

    # Create output directory for this workload
    output_dir = RAW_DATA_DIR / workload_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"Running simulation: {workload_name}")
    print(f"Output directory: {output_dir}")
    print(f"{'=' * 60}\n")

    # Build the command
    cmd = [
        GEM5_EXECUTABLE,
        str(GEM5_SCRIPT),
        workload_name,
        "-o", str(output_dir)
    ]

    print(f"Command: {' '.join(cmd)}\n")

    try:
        # Run the simulation
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        print(f"✓ {workload_name} completed successfully")
        print(f"  Stats saved to: {output_dir}/stats.txt")

        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ {workload_name} FAILED")
        print(f"  Error: {e}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        return False


def main():
    """Run all Part 2 simulations."""

    print("\n" + "=" * 60)
    print("CSC368H1 Assignment 3 - Part 2 Simulations")
    print("=" * 60)

    # Check if gem5 script exists
    if not GEM5_SCRIPT.exists():
        print(f"\nERROR: gem5 script not found at {GEM5_SCRIPT}")
        print("Please ensure a3_part2.py is in the gem5scripts/ directory")
        return

    # Create base data directory
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Track results
    successful = []
    failed = []

    # Run each workload
    for workload in WORKLOADS:
        success = run_simulation(workload)

        if success:
            successful.append(workload)
        else:
            failed.append(workload)

    # Print summary
    print("\n" + "=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    print(f"\nTotal workloads: {len(WORKLOADS)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if successful:
        print("\n✓ Successful simulations:")
        for w in successful:
            print(f"  - {w}")

    if failed:
        print("\n✗ Failed simulations:")
        for w in failed:
            print(f"  - {w}")

    print("\n" + "=" * 60)
    print(f"Data saved to: {RAW_DATA_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()