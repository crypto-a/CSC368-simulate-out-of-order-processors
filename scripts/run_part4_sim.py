"""
run_part4_sim.py
Runs all Part 4 simulations for CSC368H1 Assignment 3
Tests 4 different processor configurations across all workloads
Uses multiprocessing to run up to 4 simulations in parallel

Priority Management:
- Run this script with: nice -n -10 python3 scripts/run_part4_sim.py
- Main coordinator script runs at higher priority (nice -10)
- Individual gem5 processes run at lower priority (nice 10)
- This ensures efficient job scheduling and system responsiveness
"""

import subprocess
import os
import sys
from pathlib import Path
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count

# Define project paths
PROJECT_ROOT = Path(__file__).parent.parent
GEM5_SCRIPT = PROJECT_ROOT / "gem5scripts" / "a3_part4.py"
DATA_DIR = PROJECT_ROOT / "data" / "part4"

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

# Maximum number of parallel gem5 simulations to run at once
# Adjust based on your system's CPU cores and memory
MAX_PARALLEL_PROCESSES = 4

# gem5 executable path (adjust if needed)
# Common locations:
# - /opt/gem5/build/X86/gem5.opt
# - /u/csc368h/fall/pub/gem5/build/X86/gem5.opt
# - gem5.opt (if in PATH)
GEM5_EXECUTABLE = "/opt/gem5/build/X86/gem5.opt"  # Update this path as needed

# Processor Configurations
PROCESSOR_CONFIGS = {
    "design_a": {
        "name": "Design A - Conservative (820 credits)",
        "params": {
            # Fixed parameters (same for all designs)
            "fetch_width": 2,
            "decode_width": 2,
            "rename_width": 2,
            "dispatch_width": 2,
            "issue_width": 2,
            "commit_width": 2,
            "fetch_buffer_size": 64,
            "fetch_queue_size": 16,
            "num_iq_entries": 32,
            # Variable parameters (Design A specific)
            "fu_pool": "extended",
            "num_rob_entries": 64,
            "lq_entries": 8,
            "sq_entries": 8
        }
    },
    "design_b": {
        "name": "Design B - ROB-Focused (960 credits)",
        "params": {
            # Fixed parameters
            "fetch_width": 2,
            "decode_width": 2,
            "rename_width": 2,
            "dispatch_width": 2,
            "issue_width": 2,
            "commit_width": 2,
            "fetch_buffer_size": 64,
            "fetch_queue_size": 16,
            "num_iq_entries": 32,
            # Variable parameters (Design B specific)
            "fu_pool": "extended",
            "num_rob_entries": 128,  # DOUBLED from Design A
            "lq_entries": 8,
            "sq_entries": 8
        }
    },
    "design_c": {
        "name": "Design C - LSQ-Focused (900 credits)",
        "params": {
            # Fixed parameters
            "fetch_width": 2,
            "decode_width": 2,
            "rename_width": 2,
            "dispatch_width": 2,
            "issue_width": 2,
            "commit_width": 2,
            "fetch_buffer_size": 64,
            "fetch_queue_size": 16,
            "num_iq_entries": 32,
            # Variable parameters (Design C specific)
            "fu_pool": "extended",
            "num_rob_entries": 64,
            "lq_entries": 16,  # DOUBLED from Design A
            "sq_entries": 16   # DOUBLED from Design A
        }
    },
    "design_d": {
        "name": "Design D - FU-Focused (1000 credits)",
        "params": {
            # Fixed parameters
            "fetch_width": 2,
            "decode_width": 2,
            "rename_width": 2,
            "dispatch_width": 2,
            "issue_width": 2,
            "commit_width": 2,
            "fetch_buffer_size": 64,
            "fetch_queue_size": 16,
            "num_iq_entries": 32,
            # Variable parameters (Design D specific)
            "fu_pool": "aggressive",  # UPGRADED from Extended
            "num_rob_entries": 64,
            "lq_entries": 8,
            "sq_entries": 8
        }
    }
}


def check_gem5_executable():
    """Check if gem5 executable exists and is accessible."""
    global GEM5_EXECUTABLE

    # List of possible gem5 locations to check
    possible_paths = [
        "/opt/gem5/build/X86/gem5.opt",
        "/u/csc368h/fall/pub/gem5/build/X86/gem5.opt",
        Path.home() / "gem5" / "build" / "X86" / "gem5.opt",
        "gem5.opt",  # In PATH
        "gem5"       # In PATH
    ]

    for path in possible_paths:
        path = Path(path) if not isinstance(path, Path) else path
        if path.exists() or (not path.is_absolute() and subprocess.run(["which", str(path)], capture_output=True).returncode == 0):
            GEM5_EXECUTABLE = str(path)
            print(f"Found gem5 at: {GEM5_EXECUTABLE}")
            return True

    print(f"WARNING: gem5 executable not found at {GEM5_EXECUTABLE}")
    print("Please update GEM5_EXECUTABLE in the script to point to your gem5 installation")
    print("Common locations:")
    for path in possible_paths[:3]:
        print(f"  - {path}")
    return False


