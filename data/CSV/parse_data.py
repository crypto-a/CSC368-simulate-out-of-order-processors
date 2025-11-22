"""
parse_data.py
Parses gem5 stats.txt files from Part 4 simulations and extracts key metrics
Reads the MIDDLE dump (2nd stat dump) from each stats.txt file
Outputs comprehensive CSV files for analysis
"""

import re
from pathlib import Path
import csv
from typing import Dict, List, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "part4"
CSV_OUTPUT_DIR = Path(__file__).parent

# Processor designs and their credit costs
DESIGNS = {
    "design_a": 820,
    "design_b": 960,
    "design_c": 900,
    "design_d": 1000
}

# Workloads
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


def extract_middle_dump(stats_file_path: Path) -> Optional[List[str]]:
    """
    Extract the middle (2nd) statistics dump from a gem5 stats.txt file.

    gem5 typically outputs multiple stat dumps:
    - 1st dump: initialization
    - 2nd dump: middle/ROI (Region of Interest) - THIS IS WHAT WE WANT
    - 3rd dump: final

    Returns the lines from the middle dump, or None if not found.
    """
    try:
        with open(stats_file_path, 'r') as f:
            content = f.read()

        # Split by "Begin Simulation Statistics" markers
        dumps = re.split(r'-{10} Begin Simulation Statistics -{10}', content)

        if len(dumps) < 3:
            print(f"Warning: {stats_file_path} has fewer than 3 stat dumps (found {len(dumps)-1})")
            # If there's only one dump, use it
            if len(dumps) == 2:
                return dumps[1].split('---------- End Simulation Statistics')[0].strip().split('\n')
            return None

        # Get the 2nd dump (index 2, since index 0 is before first marker)
        middle_dump = dumps[2]

        # Extract only until "End Simulation Statistics"
        middle_dump = middle_dump.split('---------- End Simulation Statistics')[0].strip()

        return middle_dump.split('\n')

    except FileNotFoundError:
        print(f"Error: File not found: {stats_file_path}")
        return None
    except Exception as e:
        print(f"Error reading {stats_file_path}: {e}")
        return None


def parse_stat_value(line: str) -> Optional[float]:
    """
    Parse a stat line and extract its numeric value.
    Example line: "system.cpu.ipc                               0.695843                       # IPC: instructions per cycle"
    """
    # Split by whitespace and get the second column (the value)
    parts = line.split()
    if len(parts) >= 2:
        try:
            # Handle scientific notation and regular numbers
            return float(parts[1])
        except ValueError:
            return None
    return None


