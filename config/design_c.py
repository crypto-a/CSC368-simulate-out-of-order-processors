#!/usr/bin/env python3
"""
Design C: LSQ-Focused Configuration with Aggressive FUs (1000 credits)
- ROB: 64 entries
- Load Queue: 16 entries (DOUBLED from Design A)
- Store Queue: 16 entries (DOUBLED from Design A)
- Functional Units: Aggressive pool (MORE units)
"""

import m5
from m5.objects import *
from m5.util import addToPath
import sys
import argparse

# Add gem5 configs path
addToPath('/opt/gem5/configs')
from common import Options, Simulation
from common.Caches import *

def create_cpu():
    """Create O3CPU with Design C parameters"""
    cpu = O3CPU()

    # Design C specific parameters (LSQ-Focused + Aggressive FUs)
    cpu.numROBEntries = 64   # Keep ROB small
    cpu.LQEntries = 16       # DOUBLED Load Queue for memory ops
    cpu.SQEntries = 16       # DOUBLED Store Queue for memory ops

    # Pipeline widths (standard)
    cpu.fetchWidth = 4
    cpu.decodeWidth = 4
    cpu.renameWidth = 4
    cpu.issueWidth = 4
    cpu.wbWidth = 4
    cpu.commitWidth = 4

    # Physical registers
    cpu.numPhysIntRegs = 256
    cpu.numPhysFloatRegs = 256

    # Branch predictor - Tournament
    cpu.branchPred = TournamentBP()
    cpu.branchPred.BTBEntries = 4096
    cpu.branchPred.localPredictorSize = 2048
    cpu.branchPred.globalPredictorSize = 8192
    cpu.branchPred.choicePredictorSize = 8192

    # AGGRESSIVE Functional Unit Pool (MORE units than Extended)
    fu_pool = FUPool()
    fu_pool.FUList = [
        # More integer ALUs for parallelism
        IntALU(opList=[OpDesc(opClass='IntAlu')], count=6),  # 6 vs 4 in Extended

        # More multiply/divide units
        IntMultDiv(opList=[OpDesc(opClass='IntMult', opLat=3),
                          OpDesc(opClass='IntDiv', opLat=20)], count=3),  # 3 vs 2

        # More FP ALUs
        FP_ALU(opList=[OpDesc(opClass='FloatAdd', opLat=2),
                      OpDesc(opClass='FloatCmp', opLat=2),
                      OpDesc(opClass='FloatCvt', opLat=2)], count=3),  # 3 vs 2

        # More FP multiply/divide units
        FP_MultDiv(opList=[OpDesc(opClass='FloatMult', opLat=4),
                          OpDesc(opClass='FloatMultAcc', opLat=5),
                          OpDesc(opClass='FloatDiv', opLat=12),
                          OpDesc(opClass='FloatSqrt', opLat=24)], count=2),  # 2 vs 1

        # More memory ports for increased memory bandwidth
        ReadPort(opList=[OpDesc(opClass='MemRead')], count=3),  # 3 vs 2
        WritePort(opList=[OpDesc(opClass='MemWrite')], count=3),  # 3 vs 2
    ]
    cpu.fuPool = fu_pool

    return cpu

def create_system(binary_path, binary_args=""):
    """Create the complete system"""
    system = System()

    # Clock domain
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '2GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    # Memory setup
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('2GB')]

    # Create CPU
    system.cpu = create_cpu()

    # L1 Caches
    system.cpu.icache = L1_ICache(size='32kB', assoc=4)
    system.cpu.dcache = L1_DCache(size='32kB', assoc=4)

    # Connect L1 caches to CPU
    system.cpu.icache.cpu_side = system.cpu.icache_port
    system.cpu.dcache.cpu_side = system.cpu.dcache_port

    # L2 Cache and bus
    system.l2bus = L2XBar()
    system.l2cache = L2Cache(size='256kB', assoc=8)

    # Connect L1 to L2
    system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
    system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports
    system.l2cache.cpu_side = system.l2bus.mem_side_ports

    # Memory bus and controller
    system.membus = SystemXBar()
    system.l2cache.mem_side = system.membus.cpu_side_ports

    # Memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # System port
    system.system_port = system.membus.cpu_side_ports

    # Interrupt controller
    system.cpu.createInterruptController()

    # Create process
    process = Process()
    cmd = [binary_path]
    if binary_args:
        cmd.extend(binary_args.split())
    process.cmd = cmd
    system.cpu.workload = process
    system.cpu.createThreads()

    return system

def get_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Design C Configuration')

    parser.add_argument('binary', help='Path to binary to execute')
    parser.add_argument('--args', default='', help='Arguments for binary')
    parser.add_argument('--output', default='m5out/design_c',
                       help='Output directory')
    parser.add_argument('--max-inst', type=int, default=0,
                       help='Maximum instructions to simulate (0=unlimited)')

    return parser.parse_args()

def main():
    args = get_args()

    # Set output directory
    m5.options.outdir = args.output

    print("="*60)
    print("Design C: LSQ-Focused + Aggressive FUs (1000 credits)")
    print("="*60)
    print("Configuration:")
    print("  ROB Entries: 64")
    print("  Load Queue: 16 (DOUBLED)")
    print("  Store Queue: 16 (DOUBLED)")
    print("  FU Pool: AGGRESSIVE")
    print("    - Integer ALUs: 6 (vs 4 in Extended)")
    print("    - Int Mult/Div: 3 (vs 2 in Extended)")
    print("    - FP ALUs: 3 (vs 2 in Extended)")
    print("    - FP Mult/Div: 2 (vs 1 in Extended)")
    print("    - Memory Ports: 3R/3W (vs 2R/2W in Extended)")
    print("  Clock: 2GHz")
    print(f"  Binary: {args.binary}")
    print(f"  Output: {args.output}")
    print("="*60)
    print("Hypothesis: Larger LSQ + more FUs helps memory-heavy")
    print("           workloads (jpeg, susan_smoothing) by allowing")
    print("           more memory ops and computation in parallel")
    print("="*60)

    # Create system
    system = create_system(args.binary, args.args)

    # Create root and instantiate
    root = Root(full_system=False, system=system)
    m5.instantiate()

    print("Starting simulation...")
    exit_event = m5.simulate(args.max_inst)

    print(f"\nSimulation complete: {exit_event.getCause()}")
    print(f"Simulated ticks: {m5.curTick()}")

    # Basic stats
    stats = system.cpu.commitStats0
    if hasattr(stats, 'numInsts'):
        print(f"Instructions: {stats.numInsts}")
        if system.cpu.numCycles > 0:
            ipc = stats.numInsts / system.cpu.numCycles
            print(f"IPC: {ipc:.4f}")
            print(f"Cycles: {system.cpu.numCycles}")

if __name__ == "__main__":
    main()