def run_simulation_worker(job):
    """
    Worker function to run a single gem5 simulation in a separate process.
    Takes a job dict and returns a result dict.
    """
    design_id = job['design_id']
    design_name = job['design_name']
    workload_name = job['workload']
    params = job['params']
    gem5_exec = job['gem5_exec']
    gem5_script = job['gem5_script']
    output_dir = Path(job['output_dir'])

    # Create output directory for this design and workload
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build the command with all parameters
    # Use 'nice' to run gem5 at lower priority (nice value 10)
    # This allows the main coordinator script to maintain higher priority
    cmd = [
        "nice", "-n", "10",  # Run gem5 at lower priority
        gem5_exec,
        str(gem5_script),
        workload_name,
        "-o", str(output_dir),
        "--fetch_width", str(params['fetch_width']),
        "--decode_width", str(params['decode_width']),
        "--rename_width", str(params['rename_width']),
        "--dispatch_width", str(params['dispatch_width']),
        "--issue_width", str(params['issue_width']),
        "--commit_width", str(params['commit_width']),
        "--fetch_buffer_size", str(params['fetch_buffer_size']),
        "--fetch_queue_size", str(params['fetch_queue_size']),
        "--num_iq_entries", str(params['num_iq_entries']),
        "--fu_pool", params['fu_pool'],
        "--num_rob_entries", str(params['num_rob_entries']),
        "--lq_entries", str(params['lq_entries']),
        "--sq_entries", str(params['sq_entries'])
    ]

    # Log file for this simulation
    log_file = output_dir / "simulation.log"

    # Run the simulation
    start_time = time.time()

    try:
        with open(log_file, 'w') as log:
            result = subprocess.run(
                cmd,
                stdout=log,
                stderr=log,
                text=True
            )

        elapsed_time = time.time() - start_time

        success = result.returncode == 0

        return {
            'name': f"{design_id}/{workload_name}",
            'design_id': design_id,
            'design_name': design_name,
            'workload': workload_name,
            'success': success,
            'elapsed_time': elapsed_time,
            'output_dir': str(output_dir),
            'log_file': str(log_file),
            'returncode': result.returncode
        }

    except FileNotFoundError:
        elapsed_time = time.time() - start_time
        return {
            'name': f"{design_id}/{workload_name}",
            'design_id': design_id,
            'design_name': design_name,
            'workload': workload_name,
            'success': False,
            'elapsed_time': elapsed_time,
            'output_dir': str(output_dir),
            'log_file': str(log_file),
            'returncode': -1,
            'error': f"gem5 executable not found at {gem5_exec}"
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            'name': f"{design_id}/{workload_name}",
            'design_id': design_id,
            'design_name': design_name,
            'workload': workload_name,
            'success': False,
            'elapsed_time': elapsed_time,
            'output_dir': str(output_dir),
            'log_file': str(log_file) if 'log_file' in locals() else '',
            'returncode': -1,
            'error': str(e)
        }


def print_configuration_summary():
    """Print a summary of all configurations."""
    print("\n" + "=" * 80)
    print("PROCESSOR CONFIGURATION SUMMARY")
    print("=" * 80)
    print("\n| Design | ROB | LQ/SQ | FU Pool | Cost | Strategy |")
    print("|--------|-----|-------|---------|------|----------|")
    print("| A | 64 | 8/8 | Extended | 820 | Baseline/Conservative |")
    print("| B | 128 | 8/8 | Extended | 960 | ROB-Focused (2x ROB) |")
    print("| C | 64 | 16/16 | Extended | 900 | LSQ-Focused (2x LQ/SQ) |")
    print("| D | 64 | 8/8 | Aggressive | 1000 | FU-Focused (More ALUs) |")
    print("\nAll designs use: Width=2 for all pipeline stages, FetchBuffer=64B, FetchQueue=16, IQ=32")
    print("=" * 80)