def extract_metrics(stat_lines: List[str]) -> Dict[str, any]:
    """
    Extract all relevant metrics from the stat dump lines.
    Returns a dictionary of metric_name -> value.
    """
    metrics = {}

    # Create a lookup dictionary for faster searching
    stat_dict = {}
    for line in stat_lines:
        if line.strip() and not line.startswith('#') and not line.startswith('-'):
            parts = line.split()
            if len(parts) >= 2:
                stat_name = parts[0]
                stat_dict[stat_name] = line

    # Helper function to get stat value
    def get_stat(stat_name: str) -> Optional[float]:
        if stat_name in stat_dict:
            return parse_stat_value(stat_dict[stat_name])
        return None

    # 1. Core Performance Metrics
    metrics['simSeconds'] = get_stat('simSeconds')
    metrics['simTicks'] = get_stat('simTicks')
    metrics['simInsts'] = get_stat('simInsts')  # Total instructions simulated
    metrics['simOps'] = get_stat('simOps')  # Total ops (including micro-ops)
    metrics['numCycles'] = get_stat('system.cpu.numCycles')
    metrics['ipc'] = get_stat('system.cpu.ipc')
    metrics['cpi'] = get_stat('system.cpu.cpi')

    # 2. Pipeline Utilization
    metrics['instsIssued'] = get_stat('system.cpu.instsIssued')
    metrics['instsAdded'] = get_stat('system.cpu.instsAdded')
    metrics['numIssuedDist_mean'] = get_stat('system.cpu.numIssuedDist::mean')
    metrics['numIssuedDist_0'] = get_stat('system.cpu.numIssuedDist::0')
    metrics['numIssuedDist_1'] = get_stat('system.cpu.numIssuedDist::1')
    metrics['numIssuedDist_2'] = get_stat('system.cpu.numIssuedDist::2')
    metrics['numIssuedDist_total'] = get_stat('system.cpu.numIssuedDist::total')

    # 3. Commit Stage Stats
    metrics['commitSquashedInsts'] = get_stat('system.cpu.commit.commitSquashedInsts')
    metrics['branchMispredicts'] = get_stat('system.cpu.commit.branchMispredicts')
    metrics['numCommittedDist_mean'] = get_stat('system.cpu.commit.numCommittedDist::mean')
    metrics['numCommittedDist_0'] = get_stat('system.cpu.commit.numCommittedDist::0')
    metrics['numCommittedDist_1'] = get_stat('system.cpu.commit.numCommittedDist::1')
    metrics['numCommittedDist_2'] = get_stat('system.cpu.commit.numCommittedDist::2')

    # 4. Speculation Stats
    metrics['squashedInstsIssued'] = get_stat('system.cpu.squashedInstsIssued')
    metrics['squashedInstsExamined'] = get_stat('system.cpu.squashedInstsExamined')

    # 5. Functional Unit Busy Rates
    metrics['fuBusy_IntAlu'] = get_stat('system.cpu.statFuBusy::IntAlu')
    metrics['fuBusy_IntMult'] = get_stat('system.cpu.statFuBusy::IntMult')
    metrics['fuBusy_IntDiv'] = get_stat('system.cpu.statFuBusy::IntDiv')
    metrics['fuBusy_FloatAdd'] = get_stat('system.cpu.statFuBusy::FloatAdd')
    metrics['fuBusy_FloatMult'] = get_stat('system.cpu.statFuBusy::FloatMult')
    metrics['fuBusy_FloatDiv'] = get_stat('system.cpu.statFuBusy::FloatDiv')
    metrics['fuBusy_MemRead'] = get_stat('system.cpu.statFuBusy::MemRead')
    metrics['fuBusy_MemWrite'] = get_stat('system.cpu.statFuBusy::MemWrite')
    metrics['fuBusy_SimdAlu'] = get_stat('system.cpu.statFuBusy::SimdAlu')
    metrics['fuBusy_SimdCvt'] = get_stat('system.cpu.statFuBusy::SimdCvt')
    metrics['fuBusy_SimdMisc'] = get_stat('system.cpu.statFuBusy::SimdMisc')

    # 6. L1 Instruction Cache Performance
    metrics['l1i_hits'] = get_stat('system.cpu.l1i.demandHits::total')
    metrics['l1i_misses'] = get_stat('system.cpu.l1i.demandMisses::total')
    metrics['l1i_miss_rate'] = get_stat('system.cpu.l1i.demandMissRate::total')
    metrics['l1i_accesses'] = get_stat('system.cpu.l1i.demandAccesses::total')

    # 7. L1 Data Cache Performance
    metrics['l1d_hits'] = get_stat('system.cpu.l1d.demandHits::total')
    metrics['l1d_misses'] = get_stat('system.cpu.l1d.demandMisses::total')
    metrics['l1d_miss_rate'] = get_stat('system.cpu.l1d.demandMissRate::total')
    metrics['l1d_accesses'] = get_stat('system.cpu.l1d.demandAccesses::total')
    metrics['l1d_avg_miss_latency'] = get_stat('system.cpu.l1d.demandAvgMissLatency::total')

    # 8. Instruction Type Breakdown (from commit stage)
    metrics['committed_IntAlu'] = get_stat('system.cpu.commit.committedInstType_0::IntAlu')
    metrics['committed_IntMult'] = get_stat('system.cpu.commit.committedInstType_0::IntMult')
    metrics['committed_IntDiv'] = get_stat('system.cpu.commit.committedInstType_0::IntDiv')
    metrics['committed_FloatAdd'] = get_stat('system.cpu.commit.committedInstType_0::FloatAdd')
    metrics['committed_MemRead'] = get_stat('system.cpu.commit.committedInstType_0::MemRead')
    metrics['committed_MemWrite'] = get_stat('system.cpu.commit.committedInstType_0::MemWrite')

    return metrics