def main():
    """Run all Part 4 simulations."""

    print("\n" + "=" * 80)
    print("CSC368H1 Assignment 3 - Part 4 Out-of-Order Processor Simulations")
    print("=" * 80)

    # Check if gem5 script exists
    if not GEM5_SCRIPT.exists():
        print(f"\nERROR: gem5 script not found at {GEM5_SCRIPT}")
        print("Please ensure a3_part4.py is in the gem5scripts/ directory")
        return

    # Check if gem5 executable exists
    if not check_gem5_executable():
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    # Print configuration summary
    print_configuration_summary()

    # Ask user which simulations to run
    print("\n" + "=" * 80)
    print("SIMULATION OPTIONS")
    print("=" * 80)
    print("\n1. Run all designs × all workloads (36 simulations)")
    print("2. Run specific design(s)")
    print("3. Run specific workload(s) on all designs")
    print("4. Test run (1 design × 1 workload)")

    choice = input("\nSelect option (1-4): ").strip()

    designs_to_run = list(PROCESSOR_CONFIGS.keys())
    workloads_to_run = WORKLOADS.copy()

    if choice == "2":
        print("\nAvailable designs:")
        for design_id, config in PROCESSOR_CONFIGS.items():
            print(f"  {design_id}: {config['name']}")
        selected = input("Enter design IDs separated by spaces (e.g., 'design_a design_b'): ").strip().split()
        designs_to_run = [d for d in selected if d in PROCESSOR_CONFIGS]
        if not designs_to_run:
            print("No valid designs selected. Exiting.")
            return

    elif choice == "3":
        print(f"\nAvailable workloads: {', '.join(WORKLOADS)}")
        selected = input("Enter workload names separated by spaces: ").strip().split()
        workloads_to_run = [w for w in selected if w in WORKLOADS]
        if not workloads_to_run:
            print("No valid workloads selected. Exiting.")
            return

    elif choice == "4":
        designs_to_run = ["design_a"]
        workloads_to_run = ["basicmath"]
        print("\nRunning test: design_a × basicmath")

    # Create base data directory
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Build list of all simulation jobs
    jobs = []
    for design_id in designs_to_run:
        design_config = PROCESSOR_CONFIGS[design_id]
        for workload in workloads_to_run:
            output_dir = DATA_DIR / design_id / workload
            job = {
                'design_id': design_id,
                'design_name': design_config['name'],
                'workload': workload,
                'params': design_config['params'],
                'gem5_exec': GEM5_EXECUTABLE,
                'gem5_script': str(GEM5_SCRIPT),
                'output_dir': str(output_dir)
            }
            jobs.append(job)

    total_simulations = len(jobs)

    print(f"\n" + "=" * 80)
    print(f"Starting {total_simulations} simulations in parallel (max {MAX_PARALLEL_PROCESSES} at a time)...")
    print(f"Designs: {', '.join(designs_to_run)}")
    print(f"Workloads: {', '.join(workloads_to_run)}")
    print(f"CPU cores available: {cpu_count()}")
    print("=" * 80)

    start_time = datetime.now()

    # Run simulations in parallel using multiprocessing Pool
    print(f"\nLaunching {MAX_PARALLEL_PROCESSES}-worker pool...")
    with Pool(processes=MAX_PARALLEL_PROCESSES) as pool:
        # Use map to run all jobs
        results = pool.map(run_simulation_worker, jobs)

    end_time = datetime.now()
    wall_time = (end_time - start_time).total_seconds()

    # Process results
    successful = []
    failed = []
    total_sim_time = 0

    for result in results:
        total_sim_time += result['elapsed_time']
        if result['success']:
            successful.append(result['name'])
            print(f"✓ {result['name']} completed in {result['elapsed_time']:.1f}s")
            print(f"  Stats: {result['output_dir']}/stats.txt")
            print(f"  Log: {result['log_file']}")
        else:
            failed.append(result['name'])
            print(f"✗ {result['name']} FAILED (return code: {result['returncode']})")
            print(f"  Log: {result['log_file']}")
            if 'error' in result:
                print(f"  Error: {result['error']}")

    # Print summary
    print("\n" + "=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal simulations: {total_simulations}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"\nTotal simulation time: {total_sim_time:.1f}s")
    print(f"Wall clock time: {wall_time:.1f}s")
    print(f"Average time per simulation: {total_sim_time/max(len(successful), 1):.1f}s")
    if total_sim_time > 0 and wall_time > 0:
        speedup = total_sim_time / wall_time
        print(f"Parallel speedup: {speedup:.2f}x (efficiency: {(speedup/MAX_PARALLEL_PROCESSES)*100:.1f}%)")

    if successful:
        print("\n✓ Successful simulations:")
        for s in successful[:5]:  # Show first 5
            print(f"  - {s}")
        if len(successful) > 5:
            print(f"  ... and {len(successful)-5} more")

    if failed:
        print("\n✗ Failed simulations:")
        for f in failed:
            print(f"  - {f}")

    print("\n" + "=" * 80)
    print(f"Data saved to: {DATA_DIR}/")
    print("\nDirectory structure:")
    print("  data/part4/")
    print("    ├── design_a/")
    print("    │   ├── basicmath/stats.txt")
    print("    │   ├── bitcounts/stats.txt")
    print("    │   └── ...")
    print("    ├── design_b/")
    print("    ├── design_c/")
    print("    └── design_d/")
    print("=" * 80 + "\n")

    # Suggest next steps
    if successful:
        print("\nNext steps:")
        print("1. Parse the statistics: python data/parseStats.py")
        print("2. Compare designs across workloads")
        print("3. Identify which design works best for each workload type")
        print("4. Analyze IPC improvements over baseline (Design A)")


if __name__ == "__main__":
    main()