def parse_all_simulations():
    """
    Parse all simulation stats files and create CSV output.
    """
    print("=" * 80)
    print("Parsing gem5 Part 4 Simulation Statistics")
    print("=" * 80)
    print(f"Data directory: {DATA_DIR}")
    print(f"Output directory: {CSV_OUTPUT_DIR}")
    print()

    all_results = []

    # Iterate through all designs and workloads
    for design_id, credits in DESIGNS.items():
        print(f"\nProcessing {design_id} (credits: {credits})...")

        for workload in WORKLOADS:
            stats_file = DATA_DIR / design_id / workload / "stats.txt"

            if not stats_file.exists():
                print(f"  ⚠ Missing: {workload}")
                continue

            # Extract middle dump
            stat_lines = extract_middle_dump(stats_file)

            if stat_lines is None:
                print(f"  ✗ Failed to parse: {workload}")
                continue

            # Extract metrics
            metrics = extract_metrics(stat_lines)

            # Add metadata
            result = {
                'design': design_id,
                'workload': workload,
                'credits': credits,
                **metrics
            }

            # Calculate derived metrics
            if metrics['ipc'] is not None:
                result['ipc_per_credit'] = metrics['ipc'] / credits
            else:
                result['ipc_per_credit'] = None

            # Calculate issue utilization percentage (max issue width is 2)
            if metrics['numIssuedDist_mean'] is not None:
                result['issue_utilization_pct'] = (metrics['numIssuedDist_mean'] / 2.0) * 100
            else:
                result['issue_utilization_pct'] = None

            # Calculate commit utilization percentage
            if metrics['numCommittedDist_mean'] is not None:
                result['commit_utilization_pct'] = (metrics['numCommittedDist_mean'] / 2.0) * 100
            else:
                result['commit_utilization_pct'] = None

            # L1I cache hit rate (already in stats as miss_rate, so hit_rate = 1 - miss_rate)
            if metrics['l1i_miss_rate'] is not None:
                result['l1i_hit_rate'] = 1.0 - metrics['l1i_miss_rate']
            else:
                result['l1i_hit_rate'] = None

            # L1D cache hit rate
            if metrics['l1d_miss_rate'] is not None:
                result['l1d_hit_rate'] = 1.0 - metrics['l1d_miss_rate']
            else:
                result['l1d_hit_rate'] = None

            # Calculate speculation overhead (squashed / committed instructions)
            if metrics['commitSquashedInsts'] is not None and metrics['simInsts'] is not None:
                result['speculation_overhead_pct'] = (metrics['commitSquashedInsts'] / metrics['simInsts']) * 100
            else:
                result['speculation_overhead_pct'] = None

            # Branch misprediction rate
            if metrics['branchMispredicts'] is not None and metrics['simInsts'] is not None:
                result['branch_mispredict_rate'] = (metrics['branchMispredicts'] / metrics['simInsts']) * 1000  # per 1K instructions
            else:
                result['branch_mispredict_rate'] = None

            # Memory operation percentage
            if metrics['committed_MemRead'] is not None and metrics['committed_MemWrite'] is not None and metrics['simOps'] is not None:
                total_mem_ops = metrics['committed_MemRead'] + metrics['committed_MemWrite']
                result['memory_ops_pct'] = (total_mem_ops / metrics['simOps']) * 100 if metrics['simOps'] > 0 else None
            else:
                result['memory_ops_pct'] = None

            all_results.append(result)
            print(f"  ✓ {workload}: IPC={metrics['ipc']:.4f}, IPC/credit={result['ipc_per_credit']:.6f}")

    # Write to CSV
    if not all_results:
        print("\n✗ No results to write!")
        return

    output_file = CSV_OUTPUT_DIR / "part4_metrics.csv"

    # Get all unique keys (column names)
    all_keys = set()
    for result in all_results:
        all_keys.update(result.keys())

    # Sort keys for consistent column ordering
    fieldnames = ['design', 'workload', 'credits', 'ipc', 'ipc_per_credit', 'cpi'] + \
                 sorted(list(all_keys - {'design', 'workload', 'credits', 'ipc', 'ipc_per_credit', 'cpi'}))

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print("\n" + "=" * 80)
    print(f"✓ Successfully parsed {len(all_results)} simulations")
    print(f"✓ CSV output written to: {output_file}")
    print("=" * 80)

    # Print summary statistics
    print("\n📊 Summary Statistics:")
    print(f"  Total simulations: {len(all_results)}")
    print(f"  Designs: {len(DESIGNS)}")
    print(f"  Workloads per design: {len(WORKLOADS)}")
    print(f"  Expected total: {len(DESIGNS) * len(WORKLOADS)}")

    if len(all_results) < len(DESIGNS) * len(WORKLOADS):
        print(f"\n  ⚠ Warning: Missing {len(DESIGNS) * len(WORKLOADS) - len(all_results)} simulations!")


if __name__ == "__main__":
    parse_all_simulations()
